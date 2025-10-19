import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order

def seed_database():
    # Clear existing data
    Order.objects.all().delete()
    Customer.objects.all().delete()
    Product.objects.all().delete()
    
    # Create customers
    customers = [
        Customer(name="Alice Johnson", email="alice@example.com", phone="+1234567890"),
        Customer(name="Bob Smith", email="bob@example.com", phone="123-456-7890"),
        Customer(name="Carol Davis", email="carol@example.com", phone="+44555123456"),
    ]
    for customer in customers:
        customer.save()
    
    # Create products
    products = [
        Product(name="Laptop", price=999.99, stock=10),
        Product(name="Mouse", price=29.99, stock=50),
        Product(name="Keyboard", price=79.99, stock=25),
        Product(name="Monitor", price=299.99, stock=15),
    ]
    for product in products:
        product.save()
    
    # Create orders
    customer1 = Customer.objects.get(email="alice@example.com")
    customer2 = Customer.objects.get(email="bob@example.com")
    
    product1 = Product.objects.get(name="Laptop")
    product2 = Product.objects.get(name="Mouse")
    product3 = Product.objects.get(name="Keyboard")
    
    # Order 1
    order1 = Order(customer=customer1, total_amount=1029.98)
    order1.save()
    order1.products.set([product1, product2])
    
    # Order 2
    order2 = Order(customer=customer2, total_amount=79.99)
    order2.save()
    order2.products.set([product3])
    
    print("Database seeded successfully!")
    print(f"Created {Customer.objects.count()} customers")
    print(f"Created {Product.objects.count()} products")
    print(f"Created {Order.objects.count()} orders")

if __name__ == "__main__":
    seed_database()