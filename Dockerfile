FROM python:3.12-slim

# Cài các gói cần thiết
RUN apt-get update && apt-get install -y wget curl unzip && rm -rf /var/lib/apt/lists/*

# Cài dependencies Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cài Chromium cho Playwright
RUN playwright install --with-deps chromium

# Copy code vào container
COPY . /app
WORKDIR /app

CMD ["python", "main.py"]
