from datetime import datetime
from mongoengine import (
    StringField,
    IntField,
    ReferenceField,
    DateTimeField,
    EmailField
)
from .db import db    
class User(db.Document):
    """
    Users on the auction site
    """ 

    email = EmailField(require=True, unique=True)
    password = StringField(required=True)
    created_at = DateTimeField(required=True, default=datetime.utcnow)

class Item(db.Document):
    """
    Items on the auction site
    """

    title = StringField(max_length=100, required=True)
    description = StringField(max_length=2000, required=True)
    starting_bid = IntField(required=True, min_value=0)
    seller = ReferenceField(User, required=True)
    created_at = DateTimeField(required=True, default=datetime.utcnow)
    closed_at = DateTimeField()
    