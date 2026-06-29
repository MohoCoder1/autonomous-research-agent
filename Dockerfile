FROM python:3.11-slim

WORKDIR /app

# make sure the browser (chromium) installs correctly and doesn't crash
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# install the browser (chromium) and its dependencies for playwright
RUN playwright install chromium
RUN playwright install-deps chromium

# copy the whole project
COPY . .

# main  running command when the container starts
CMD ["python", "main.py"]