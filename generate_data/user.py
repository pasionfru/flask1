import random

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from faker import Faker
from datetime import datetime

import models
from extensions import db

app = Flask(__name__)

#配置数据库并连接数据库表
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:123456qwe@localhost/work?charset=utf8'
# 初始化数据库
db.init_app(app)


# 生成并插入用户数据
def generate_users(num_users=200):
    fake = Faker() # 初始化 Faker 实例
    users = [] # 用于存储生成的用户对象

    for _ in range(num_users):
        username = fake.user_name()
        password = fake.password()
        email = fake.email()
        phone_number = fake.phone_number()[:20]

        user = models.Users(username=username, password=password, email=email, phone_number=phone_number)
        #每生成一条添加到users列表
        users.append(user)

    db.session.bulk_save_objects(users)  # 批量插入
    db.session.commit()  # 提交事务


if __name__ == '__main__':
    with app.app_context():
        generate_users()  # 生成并插入用户数据-