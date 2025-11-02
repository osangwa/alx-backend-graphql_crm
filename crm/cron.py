from datetime import datetime
import requests
import json

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    
    # Basic heartbeat log
    log_message = f"{timestamp} CRM is alive\n"
    
    # Optional: Check GraphQL endpoint
    try:
        url = "http://localhost:8000/graphql"
        query = "{ hello }"
        payload = {"query": query}
        
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            log_message += f"{timestamp} GraphQL endpoint is responsive\n"
        else:
            log_message += f"{timestamp} GraphQL endpoint returned status: {response.status_code}\n"
            
    except Exception as e:
        log_message += f"{timestamp} GraphQL endpoint check failed: {str(e)}\n"
    
    # Write to log file
    with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
        f.write(log_message)


def update_low_stock():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    
    # GraphQL mutation to update low stock products
    mutation = """
    mutation {
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
    """
    
    payload = {
        "query": mutation
    }
    
    try:
        url = "http://localhost:8000/graphql"
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        if "errors" in data:
            log_message = f"{timestamp}: GraphQL errors: {data['errors']}\n"
        else:
            result = data.get("data", {}).get("updateLowStockProducts", {})
            success = result.get("success", False)
            message = result.get("message", "")
            updated_products = result.get("updatedProducts", [])
            
            log_message = f"{timestamp}: {message}\n"
            
            if success and updated_products:
                for product in updated_products:
                    log_message += f"  - {product['name']}: New stock level {product['stock']}\n"
        
        # Write to log file
        with open('/tmp/low_stock_updates_log.txt', 'a') as f:
            f.write(log_message)
            
    except Exception as e:
        error_message = f"{timestamp}: Error updating low stock products: {str(e)}\n"
        with open('/tmp/low_stock_updates_log.txt', 'a') as f:
            f.write(error_message)