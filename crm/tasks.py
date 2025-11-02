from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime
import requests  # Required import

@shared_task(bind=True)
def generate_crm_report(self):
    """
    Celery task to generate weekly CRM report using GraphQL queries
    """
    try:
        # First, check if the GraphQL endpoint is reachable using requests
        url = "http://localhost:8000/graphql"
        
        # Simple health check using requests
        health_check = requests.get("http://localhost:8000/", timeout=5)
        if health_check.status_code != 200:
            raise Exception("Django server is not responding")
        
        # Setup GraphQL client with requests transport
        transport = RequestsHTTPTransport(
            url=url,
            headers={
                'Content-Type': 'application/json',
            },
            use_json=True
        )
        
        client = Client(
            transport=transport,
            fetch_schema_from_transport=True
        )
        
        # GraphQL query to fetch CRM statistics
        query = gql("""
            query GenerateCRMReport {
                totalCustomers
                totalOrders
                totalRevenue
            }
        """)
        
        # Execute the query
        result = client.execute(query)
        
        # Extract and validate data
        total_customers = result.get('totalCustomers', 0)
        total_orders = result.get('totalOrders', 0)
        total_revenue = float(result.get('totalRevenue', 0.0))
        
        # Format the report
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_message = (
            f"{timestamp} - Weekly CRM Report: {total_customers} customers, "
            f"{total_orders} orders, ${total_revenue:.2f} revenue\n"
        )
        
        # Log the report to file
        with open('/tmp/crm_report_log.txt', 'a') as log_file:
            log_file.write(report_message)
        
        # Also print to console for Celery logs
        print(f"CRM Report generated at {timestamp}")
        
        return {
            'status': 'success',
            'timestamp': timestamp,
            'total_customers': total_customers,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'message': 'CRM report generated successfully'
        }
        
    except requests.exceptions.RequestException as e:
        # Handle requests-related errors
        error_message = f"{datetime.now()} - Network error generating CRM report: {str(e)}\n"
        with open('/tmp/crm_report_log.txt', 'a') as log_file:
            log_file.write(error_message)
        
        # Retry the task after 2 minutes
        raise self.retry(countdown=120, exc=e)
        
    except Exception as e:
        # Handle other errors
        error_message = f"{datetime.now()} - Error generating CRM report: {str(e)}\n"
        with open('/tmp/crm_report_log.txt', 'a') as log_file:
            log_file.write(error_message)
        
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }