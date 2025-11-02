from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import TransportQueryError
import sys

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    
    log_entries = [f"{timestamp} CRM is alive"]
    
    try:
        # Setup GraphQL client with timeout
        url = "http://localhost:8000/graphql"
        transport = RequestsHTTPTransport(
            url=url,
            timeout=10
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Query the hello field using gql
        query = gql("""
            query HealthCheck {
                hello
            }
        """)
        
        result = client.execute(query)
        hello_message = result.get('hello', 'No hello message')
        log_entries.append(f"{timestamp} GraphQL endpoint is responsive - {hello_message}")
        
    except TransportQueryError as e:
        log_entries.append(f"{timestamp} GraphQL query error: {e.errors}")
    except Exception as e:
        log_entries.append(f"{timestamp} GraphQL endpoint check failed: {str(e)}")
    
    # Write to log file
    with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
        f.write("\n".join(log_entries) + "\n")

def update_low_stock():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    
    try:
        # Setup GraphQL client
        url = "http://localhost:8000/graphql"
        transport = RequestsHTTPTransport(url=url)
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Define the mutation using gql
        mutation = gql("""
            mutation UpdateLowStock {
                updateLowStockProducts {
                    success
                    message
                    updatedProducts {
                        id
                        name
                        stock
                    }
                }
            }
        """)
        
        # Execute the mutation
        result = client.execute(mutation)
        
        # Process the result
        mutation_data = result.get("updateLowStockProducts", {})
        success = mutation_data.get("success", False)
        message = mutation_data.get("message", "No message returned")
        updated_products = mutation_data.get("updatedProducts", [])
        
        # Build log message
        log_entries = [f"{timestamp}: {message}"]
        
        if success:
            if updated_products:
                log_entries.append("Updated products:")
                for product in updated_products:
                    log_entries.append(f"  - {product['name']}: Stock level → {product['stock']}")
            else:
                log_entries.append("No products required restocking")
        else:
            log_entries.append("Mutation was not successful")
        
        # Write to log file
        with open('/tmp/low_stock_updates_log.txt', 'a') as f:
            f.write("\n".join(log_entries) + "\n")
            
    except TransportQueryError as e:
        error_message = f"{timestamp}: GraphQL mutation error: {e.errors}\n"
        with open('/tmp/low_stock_updates_log.txt', 'a') as f:
            f.write(error_message)
    except Exception as e:
        error_message = f"{timestamp}: Error in update_low_stock: {str(e)}\n"
        with open('/tmp/low_stock_updates_log.txt', 'a') as f:
            f.write(error_message)