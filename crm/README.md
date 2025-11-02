# Celery Setup for CRM Reports

## Setup Steps

### 1. Install Redis

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis

macOS:

bash
brew install redis
brew services start redis
Verify Redis:

bash
redis-cli ping
2. Install Dependencies
Add to requirements.txt:

text
celery>=5.0
redis>=4.0
django-celery-beat>=2.0
requests
gql[requests]
Install dependencies:

bash
pip install -r requirements.txt
3. Create Celery Configuration
File: crm/celery.py

python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

app = Celery('crm')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
File: crm/__init__.py

python
from .celery import app as celery_app

__all__ = ('celery_app',)
4. Create Celery Task
File: crm/tasks.py

python
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
5. Update Django Settings
File: crm/settings.py
Add to INSTALLED_APPS:

python
INSTALLED_APPS = [
    # ... other apps
    'django_celery_beat',
    'crm',
]
Add Celery configuration:

python
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
6. Update GraphQL Schema
File: crm/schema.py
Add to Query class:

python
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
7. Run Migrations
bash
python manage.py makemigrations
python manage.py migrate
8. Start Celery Worker
bash
celery -A crm worker -l info
9. Start Celery Beat
bash
celery -A crm beat -l info
10. Verify Logs
bash
tail -f /tmp/crm_report_log.txt
The CRM report will run every Monday at 6:00 AM and log to /tmp/crm_report_log.txt.


