import json
import os
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional


INBOX_DIR = "inbox"
REPORTS_DIR = "reports"
EVENTS_LOG = os.path.join(REPORTS_DIR, "events", "events.jsonl")


def parse_event_file(path: str) -> Optional[Dict]:
    ext = Path(path).suffix.lower()
    try:
        if ext == ".json":
            with open(path) as f:
                data = json.load(f)
        elif ext == ".txt":
            with open(path) as f:
                data = _parse_text_event(f.read())
        else:
            return None
        if "service" not in data:
            data["service"] = "unknown"
        if "timestamp" not in data:
            data["timestamp"] = datetime.now(timezone.utc).isoformat()
        if "event_type" not in data:
            data["event_type"] = "log"
        data["_source"] = path
        return data
    except (json.JSONDecodeError, OSError):
        return None


def _parse_text_event(text: str) -> Dict:
    result = {"event_type": "log", "payload": {}}
    for line in text.strip().splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip().lower().replace(" ", "_")
            val = val.strip()
            if key == "deploy":
                result["event_type"] = "deploy"
                result["payload"]["deploy_info"] = val
            elif key in ("service", "event_type", "severity", "timestamp"):
                result[key] = val
            else:
                try:
                    result["payload"][key] = float(val) if "." in val else int(val)
                except ValueError:
                    result["payload"][key] = val
    return result


def scan_directory(input_dir: str = INBOX_DIR) -> List[Dict]:
    events = []
    path = Path(input_dir)
    if not path.exists():
        return events
    for fpath in sorted(path.iterdir()):
        if fpath.is_file() and not fpath.name.startswith("."):
            event = parse_event_file(str(fpath))
            if event:
                events.append(event)
    return events


def write_event_log(event: Dict):
    os.makedirs(os.path.dirname(EVENTS_LOG), exist_ok=True)
    with open(EVENTS_LOG, "a") as f:
        f.write(json.dumps(event, default=str) + "\n")


class EventWatcher:
    def __init__(self, inbox_dir: str = INBOX_DIR, poll_interval: float = 1.0):
        self.inbox_dir = inbox_dir
        self.poll_interval = poll_interval
        self._known_files = set()

    def watch(self):
        os.makedirs(self.inbox_dir, exist_ok=True)
        while True:
            current = set()
            path = Path(self.inbox_dir)
            if path.exists():
                for f in path.iterdir():
                    if f.is_file() and not f.name.startswith("."):
                        current.add(f.name)
                        if f.name not in self._known_files:
                            event = parse_event_file(str(f))
                            if event:
                                write_event_log(event)
                                yield event
            self._known_files = current
            time.sleep(self.poll_interval)
