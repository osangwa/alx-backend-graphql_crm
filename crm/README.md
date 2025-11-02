# CRM Reports - Celery Setup Guide

This guide provides instructions for setting up and running the Celery-based CRM report generation system.

## Install Redis and Dependencies

### Install Redis

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Verify Redis is running:**
```bash
redis-cli ping
```

### Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

The `requirements.txt` should include:
```text
celery>=5.0
redis>=4.0
django-celery-beat>=2.0
requests
gql[requests]
```

## Run Migrations

Run Django migrations to set up the database:

```bash
python manage.py migrate
```

## Start Celery Worker

Open a terminal and start the Celery worker:

```bash
celery -A crm worker -l info
```

Keep this terminal running.

## Start Celery Beat

Open a new terminal and start the Celery Beat scheduler:

```bash
celery -A crm beat -l info
```

Keep this terminal running as well.

## Verify Logs

To monitor the CRM report logs:

```bash
tail -f /tmp/crm_report_log.txt
```

The log file will contain entries in the format:
```
YYYY-MM-DD HH:MM:SS - Report: X customers, Y orders, Z revenue
```

The report runs automatically every Monday at 6:00 AM UTC.