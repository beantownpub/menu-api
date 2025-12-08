FROM python:3.14.1-slim

ENV TINI_VERSION=v0.18.0
# Optimize Python for memory usage
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends libpq5 && \
    pip install --no-cache-dir -U pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /opt/app/

ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini

RUN chmod +x /tini && \
    useradd --create-home appuser

# STOPSIGNAL SIGINT

USER appuser
ENTRYPOINT ["/tini", "-s", "--"]

WORKDIR /opt/app

EXPOSE 5004

# Optimized gunicorn configuration for low memory environments
# --preload: Load application code before forking workers (saves memory)
# --worker-class sync: Use sync workers (lower memory than async)
# --timeout: Worker timeout
# --graceful-timeout: Graceful shutdown timeout
# --max-requests: Restart workers after N requests to prevent memory leaks
# --max-requests-jitter: Add randomness to max-requests
CMD ["gunicorn", "--preload", "--workers", "1", "--worker-class", "sync", "--timeout", "30", "--graceful-timeout", "30", "--max-requests", "1000", "--max-requests-jitter", "100", "--bind", ":5004", "server:APP"]
