# TrackARuntime — teaching Agent runtime (offline-first)
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default: run eval gate (CI-equivalent smoke)
CMD ["python", "cli.py", "eval", "--baseline", "0.45"]
