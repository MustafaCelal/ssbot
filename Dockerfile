FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Chromium'un yerini Selenium'a bildirmek için
    CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app

# ARM uyumlu Chromium ve Sürücüsünü kuruyoruz
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    tini \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p logs screenshots && \
    useradd -m botuser && \
    chown -R botuser:botuser /app

USER botuser
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "main.py", "--help"]