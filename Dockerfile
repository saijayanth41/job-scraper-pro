FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY README.md .

ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "src.jobscraper.cli", "--schedule", "60", "--sites", "indeed"]
