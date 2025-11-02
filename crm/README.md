# Celery Setup for CRM Reports

## Setup Steps

### 1. Install Redis and Dependencies

Install Redis:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

Install Python dependencies:
```bash
pip install celery redis django-celery-beat requests gql[requests]
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Start Celery Worker
```bash
celery -A crm worker -l info
```

### 4. Start Celery Beat
```bash
celery -A crm beat -l info
```

### 5. Verify Logs
```bash
tail -f /tmp/crm_report_log.txt
```

The CRM report task will run every Monday at 6:00 AM and log reports to `/tmp/crm_report_log.txt`.