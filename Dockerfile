FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Keep Alpine packages current and install patched Python tooling.
RUN apk upgrade --no-cache

COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip setuptools urllib3 msgpack \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && python -m pip install --no-cache-dir --force-reinstall 'setuptools>=78.1.1' \
    && python -c "import setuptools; assert tuple(map(int, setuptools.__version__.split('.')[:2])) >= (78, 1)"

COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./alembic.ini
COPY entrypoint.sh ./entrypoint.sh

RUN adduser -D -u 10001 appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /app /data

USER appuser

EXPOSE 8000

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
