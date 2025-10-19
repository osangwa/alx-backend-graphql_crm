import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"

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
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    def resolve_hello(self, info):
        return "Hello, GraphQL!"

    def resolve_all_customers(self, info):
        return Customer.objects.all()

    def resolve_all_products(self, info):
        return Product.objects.all()

    def resolve_all_orders(self, info):
        return Order.objects.all()
