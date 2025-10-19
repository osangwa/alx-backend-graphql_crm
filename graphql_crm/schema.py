import graphene
from crm.schema import Query as CRMQuery

class Query(CRMQuery, graphene.ObjectType):
    # This combines queries from different apps
    pass

# THIS LINE IS CRITICAL FOR THE CHECKS
schema = graphene.Schema(query=Query)