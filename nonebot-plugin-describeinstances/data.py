"""
 - Author: DiheChen
 - Date: 2021-08-23 09:59:12
 - LastEditTime: 2021-08-26 05:31:48
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/Chendihe4975
"""
import peewee as pw
from os import path

db_path = path.abspath(
    path.join(path.dirname(__file__), "describeinstances.db"))
db = pw.SqliteDatabase(db_path)


class BaseModel(pw.Model):
    class Meta:
        database = db


class DescribeInstances(BaseModel):
    """
    - `instances` 实例
    - `instances_en` 实例英文名
    - `describe` 实例描述
    """
    instances = pw.TextField()
    instances_en = pw.TextField()
    describe = pw.TextField()

    class Meta:
        primary_key = pw.CompositeKey("instances", "instances_en")


if not path.exists(db_path):
    db.connect()
    db.create_tables([DescribeInstances])
    db.close()
