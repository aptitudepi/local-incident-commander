FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/ services/
COPY src/ src/
COPY config.yaml .
COPY inbox/ inbox/
COPY reports/ reports/
COPY runbooks/ runbooks/
EXPOSE 5000 5001 5002 5003 5004 5005 5514 8080 8501
CMD ["python", "-m", "src.cli"]
