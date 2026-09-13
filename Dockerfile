FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN addgroup --system app && adduser --system --ingroup app app
COPY pyproject.toml ./
RUN pip install --no-cache-dir .
COPY auth_service auth_service
COPY vehicle_service vehicle_service
COPY migrations migrations
COPY alembic.ini ./
USER app
ARG SERVICE=vehicle_service
ENV SERVICE=${SERVICE}
CMD ["sh", "-c", "alembic -x service=${SERVICE} upgrade head && uvicorn ${SERVICE}.main:app --host 0.0.0.0 --port 8000"]

