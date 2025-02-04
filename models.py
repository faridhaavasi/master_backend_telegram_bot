from peewee import *

db = SqliteDatabase('sqlite3.db')

class Rool(Model):
    id = PrimaryKeyField()
    name = CharField()

    class Meta:
        database = db

class User(Model):
    id = PrimaryKeyField()
    first_name = CharField()
    last_name = CharField()
    phone = CharField() # This field is a string that will hold the phone number.
    rool = ForeignKeyField(Rool, backref='rools') # This field is a foreign key that will hold the rool of the user.
    status_work = CharField() # This field is a string that will hold the status of the user.
    
    class Meta:
        database = db # This model uses the "people.db" database.

db.connect()
db.create_tables([Rool, User]) # This line creates the tables in the database.        