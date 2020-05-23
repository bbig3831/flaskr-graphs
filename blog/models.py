from py2neo import Graph, Node, NodeMatcher, Relationship
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
        matcher = NodeMatcher(graph)
        user = matcher.match(username=self.username).first()
        return user

    def register(self, password):
        if not self.find():
            user = Node('User', username=self.username, password=bcrypt.encrypt(password))
            graph.create(user)
            return True
        else:
            return False

    def verify_password(self, password):
        user = self.find()

        if not user:
            return False

        return bcrypt.verify(password, user['password'])

    def add_post(self, title, tags, text):
        user = self.find()

        post = Node(
            "Post",
            id=str(uuid.uuid4()),
            title=title,
            text=text,
            timestamp=datetime.now().strftime('%s'),
            date=datetime.now().strftime('%F')
        )

        rel = Relationship(user, "PUBLISHED", post)
        graph.create(rel)

        tags = [x.strip() for x in tags.lower().split(',')]
        tags = set(tags)

        for tag in tags:
            tag_node = Node('Tag', name=tag)
            rel = Relationship(tag_node, 'TAGGED', post)
            graph.merge(rel, 'Tag', 'name')

    def like_post(self, post_id):
        user = self.find()
        matcher = NodeMatcher(graph)
        post = matcher.match('Post', id=post_id).first()
        graph.create(Relationship(user, 'LIKES', post))

    def recent_posts(self, n):
        query = """
        MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
        WHERE user.username = {username}
        RETURN post, COLLECT(tag.name) AS tags
        ORDER BY post.timestamp DESC LIMIT {n}
        """
        return graph.run(query, username=self.username, n=n).data()

    def similar_users(self, n):
        query = """
        MATCH (user1:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
            (user2:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag)
        WHERE user1.username = {username} AND user1 <> user2
        WITH user2, COLLECT(DISTINCT tag.name) AS tags, COUNT(DISTINCT tag.name) AS tag_count
        ORDER BY tag_count DESC LIMIT {n}
        RETURN user2.username AS similar_user, tags
        """
        return graph.run(query, username=self.username, n=n).data()

    def commonality_of_user(self, user):
        query1 = """
        MATCH (user1:User)-[:PUBLISHED]->(post:Post)<-[:LIKES]-(user2:User)
        WHERE user1.username = {username1} and user2.username = {username2}
        RETURN COUNT(post) AS likes
        """

        likes = graph.run(query1, username1=self.username, username2=user.username).evaluate('likes')
        likes = 0 if not likes else likes

        query2 = """
        MATCH (user1:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
            (user2:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag)
        WHERE user1.username = {username1} and user2.username = {username2}
        RETURN COLLECT(DISTINCT tag.name) as tags
        """

        tags = graph.run(query2, username1=self.username, username2=user.username).data()[0]['tags']
        return {'likes': likes, 'tags': tags}


def todays_recent_posts(n):
    today = datetime.now().strftime('%F')
    query = """
    MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
    WHERE post.date = {today}
    RETURN user.username as username, post, COLLECT(tag.name) as tags
    ORDER BY post.timestamp DESC LIMIT {n}
    """
    return graph.run(query, parameters={'today': today, 'n': n}).data()
