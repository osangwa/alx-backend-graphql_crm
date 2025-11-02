#!/bin/bash

# Change to the Django project directory
cd /Users/octave/alx-projects/alx-backend-graphql_crm

# Activate virtual environment if you have one
# source venv/bin/activate

# Run the Django shell command to delete inactive customers
python manage.py shell << EOF
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order
from django.db.models import Max

# Find customers with no orders in the last year
one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = []

for customer in Customer.objects.all():
    last_order = Order.objects.filter(customer=customer).aggregate(Max('order_date'))
    if not last_order['order_date__max'] or last_order['order_date__max'] < one_year_ago:
        inactive_customers.append(customer)

# Delete inactive customers
deleted_count = len(inactive_customers)
for customer in inactive_customers:
    customer.delete()

# Log the result
with open('/tmp/customer_cleanup_log.txt', 'a') as f:
    f.write(f"$(date): Deleted {deleted_count} inactive customers\n")
EOF