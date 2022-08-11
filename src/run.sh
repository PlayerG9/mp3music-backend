cd "$(dirname "$0")/mp3backend/" || exit 1

../../.venv/bin/uvicorn main:app --host=0.0.0.0 --port="${PORT:-5000}" "$@"
