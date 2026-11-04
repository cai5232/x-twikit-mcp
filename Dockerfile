FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd --uid 10001 --create-home lumi && mkdir -p /data && chown lumi:lumi /data
COPY server.py http_server.py twikit_compat.py ./
ENV PYTHONUNBUFFERED=1 TWITTER_DATA_DIR=/data TWITTER_COOKIES_PATH=/data/cookies.json
USER lumi
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)"
CMD ["python", "http_server.py"]
