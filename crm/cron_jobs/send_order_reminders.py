#!/usr/bin/env python3

import requests
from datetime import datetime, timedelta
import json

def send_order_reminders():
    # GraphQL endpoint
    url = "http://localhost:8000/graphql"
    
    # Calculate date 7 days ago
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    # GraphQL query to get recent orders
    query = """
    query GetRecentOrders($since: String!) {
        recentOrders(since: $since) {
            id
            orderDate
            customer {
                email
            }
        }
    }
    """
    
    variables = {
        "since": one_week_ago
    }
    
    payload = {
        "query": query,
        "variables": variables
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        if "errors" in data:
            log_message = f"{datetime.now()}: GraphQL errors: {data['errors']}\n"
        else:
            orders = data.get("data", {}).get("recentOrders", [])
            
            log_message = f"{datetime.now()}: Processing {len(orders)} order reminders\n"
            
            for order in orders:
                order_id = order.get('id', 'N/A')
                customer_email = order.get('customer', {}).get('email', 'N/A')
                log_message += f"  - Order {order_id}: Customer {customer_email}\n"
            
            log_message += "Order reminders processed!\n"
        
        # Write to log file
        with open('/tmp/order_reminders_log.txt', 'a') as f:
            f.write(log_message)
        
        print("Order reminders processed!")
        
    except requests.exceptions.RequestException as e:
        error_message = f"{datetime.now()}: Error connecting to GraphQL endpoint: {str(e)}\n"
        with open('/tmp/order_reminders_log.txt', 'a') as f:
            f.write(error_message)
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    send_order_reminders()