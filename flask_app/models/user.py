from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import app
from flask import flash
from flask_bcrypt import Bcrypt
import re

BCRYPT = Bcrypt(app)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$')

class User:
    def __init__ (self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.friends = []

    # STATIC METHODS

    @staticmethod
    def parse_user_registration(data:dict) -> dict:
        parsed_data = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'email': data.get('email'),
            'password': BCRYPT.generate_password_hash(data.get('password'))
        }
        return parsed_data
    
    @staticmethod
    def parse_user_data(data:dict) -> dict: 
        parsed_data = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
        }
        return parsed_data
    
    @staticmethod
    def validate_new_user(data:dict) -> bool:
        is_valid = True

        if len(data['first_name']) < 3:
            flash(u'First name must be at least 3 characters', 'create_user')
            is_valid = False

        if len(data['last_name']) < 1:
            flash(u'Last name must be at least 1 character', 'create_user')
            is_valid = False
        return is_valid

    @staticmethod
    def validate_registration(data:dict) -> bool:
        is_valid = True

        if len(data['first_name']) < 3:
            flash(u'First name must be at least 3 characters', 'register')
            is_valid = False

        if len(data['last_name']) < 1:
            flash(u'Last name must be at least 1 character', 'register')
            is_valid = False

        if not EMAIL_REGEX.match(data['email']):
            flash(u'Email address is not valid', 'register')
            is_valid = False

        if User.get_user_by_email(data):
                flash(u'Email address is already in use', 'register')
                is_valid = False

        if not PASSWORD_REGEX.match(data['password']) and len(data['password']) < 8:
            flash(u'Password must include: length of 8 characters, one uppercase letter, one digit, and include special character.', 'register')
            is_valid = False

        if not data['password'] == data['confirm_password']:
            flash(u'Passwords entered do not match', 'register')
            is_valid = False

        return is_valid

    # CLASS METHODS

    @classmethod
    def get_user_by_email(cls, data):
        query = '''
        SELECT * FROM users WHERE email = %(email)s;
        '''
        result = connectToMySQL('friendships').query_db(query,data)
        if not result:
            return False
        
        user = cls(result[0])

        return user

    def check_password(cls, data):
        query = '''
        SELECT %(email)s FROM users WHERE password = %(password)s;
        '''

        result = connectToMySQL('friendships').query_db(query, data)
        if not result:
            return False

        user = cls(result[0])

        return user

    @classmethod
    def save(cls, data):
        query = '''
        INSERT INTO users (first_name, last_name, email, password)
        VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);
        '''

        return connectToMySQL('friendships').query_db(query, data)
    
    @classmethod
    def user_add(cls, data:dict):
        query = '''
        INSERT INTO users (first_name, last_name)
        VALUES (%(first_name)s, %(last_name)s);
        '''

        return connectToMySQL('friendships').query_db(query, data)
    
    @classmethod
    def get_user_by_id(cls, data):
        query = '''
        SELECT * FROM users WHERE users.id = %(id)s;
        '''
        result = connectToMySQL('friendships').query_db(query, data)
        if not result:
            return False
        
        return cls(result[0])

    @classmethod
    def get_all(cls):
        query = '''
        SELECT * FROM users;
        '''

        results = connectToMySQL('friendships').query_db(query)

        all_users = []

        if results:
            for row in results:
                all_users.append(cls(row))

            return all_users

        else:
            print('ooopsie no results!!!')

    @classmethod
    def create_friendship(cls, data:dict):
        query = '''
        INSERT INTO friendships (user_id, friend_id)
        SELECT %(user_id)s, %(friend_id)s
        WHERE NOT EXISTS
        (SELECT user_id, friend_id FROM friendships WHERE user_id = %(user_id)s AND friend_id = %(friend_id)s);
        '''

        return connectToMySQL('friendships').query_db(query, data)
    
    @classmethod
    def get_all_friendships(cls):
        query = '''
        SELECT *, friendships.id, users2.id, users2.first_name AS friend_first_name, users2.last_name AS friend_last_name
        FROM users
        JOIN friendships ON users.id = user_id
        LEFT JOIN users AS users2 ON users2.id = friend_id;
        '''

        results = connectToMySQL('friendships').query_db(query)

        all_friendships = []

        if results:
            for row in results:
                one_user = cls(row)

                friend_data = {
                    'id': row.get('users2.id'),
                    'first_name': row.get('users2.first_name'),
                    'last_name': row.get('users2.last_name'),
                    'email': row.get('users2.email'),
                    'password': row.get('users2.password'),
                    'created_at': row.get('users2.created_at'),
                    'updated_at': row.get('users2.updated_at')
                }

                one_friendship = User(friend_data)
                print(f"Printing friend data {friend_data}....................................")
                one_user.friends.append(one_friendship)
                print(f"Printing friends.append {one_user.friends}...........................")
                all_friendships.append(one_user)

            return all_friendships
        else:
            print("Oh no, our table... It's empty!")


