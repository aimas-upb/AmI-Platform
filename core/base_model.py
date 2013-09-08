from mongoengine import *

class BaseModel(Document):
    meta = {'collection': 'docs', 'allow_inheritance': True}
