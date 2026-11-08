"""Entry point.

Development : APP_ENV=development flask --app run run --debug
Staging     : APP_ENV=staging     gunicorn -w 2 -b 0.0.0.0:8000 "run:app"
Production  : APP_ENV=production SECRET_KEY=... gunicorn -w 4 -b 0.0.0.0:8000 "run:app"
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
