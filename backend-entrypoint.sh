#!/bin/sh
set -e

# Wait for database if env provided
if [ -n "$DB_HOST" ]; then
  echo "Waiting for DB $DB_HOST:$DB_PORT..."
  python - <<'PYCODE'
import socket, os, time, sys
host = os.getenv("DB_HOST", "db")
port = int(os.getenv("DB_PORT", "5432"))
for _ in range(60):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex((host, port)) == 0:
            sys.exit(0)
    time.sleep(1)
print("DB not available", file=sys.stderr)
sys.exit(1)
PYCODE
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000

