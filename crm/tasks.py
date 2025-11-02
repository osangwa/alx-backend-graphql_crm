from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime
import logging

@shared_task
def generate_crm_report():
    """
    Celery task to generate weekly CRM report using GraphQL queries
    """
    try:
        # Setup GraphQL client
        url = "http://localhost:8000/graphql"
        transport = RequestsHTTPTransport(url=url)
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # GraphQL query to fetch CRM statistics
        query = gql("""
            query GetCRMStats {
                totalCustomers
                totalOrders
                totalRevenue
            }
        """)
        
        # Execute the query
        result = client.execute(query)
        
        # Extract data from result
        total_customers = result.get('totalCustomers', 0)
        total_orders = result.get('totalOrders', 0)
        total_revenue = result.get('totalRevenue', 0.0)
        
        # Format the report
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_message = (
            f"{timestamp} - Report: {total_customers} customers, "
            f"{total_orders} orders, {total_revenue:.2f} revenue\n"
        )
        
        # Log the report to file
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