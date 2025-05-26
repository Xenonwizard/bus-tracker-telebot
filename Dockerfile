FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code files including credentials.json
COPY . .

EXPOSE 8080

# Use main.py to launch, since it handles uvicorn and webhook logic
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

