# Add these imports at the top
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay
import django_filters
from .filters import CustomerFilter, ProductFilter, OrderFilter

# Update Types to use Relay
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"
        interfaces = (relay.Node,)
        filterset_class = CustomerFilter

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"
        interfaces = (relay.Node,)
        filterset_class = ProductFilter

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"
        interfaces = (relay.Node,)
        filterset_class = OrderFilter

# Update Query class
class Query(graphene.ObjectType):
    hello = graphene.String()
    
    # Filtered queries
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType)
    all_orders = DjangoFilterConnectionField(OrderType)
    
    def resolve_hello(root, info):
        return "Hello, GraphQL!"