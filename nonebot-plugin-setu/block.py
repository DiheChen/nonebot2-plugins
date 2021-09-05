"""
 - Author: DiheChen
 - Date: 2021-09-04 13:34:27
 - LastEditTime: 2021-09-04 18:13:25
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/Chendihe4975
"""
from os import path

import peewee as pw

db_path = path.abspath(path.join(path.dirname(__file__), "block.db"))
db = pw.SqliteDatabase(db_path)


class BaseModel(pw.Model):
    class Meta:
        database = db


class Block(BaseModel):
    id = pw.AutoField(primary_key=True)
    user_id = pw.IntegerField(null=True)
    group_id = pw.IntegerField(null=True)


if not path.exists(db_path):
    db.connect()
    db.create_tables([Block])
    db.close()
