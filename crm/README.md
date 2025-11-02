# CRM Reports Setup

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

Verify Redis is running:
```bash
redis-cli ping
```

### Install Dependencies

Install required Python packages:
```bash
pip install -r requirements.txt
```

## Run Migrations

Run Django migrations:
```bash
python manage.py migrate
```

## Start Celery Worker

Start the Celery worker:
```bash
celery -A crm worker -l info
```

## Start Celery Beat

Start the Celery Beat scheduler:
```bash
celery -A crm beat -l info
```

## Verify Logs

Monitor the CRM report logs:
```bash
tail -f /tmp/crm_report_log.txt
```