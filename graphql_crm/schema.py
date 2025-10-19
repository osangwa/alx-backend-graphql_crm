import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from django.core.exceptions import ValidationError
import re
from .models import Customer, Product, Order

# Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"

# Inputs
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

# Response Types
class CreateCustomerResponse(graphene.ObjectType):
    customer = graphene.Field(CustomerType)
    message = graphene.String()

class BulkCreateCustomersResponse(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

class CreateProductResponse(graphene.ObjectType):
    product = graphene.Field(ProductType)

class CreateOrderResponse(graphene.ObjectType):
    order = graphene.Field(OrderType)

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    Output = CreateCustomerResponse

    @staticmethod
    def mutate(root, info, input):
        # Validate email format
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', input.email):
            raise ValidationError("Invalid email format")
        
        # Validate phone format if provided
        if input.phone and not re.match(r'^(\+\d{1,3}[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})$', input.phone):
            raise ValidationError("Invalid phone format. Use formats like +1234567890 or 123-456-7890")
        
        # Check for duplicate email
        if Customer.objects.filter(email=input.email).exists():
            raise ValidationError("Email already exists")
        
        customer = Customer(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        customer.full_clean()
        customer.save()
        
        return CreateCustomerResponse(
            customer=customer,
            message="Customer created successfully"
        )

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    Output = BulkCreateCustomersResponse

    @staticmethod
    @transaction.atomic
    def mutate(root, info, input):
        customers = []
        errors = []
        
        for idx, customer_data in enumerate(input):
            try:
                # Validate email format
                if not re.match(r'^[^@]+@[^@]+\.[^@]+$', customer_data.email):
                    errors.append(f"Row {idx + 1}: Invalid email format")
                    continue
                
                # Validate phone format if provided
                if customer_data.phone and not re.match(r'^(\+\d{1,3}[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})$', customer_data.phone):
                    errors.append(f"Row {idx + 1}: Invalid phone format")
                    continue
                
                # Check for duplicate email
                if Customer.objects.filter(email=customer_data.email).exists():
                    errors.append(f"Row {idx + 1}: Email already exists")
                    continue
                
                customer = Customer(
                    name=customer_data.name,
                    email=customer_data.email,
                    phone=customer_data.phone
                )
                customer.full_clean()
                customer.save()
                customers.append(customer)
                
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")
        
        return BulkCreateCustomersResponse(
            customers=customers,
            errors=errors
        )

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    Output = CreateProductResponse

    @staticmethod
    def mutate(root, info, input):
        # Validate price is positive
        if input.price <= 0:
            raise ValidationError("Price must be positive")
        
        # Validate stock is non-negative
        stock = input.stock or 0
        if stock < 0:
            raise ValidationError("Stock cannot be negative")
        
        product = Product(
            name=input.name,
            price=input.price,
            stock=stock
        )
        product.full_clean()
        product.save()
        
        return CreateProductResponse(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    Output = CreateOrderResponse

    @staticmethod
    def mutate(root, info, input):
        # Validate customer exists
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Customer does not exist")
        
        # Validate products exist and get them
        products = []
        for product_id in input.product_ids:
            try:
                product = Product.objects.get(id=product_id)
                products.append(product)
            except Product.DoesNotExist:
                raise ValidationError(f"Product with ID {product_id} does not exist")
        
        # Validate at least one product
        if not products:
            raise ValidationError("At least one product is required")
        
        # Calculate total amount
        total_amount = sum(product.price for product in products)
        
        # Create order
        order = Order(
            customer=customer,
            total_amount=total_amount
        )
        if input.order_date:
            order.order_date = input.order_date
        
        order.save()
        order.products.set(products)
        
        return CreateOrderResponse(order=order)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

# Queries
class Query(graphene.ObjectType):
    hello = graphene.String()
    
    def resolve_hello(root, info):
        return "Hello, GraphQL!"