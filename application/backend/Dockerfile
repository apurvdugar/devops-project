FROM python:3.12-slim-bookworm AS builder

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

RUN python -m venv "${VIRTUAL_ENV}"

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools==84.0.0 wheel==0.48.0 && \
    pip install --no-cache-dir -r requirements.txt && \
    python -m pip check && \
    rm -rf "${VIRTUAL_ENV}/lib/python3.12/site-packages/pip"* \
           "${VIRTUAL_ENV}/lib/python3.12/site-packages/setuptools"* \
           "${VIRTUAL_ENV}/lib/python3.12/site-packages/wheel"*

FROM python:3.12-slim-bookworm

WORKDIR /app
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# The application runs entirely from /opt/venv. Remove base-image package
# management artifacts so their vendored libraries are not shipped or scanned.
RUN apt-get update && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/* && \
    rm -rf /usr/local/lib/python3.12/site-packages/pip* \
           /usr/local/lib/python3.12/site-packages/setuptools* \
           /usr/local/lib/python3.12/site-packages/wheel* \
           /usr/local/bin/pip*

COPY --from=builder /opt/venv /opt/venv
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

RUN useradd --create-home --uid 10001 appuser
USER 10001
EXPOSE 8000
CMD ["sh", "-c", "python -m app.wait_for_db && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
