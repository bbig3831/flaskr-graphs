from .views import app
from .models import graph

graph.evaluate('create constraint on (n:User) assert n.username is unique')
graph.evaluate('create constraint on (n:Post) assert n.id is unique')
graph.evaluate('create constraint on (n:Tag) assert n.name is unique')