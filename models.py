from peewee import *

db = SqliteDatabase('sqlite3.db')

class Rool(Model):
    id = PrimaryKeyField()
    name = CharField()

    class Meta:
        database = db
class User(Model):
    id = PrimaryKeyField()
    chat_id = IntegerField(unique=True)  # افزودن chat_id برای نگهداری ID تلگرام کاربر
    first_name = CharField()
    last_name = CharField()
    phone = CharField()
    rool = ForeignKeyField(Rool, backref='users')  # تصحیح backref
    status_work = CharField()

    class Meta:
        database = db


db.connect()
db.create_tables([Rool, User]) # This line creates the tables in the database.        