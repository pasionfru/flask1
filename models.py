from extensions import db
from datetime import datetime

#ORM关系对象模型映射

# 用户
class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.now)

# 航班信息
class Flight(db.Model):
    __tablename__ = 'flights'
    id = db.Column(db.Integer, primary_key=True)
    flight_name = db.Column(db.String(100), nullable=False)
    departure_city = db.Column(db.String(100), nullable=False)
    arrival_city = db.Column(db.String(100), nullable=False)
    flight_date = db.Column(db.Date, nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    order_amount = db.Column(db.Integer, nullable=False)

# 航班订单信息
class FlightOrder(db.Model):
    __tablename__ = 'flights_order'
    id = db.Column(db.Integer, primary_key=True)
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    order_amount = db.Column(db.Float, nullable=False)
    # 给Flight 添加一个属性orders 一对多
    flight = db.relationship('Flight', backref=db.backref('orders', lazy=True)) # SQLAlchemy 会在需要时才会发送SQL查询所有订单。

    user = db.relationship('Users', backref=db.backref('orders', lazy=True))



#酒店表
class Hotels(db.Model):
    __tablename__ = 'hotels'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    description_short = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    checkin_date = db.Column(db.Date, nullable=False)
    checkout_date = db.Column(db.Date, nullable=False)

#酒店详情表
class HotelDetails(db.Model):
    __tablename__ = 'hotel_details'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=False)
    image_url_1 = db.Column(db.String(255), nullable=False)
    image_url_2 = db.Column(db.String(255), nullable=False)
    image_url_3 = db.Column(db.String(255), nullable=False)
    image_url_4 = db.Column(db.String(255), nullable=False)
    image_url_5 = db.Column(db.String(255), nullable=False)
    image_url_6 = db.Column(db.String(255), nullable=False)
    map = db.Column(db.String(100))



#酒店评论表
class HotelReviews(db.Model):
    __tablename__ = 'hotel_reviews'
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('Users', backref='reviews', lazy=True)
    hotel = db.relationship('Hotels', backref='reviews', lazy=True)

#酒店预订表
class HotelBooking(db.Model):
    __tablename__ = 'hotel_bookings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('hotel_rooms.id'), nullable=False)

    checkin_date = db.Column(db.Date, nullable=False)
    checkout_date = db.Column(db.Date, nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.now)

    guest_name = db.Column(db.String(100), nullable=False)
    guest_email = db.Column(db.String(100))
    guest_phone = db.Column(db.String(20), nullable=False)

    # 关系
    user = db.relationship('Users', backref=db.backref('hotel_bookings', lazy=True))
    hotel = db.relationship('Hotels', backref=db.backref('hotel_bookings', lazy=True))
    room = db.relationship('HotelRooms', backref=db.backref('hotel_bookings', lazy=True))
#酒店房间表
class HotelRooms(db.Model):
    __tablename__ = 'hotel_rooms'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=False)
    room_type = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    available = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(255), nullable=False)

 #储存用户发布的旅游攻略
class TravelGuides(db.Model):
    __tablename__ = 'travel_guides'
    guide_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # 外键，关联到 Users 表
    head_img = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    start_date = db.Column(db.DateTime)
    days = db.Column(db.String(100))
    avg_cost = db.Column(db.String(100))


    user = db.relationship('Users', backref='guides', lazy=True)

#用户关注
class TravelFollows(db.Model):
    __tablename__ = 'travel_follows'

    #关注者的用户 ID
    follower_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    #被关注者的用户 ID
    followed_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)

    follower = db.relationship('Users', foreign_keys=[follower_id], backref='following', lazy=True)
    followed = db.relationship('Users', foreign_keys=[followed_id], backref='followers', lazy=True)



#旅游评论
class TravelComments(db.Model):
    __tablename__ = 'travel_comments'

    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    guide_id = db.Column(db.Integer, db.ForeignKey('travel_guides.guide_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    parent_id = db.Column(db.Integer, db.ForeignKey('travel_comments.comment_id'), nullable=True)

    guide = db.relationship('TravelGuides', backref='comments', lazy=True)
    user = db.relationship('Users', backref='comments', lazy=True)
    parent = db.relationship('TravelComments', remote_side=[comment_id], backref='replies', lazy=True)


#用户图片库
class UserImages(db.Model):

    __tablename__ = 'user_images'

    image_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    travel_img = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('Users', backref='images', lazy=True)



#用于存储每个攻略的段落
class TravelGuideSections(db.Model):

    __tablename__ = 'travel_guide_sections'

    section_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    guide_id = db.Column(db.Integer, db.ForeignKey('travel_guides.guide_id'), nullable=False)
    section_pre = db.Column(db.String(100), nullable=False)  # 前言
    section_title = db.Column(db.String(100), nullable=False)  # 标题
    section_content = db.Column(db.Text, nullable=False)  # 内容
    created_at = db.Column(db.DateTime, default=datetime.now)


    guide = db.relationship('TravelGuides', backref=db.backref('sections', lazy=True))

#餐饮产品表
class Catering(db.Model):
    __tablename__ = 'catering'

    catering_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Numeric(2, 1), nullable=False)  # 餐馆评分，0到5之间，保留一位小数
    address = db.Column(db.String(255), nullable=False)
    tags = db.Column(db.String(255))
    catering_img = db.Column(db.String(255), nullable=False)

#餐饮产品预订表
class CateringBookings(db.Model):
    __tablename__ = 'catering_bookings'

    reservation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    catering_id = db.Column(db.Integer, db.ForeignKey('catering.catering_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    reservation_date = db.Column(db.Date, nullable=False)
    reservation_time = db.Column(db.Time, nullable=False)
    guest_count = db.Column(db.Integer, nullable=False)
    table_condition = db.Column(db.Enum('只订包房', '只订大厅', '大厅优先', '包房优先'), nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)


    catering = db.relationship('Catering', backref=db.backref('reservations', lazy=True))
    user = db.relationship('Users', backref=db.backref('catering_reservations', lazy=True))

# 餐厅评价
class CateringReview(db.Model):
    __tablename__ = 'catering_reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    catering_id = db.Column(db.Integer, db.ForeignKey('catering.catering_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)


    catering = db.relationship('Catering', backref=db.backref('reviews', lazy=True))
    user = db.relationship('Users', backref=db.backref('catering_reviews', lazy=True))


#导游信息
class TourGuide(db.Model):
    __tablename__ = 'tour_guides'

    guide_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)  # 导游介绍
    guide_fee = db.Column(db.Numeric(10, 2), nullable=False)
    avatar_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)
    rating = db.Column(db.Float,nullable=False)

#导游评价
class TourGuidesReview(db.Model):
    __tablename__ = 'tour_guides_reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    guide_id = db.Column(db.Integer, db.ForeignKey('tour_guides.guide_id', ondelete="CASCADE"),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    guide = db.relationship('TourGuide', backref=db.backref('reviews', lazy=True, cascade="all, delete"))
    user = db.relationship('Users', backref=db.backref('guide_reviews', lazy=True, cascade="all, delete"))

#导游预订
class TourGuideBooking(db.Model):
    __tablename__ = 'tour_guide_bookings'

    booking_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    guide_id = db.Column(db.Integer, db.ForeignKey('tour_guides.guide_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    service_start = db.Column(db.DateTime, nullable=False)
    service_end = db.Column(db.DateTime, nullable=False)
    adult_count = db.Column(db.Integer, nullable=False)
    child_count = db.Column(db.Integer, nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    guide = db.relationship('TourGuide', backref=db.backref('bookings', lazy=True))



#跟团游列表
class Tour(db.Model):
    __tablename__ = 'tours'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    description_short = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Float, nullable=False)


#旅游
class ToursBooking(db.Model):
    __tablename__ = 'tours_bookings'

    booking_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tour_id = db.Column(db.Integer, db.ForeignKey('tours.id', ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    departure_date = db.Column(db.Date, nullable=False)
    adult_count = db.Column(db.Integer, nullable=False)
    child_count = db.Column(db.Integer)  # 儿童人数
    contact_name = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)


    tour = db.relationship('Tour', backref=db.backref('bookings', lazy=True, cascade="all, delete"))
    user = db.relationship('Users', backref=db.backref('bookings', lazy=True, cascade="all, delete"))


#旅游预订
class ToursBookingsTraveler(db.Model):
    __tablename__ = 'tours_bookings_traveler'

    id = db.Column(db.Integer, primary_key=True)
    tours_booking_id = db.Column(db.Integer, db.ForeignKey('tours_bookings.booking_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    nationality = db.Column(db.String(100), nullable=False)
    id_number = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

#旅游评价
class ToursReview(db.Model):
    __tablename__ = 'tours_reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tour_id = db.Column(db.Integer, db.ForeignKey('tours.id', ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)


    tour = db.relationship('Tour', backref=db.backref('reviews', lazy=True, cascade="all, delete"))
    user = db.relationship('Users', backref=db.backref('user_reviews', lazy=True, cascade="all, delete"))
