# CRM Reports - Celery Setup Guide

This guide provides step-by-step instructions for setting up Celery with Celery Beat to generate automated weekly CRM reports.

## Prerequisites

- Python 3.8+
- Django project set up
- Redis server

## Setup Steps

### 1. Install Redis

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
# Expected output: PONG
```

### 2. Install Dependencies

Add the following to your `requirements.txt`:

```text
celery>=5.0
redis>=4.0
django-celery-beat>=2.0
requests
gql[requests]
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### 3. Create Celery Configuration

**File: `crm/celery.py`**

```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

app = Celery('crm')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

**File: `crm/__init__.py`**

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### 4. Create Celery Task

**File: `crm/tasks.py`**

```python
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime
import requests

@shared_task
def generate_crm_report():
    try:
        url = "http://localhost:8000/graphql"
        transport = RequestsHTTPTransport(url=url)
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        query = gql("""
            query GetCRMStats {
                totalCustomers
                totalOrders
                totalRevenue
            }
        """)
        
        result = client.execute(query)
        
        total_customers = result.get('totalCustomers', 0)
        total_orders = result.get('totalOrders', 0)
        total_revenue = result.get('totalRevenue', 0.0)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_message = (
            f"{timestamp} - Report: {total_customers} customers, "
            f"{total_orders} orders, {total_revenue:.2f} revenue\n"
        )
        
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(report_message)
        
        return {
            'status': 'success',
            'total_customers': total_customers,
            'total_orders': total_orders,
            'total_revenue': total_revenue
        }
        
    except Exception as e:
        error_message = f"{datetime.now()} - Error generating CRM report: {str(e)}\n"
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(error_message)
        
        return {
            'status': 'error',
            'error': str(e)
        }
```

### 5. Update Django Settings

**File: `crm/settings.py`**

Add `django_celery_beat` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'django_celery_beat',
    'crm',
]
```

Add Celery configuration:

```python
# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
    },
}
```

### 6. Update GraphQL Schema

**File: `crm/schema.py`**

Add the following fields to your `Query` class:

```python
class Query(graphene.ObjectType):
    total_customers = graphene.Int()
    total_orders = graphene.Int()
    total_revenue = graphene.Float()
    
    def resolve_total_customers(self, info):
        from crm.models import Customer
        return Customer.objects.count()
    
    def resolve_total_orders(self, info):
        from crm.models import Order
        return Order.objects.count()
    
    def resolve_total_revenue(self, info):
        from crm.models import Order
        from django.db.models import Sum
        result = Order.objects.aggregate(total_revenue=Sum('total_amount'))
        return result['total_revenue'] or 0.0
```

### 7. Run Migrations

Run Django migrations to set up the database tables for django-celery-beat:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Start Celery Worker

Open a terminal and start the Celery worker:

```bash
celery -A crm worker -l info
```

Keep this terminal running.

### 9. Start Celery Beat

Open a new terminal and start the Celery Beat scheduler:

```bash
celery -A crm beat -l info
```

Keep this terminal running as well.

### 10. Verify Logs

To monitor the CRM report logs:

```bash
tail -f /tmp/crm_report_log.txt
```

## Report Schedule

The CRM report will run automatically **every Monday at 6:00 AM UTC** and log the results to `/tmp/crm_report_log.txt`.

## Manual Testing

To manually trigger the report generation for testing:

```bash
python manage.py shell
```

Then in the Python shell:

```python
from crm.tasks import generate_crm_report
generate_crm_report.delay()
```

## Expected Log Format

The log file will contain entries in this format:

```
YYYY-MM-DD HH:MM:SS - Report: X customers, Y orders, Z revenue
```

Example:
```
2025-11-02 06:00:00 - Report: 150 customers, 320 orders, 45000.00 revenue
```

## Troubleshooting

### Redis Connection Issues

If you encounter Redis connection errors:

```bash
# Check if Redis is running
redis-cli ping

# Restart Redis if needed (Ubuntu/Debian)
sudo systemctl restart redis

# Restart Redis if needed (macOS)
brew services restart redis
```

### Celery Worker Issues

- Ensure the Django development server is running on `http://localhost:8000`
- Verify the GraphQL endpoint is accessible at `/graphql`
- Check that the `Customer` and `Order` models exist and have data
- Review the Celery worker logs for any error messages

### Task Not Running

- Verify Celery Beat is running
- Check the schedule configuration in `settings.py`
- Ensure the timezone is set correctly
- Look for errors in the Celery Beat logs

## Production Deployment

For production environments, consider:

1. Using a process manager like Supervisor or systemd to keep Celery workers running
2. Setting up proper logging with log rotation
3. Using a more robust message broker setup
4. Implementing monitoring and alerting for task failures
5. Adjusting the `CELERY_TIMEZONE` to match your application's timezone

## Project Structure

```
crm/
├── __init__.py              # Celery app initialization
├── celery.py                # Celery configuration
├── settings.py              # Django settings with Celery config
├── tasks.py                 # Celery tasks (generate_crm_report)
├── schema.py                # GraphQL schema with report queries
├── models.py                # Customer and Order models
└── README.md                # This file
```