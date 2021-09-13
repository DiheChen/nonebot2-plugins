"""
 - Author: DiheChen
 - Date: 2021-08-24 11:32:30
 - LastEditTime: 2021-09-13 22:17:44
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/DiheChen
"""
import peewee as pw
from os import path

db_path = path.abspath(path.join(path.dirname(__file__), "image_msg.db"))
db = pw.SqliteDatabase(db_path)


class BaseModel(pw.Model):
    class Meta:
        database = db


class ImageMessage(BaseModel):
    """
    - `time_stamp` 用户第一次发送该图片的时间戳
    - `user_id` 用户 qq 号
    - `group_id` qq 群号
    - `image_md5` 该图片的 md5 值
    - `sent_count` 此人发送该图数量
    """
    time_stamp = pw.IntegerField()
    user_id = pw.IntegerField()
    group_id = pw.IntegerField()
    image_md5 = pw.TextField()
    sent_count = pw.IntegerField()

    class Meta:
        primary_key = pw.CompositeKey("user_id", "group_id", "image_md5")


if not path.exists(db_path):
    db.connect()
    db.create_tables([ImageMessage])
    db.close()
