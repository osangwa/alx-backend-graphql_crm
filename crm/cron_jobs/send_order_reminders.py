#!/usr/bin/env python3

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import TransportQueryError
from datetime import datetime, timedelta
import sys

def send_order_reminders():
    # GraphQL endpoint configuration
    url = "http://localhost:8000/graphql"
    
    try:
        # Setup GraphQL client
        transport = RequestsHTTPTransport(
            url=url,
            use_json=True,
            headers={
                "Content-type": "application/json",
            }
        )
        
        client = Client(
            transport=transport,
            fetch_schema_from_transport=True,
        )
        
        # Calculate date 7 days ago
        one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Define GraphQL query
        query = gql("""
            query GetRecentOrders($since: String!) {
                recentOrders(since: $since) {
                    id
                    orderDate
                    customer {
                        email
                        name
                    }
                    status
                }
            }
        """)
        
        # Execute query with variables
        result = client.execute(query, variable_values={"since": one_week_ago})
        
        # Process results
        orders = result.get('recentOrders', [])
        
        # Create log entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entries = [f"{timestamp}: Found {len(orders)} orders from the last 7 days"]
        
        for order in orders:
            order_id = order.get('id', 'Unknown ID')
            customer_email = order.get('customer', {}).get('email', 'No email')
            order_date = order.get('orderDate', 'Unknown date')
            status = order.get('status', 'Unknown status')
            
            log_entries.append(
                f"  - Order #{order_id} ({status}): {customer_email} on {order_date}"
            )
        
        log_entries.append("Order reminders processed successfully!")
        
        # Write to log file
        full_log = "\n".join(log_entries) + "\n"
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(full_log)
        
        # Print success message to console
        print("Order reminders processed!")
        
    except TransportQueryError as e:
        # Handle GraphQL query errors
        error_msg = f"{datetime.now()}: GraphQL Query Error: {e.errors}\n"
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(error_msg)
        print(f"GraphQL Error: {e.errors}")
        
    except Exception as e:
        # Handle other errors
        error_msg = f"{datetime.now()}: Unexpected error: {str(e)}\n"
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(error_msg)
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    send_order_reminders()