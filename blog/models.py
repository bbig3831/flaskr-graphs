from py2neo import Graph, Node, Relationship
from passlib.hash import bcrypt
from datetime import datetime
import uuid

from py2neo.ogm import GraphObject, Property

graph = Graph()


class User(GraphObject):
    __primarykey__ = 'username'

    username = Property()
    password = Property()

    def __init__(self, username):
        self.username = username

    def find(self):
        user = self.match(graph, self.username).first()
        return user

    def register(self, password):
        if not self.find():
            user = Node('User', username=self.username, password=bcrypt.encrypt(password))
            graph.create(user)
            return True
        else:
            return False



