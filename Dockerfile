FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Apply current Debian security updates and refresh vulnerable Python tooling.
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get purge -y python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip setuptools urllib3 msgpack \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && python -m pip install --no-cache-dir --force-reinstall 'setuptools>=78.1.1' \
    && python -c "import setuptools; assert tuple(map(int, setuptools.__version__.split('.')[:2])) >= (78, 1)" \
    && find /usr/local/lib/python3.13/site-packages /usr/lib/python3/dist-packages -maxdepth 1 -type d -name 'setuptools-70.3.0.dist-info' -prune -exec rm -rf {} +

COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./alembic.ini
COPY entrypoint.sh ./entrypoint.sh

RUN useradd --uid 10001 --create-home appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /app /data

USER appuser

EXPOSE 8000

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
