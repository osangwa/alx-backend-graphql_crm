import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from django.db import transaction

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")
        interfaces = (graphene.relay.Node,)

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"
        interfaces = (graphene.relay.Node,)

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"
        interfaces = (graphene.relay.Node,)

class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=True)

    customer = graphene.Field(CustomerType)

    def mutate(self, info, name, email, phone):
        customer = Customer(
            name=name,
            email=email,
            phone=phone
        )
        customer.save()
        return CreateCustomer(customer=customer)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()

class Query(graphene.ObjectType):
    hello = graphene.String()
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType)
    all_orders = DjangoFilterConnectionField(OrderType)

    def resolve_hello(self, info):
        return "Hello, GraphQL!"

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass

    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(ProductType)

    @transaction.atomic
    def mutate(self, info):
        try:
            # Find products with stock less than 10
            low_stock_products = Product.objects.filter(stock__lt=10)
            updated_count = low_stock_products.count()
            
            # Update stock by adding 10 to each low stock product
            for product in low_stock_products:
                product.stock += 10
                product.save()
            
            return UpdateLowStockProducts(
                success=True,
                message=f"Updated {updated_count} low-stock products",
                updated_products=low_stock_products
            )
            
        except Exception as e:
            return UpdateLowStockProducts(
                success=False,
                message=f"Error updating low-stock products: {str(e)}",
                updated_products=[]
            )

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()

# Add to your existing schema
schema = graphene.Schema(
    query=Query,  # Your existing Query class
    mutation=Mutation
)