from peewee import *

db = SqliteDatabase('sqlite3.db')

class Rool(Model):
    id = PrimaryKeyField()
    name = CharField()

    class Meta:
        database = db
class User(Model):
    id = PrimaryKeyField()
    chat_id = IntegerField(unique=True) # This line creates a unique field for each user.
    first_name = CharField()
    last_name = CharField()
    phone = CharField()
    rool = ForeignKeyField(Rool, backref='users') 
    status_work = CharField()

    class Meta:
        database = db



class Report(Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, backref='reports')
    date = DateTimeField()
    text = TextField()

    class Meta:
        database = db



db.connect()
db.create_tables([Rool, User]) # This line creates the tables in the database.        