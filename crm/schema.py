import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order

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
