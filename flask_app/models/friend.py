from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import app
from flask import flash

class Friend:
    def __init__(self, data:dict):
        self.id = data['id']
        self.user_id = data['user_id']
        self.friend_id = data['friend_id']
        self.created_at = data['created_at']

    @classmethod
    def get_friendship_created(cls):
        query = '''
        SELECT * FROM friendships
        GROUP BY friendships.created_at
        ORDER BY friendships.created_at DESC;
        '''

        result = connectToMySQL('friendships').query_db(query)

        return cls(result[0])

    @classmethod
    def add_friendship(cls, data:dict):
        query = '''
        INSERT INTO friendships (user_id, friend_id)
        SELECT %(user_id)s, %(friend_id)s
        WHERE NOT EXISTS (SELECT user_id, friend_id FROM friendships WHERE user_id = %(user_id)s AND friend_id = %(friend_id)s);
        '''

        return connectToMySQL('friendships').query_db(query, data)