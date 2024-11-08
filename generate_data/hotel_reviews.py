import random

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from faker import Faker
from datetime import datetime

import models
from extensions import db


app = Flask(__name__) #创建一个 Flask 应用实例。

#配置数据库并连接数据库表
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:123456qwe@localhost/work?charset=utf8'
# 初始化数据库
db.init_app(app)


# 生成并插入酒店评论数据
def generate_reviews(num_reviews=500):
    fake = Faker("zh_CN")  # 用于生成中文内容。
    reviews = []
    # 直接设定用户 ID 范围在 211 到 410
    user_ids = list(range(211, 411))

    for _ in range(num_reviews):
        hotel_id = random.randint(1, 6)  # hotel_id 范围为 1 到 6
        user_id = random.choice(user_ids)  # 从 211 到 410 范围中随机选择用户ID
        rating = random.randint(1, 5)  # 评分范围为 1 到 5
        content = fake.text(max_nb_chars=30)[:15]  # 生成中文评论内容，限制为 15 个字以内
        created_at = fake.date_time_this_year(before_now=True, after_now=False)  # 生成今年的日期

        # 创建评论对象并添加到列表
        review = models.HotelReviews(hotel_id=hotel_id, user_id=user_id, rating=rating, content=content,
                                     created_at=created_at)
        reviews.append(review)

    db.session.bulk_save_objects(reviews)  # 批量插入
    db.session.commit()  # 提交事务

if __name__ == '__main__':
    with app.app_context():
        generate_reviews()  # 生成并插入评论数据