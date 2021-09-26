"""
 - Author: DiheChen
 - Date: 2021-09-04 13:34:27
 - LastEditTime: 2021-09-27 00:21:27
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/Chendihe4975
"""
from os import path

import peewee as pw

db_path = path.abspath(path.join(path.dirname(__file__), "setu_data.db"))
db = pw.SqliteDatabase(db_path)


class BaseModel(pw.Model):
    class Meta:
        database = db


class UserXP(BaseModel):
    user_id = pw.IntegerField()
    tag = pw.CharField()
    count = pw.IntegerField()

    class Meta:
        primary_key = pw.CompositeKey("user_id", "tag")


if not path.exists(db_path):
    db.connect()
    db.create_tables([Block, UserXP])
    db.close()
