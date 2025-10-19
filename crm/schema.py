import graphene

class Query(graphene.ObjectType):
    # This class must inherit from graphene.ObjectType
    hello = graphene.String()

    def resolve_hello(self, info):
        return "Hello, GraphQL!"