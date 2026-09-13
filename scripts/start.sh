#!/bin/sh
set -u

attempt=1
max_attempts=30

while ! alembic -x "service=${SERVICE}" upgrade head; do
  if [ "$attempt" -ge "$max_attempts" ]; then
    echo "Database migration failed after ${max_attempts} attempts."
    exit 1
  fi

  echo "Database is not ready; migration attempt ${attempt}/${max_attempts} failed. Retrying in 2 seconds."
  attempt=$((attempt + 1))
  sleep 2
done

exec uvicorn "${SERVICE}.main:app" --host 0.0.0.0 --port 8000
