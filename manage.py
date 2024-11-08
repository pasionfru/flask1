import json
from datetime import datetime, timedelta
import random
from http.client import responses
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from unicodedata import east_asian_width
from werkzeug.utils import secure_filename
from extensions import db

import models
from models import Users, Flight, FlightOrder

from nlp_reviews_api import fetch_token, COMMENT_TAG_URL, make_request

app = Flask(__name__)
app.config.from_object('config')

# 初始化并连接数据库
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:123456qwe@localhost/work?charset=utf8'
db.init_app(app)


# 主页
@app.route('/')
def main():
    # tours = models.Tour.query.all()
    # return render_template('test.html',tours=tours)
    return render_template('index.html')


# 登录后台
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = models.Users.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.user_id
            session['username'] = user.username
            return redirect(url_for('user_profile', user_id=user.user_id))
        else:
            flash("用户名或密码错误")
            return redirect(url_for('login'))
    return render_template('login.html')


# 注册后台
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone_number = request.form['phone_number']
        registration_date = datetime.now()

        # 检测用户名是否存在
        existing_user = models.Users.query.filter_by(username=username).first()
        if existing_user:
            flash("该用户已存在")
            return redirect(url_for('register'))

        new_user = models.Users(username=username, password=password, email=email, phone_number=phone_number,
                                registration_date=registration_date)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("注册成功！请登录")
            return redirect(url_for('login'))  # 注册成功后跳转到登录页面
        except:
            db.session.rollback()
            flash("注册失败，请稍后重试")
            return redirect(url_for('register'))

    return render_template('register.html')


# 机票预定页面1
@app.route('/plane_ticket', methods=['GET', 'POST'])
def plane_ticket():
    return render_template('plane_ticket.html')


# 机票搜索页面
@app.route('/plane_search', methods=['POST'])
def search_flights():
    if request.method == 'POST':
        departure_city = request.form['from']
        arrival_city = request.form['to']
        departure_time = datetime.strptime(request.form['departure'], '%Y-%m-%d')
        arrival_time = datetime.strptime(request.form['returnDate'], '%Y-%m-%d')
        # 到达时间为第二天的00:00点之前，方便后续搜索机票
        arrival_time = arrival_time + timedelta(days=1)

    query = models.Flight.query.filter(
        models.Flight.departure_city == departure_city,
        models.Flight.arrival_city == arrival_city,

        # 这里查询不出来 是因为数据库的departure_time是datetime类型
        # models.Flight.departure_time == datetime.strptime(departure_time, '%Y-%m-%d').date(),

        # 修复方法:
        models.Flight.departure_time >= departure_time,
        models.Flight.arrival_time <= arrival_time

        # 修复方法2:
        # models.Flight.departure_time == datetime.strptime(departure_time, '%Y-%m-%d').datetime()
    )

    flights = query.all()

    return render_template('plane_search_result.html', flights=flights)


# 机票购买
@app.route('/order/<int:flight_id>', methods=['POST'])
def order_flight(flight_id):
    # 获取当前登录的用户
    user_id = session['user_id']
    if not user_id:
        flash("请先登录")
        # print("123")
        return redirect(url_for('login'))

    flight = models.Flight.query.get(flight_id)
    # print(flight.id)
    # print(user_id)
    # print(flight.order_amount)
    new_order = models.FlightOrder(
        flight_id=flight.id,
        user_id=user_id,
        order_amount=flight.order_amount
    )

    try:
        db.session.add(new_order)
        db.session.commit()
        flash('购票成功！')
        return redirect(url_for('user_profile', user_id=user_id))
    except:
        db.session.rollback()
        flash('购票失败，请重试!')
        return redirect(url_for('plane_search_result'))


# 个人信息页面
@app.route('/user/<int:user_id>')
def user_profile(user_id):
    # 确保用户已登录
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('login'))


    user = models.Users.query.get(user_id)
    if not user:
        return "用户不存在", 404

    tours_orders = models.ToursBooking.query.filter_by(user_id=user_id).all()
    flight_orders = models.FlightOrder.query.filter_by(user_id=user_id).all()
    hotel_orders = models.HotelBooking.query.filter_by(user_id=user_id).all()
    catering_orders = models.CateringBookings.query.filter_by(user_id=user_id).all()
    guide_orders = models.TourGuideBooking.query.filter_by(user_id=user_id).all()
    travel_guides = models.TravelGuides.query.filter_by(user_id=user_id).all()

    return render_template('user_profile.html', user=user, tours_orders=tours_orders,
                           flight_orders=flight_orders, hotel_orders=hotel_orders,
                           catering_orders=catering_orders, guide_orders=guide_orders, travel_guides=travel_guides)


# 管理后台首页
@app.route('/admin')
def admin():
    flights = models.Flight.query.all()
    return render_template('admin.html', flights=flights)


# 注销用户
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('您已成功退出')
    return redirect(url_for('main'))


# 单个旅游的页面介绍
@app.route('/tour/<int:tour_id>')
def tour_detail(tour_id):
    tour = models.Tour.query.get_or_404(tour_id)

    # 查询该旅游景点的评论，获取用户名、评论时间、评论内容和评分
    reviews = (
        models.ToursReview.query
        .filter_by(tour_id=tour_id)
        .join(models.Users, models.ToursReview.user_id == models.Users.user_id)
        .add_columns(
            models.Users.username,  # 用户名
            models.ToursReview.rating,  # 评论评分
            models.ToursReview.content,  # 评论内容
            models.ToursReview.created_at  # 评论时间
        )
        .all()
    )

    return render_template('tour_detail.html', tour=tour, reviews=reviews)


# 添加旅游地点信息
@app.route('/admin/add', methods=['GET', 'POST'])
def add_tour():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        description_short = request.form['description_short']
        image_url = request.form['image_url']
        price = request.form['price']

        new_tour = models.Tour(
            title=title,
            description=description,
            description_short=description_short,
            image_url=image_url,
            price=price
        )
        try:
            db.session.add(new_tour)
            db.session.commit()
            flash('旅游地点信息添加成功！')
            return redirect(url_for('index'))
        except:
            db.session.rollback()
            flash('添加失败，请重试！')
    return render_template('add_tour.html')


# 更新旅游地点信息
@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
def edit_tour(id):
    tour = models.Tour.query.get_or_404(id)
    if request.method == 'POST':
        tour.title = request.form['title']
        tour.description = request.form['description']
        tour.description_short = request.form['description_short']
        tour.image_url = request.form['image_url']
        tour.price = request.form['price']

        try:
            db.session.commit()
            flash('旅游地点信息更新成功！')
            return redirect(url_for('index'))
        except:
            db.session.rollback()
            flash('更新失败，请重试！')
    return render_template('edit_tour.html', tour=tour)


# 删除旅游地点信息
@app.route('/admin/delete/<int:id>', methods=['POST'])
def delete_tour(id):
    tour = models.Tour.query.get_or_404(id)
    try:
        db.session.delete(tour)
        db.session.commit()
        flash('旅游地点信息删除成功！')
    except:
        db.session.rollback()
        flash('删除失败，请重试！')
    return redirect(url_for('index'))


@app.route('/tour')
def tour_index():
    tours = models.Tour.query.all()
    random.shuffle(tours)
    return render_template('tour.html', tours=tours)


@app.route('/get_flights')
def get_flights():
    departure = request.args.get('departure')
    destination = request.args.get('destination')
    date = request.args.get('date')
    # 在数据库中查询符合条件的航班
    flights = models.Flight.query.filter_by(departure_city=departure, arrival_city=destination, flight_date=date).all()
    # 将查询到的航班信息转换为字典并返回
    flights_data = [{
        'flight_name': flight.flight_name,
        'departure_time': flight.departure_time.strftime('%Y-%m-%d %H:%M'),
        'arrival_time': flight.arrival_time.strftime('%Y-%m-%d %H:%M'),
        'order_amount': flight.order_amount
    } for flight in flights]

    return jsonify(flights_data)


@app.route('/hotel', methods=['GET'])
def hotel_index():
    # 如果没有参数传递，则返回酒店页面
    if not request.args:
        hotels = models.Hotels.query.all()
        random.shuffle(hotels)
        return render_template('hotel.html', hotels=hotels)

    # 如果有参数传递，则执行搜索
    destination = request.args.get('destination', '不限')
    keyword = request.args.get('keyword', '').strip()
    checkin = request.args.get('checkin')
    checkout = request.args.get('checkout')

    # 将日期字符串转换为 datetime 对象
    try:
        checkin_date = datetime.strptime(checkin, '%Y-%m-%d').date()
        checkout_date = datetime.strptime(checkout, '%Y-%m-%d').date()
    except ValueError:
        return jsonify([])  # 日期格式错误，返回空结果

    # 查询酒店信息
    query = models.Hotels.query

    # 根据目的地过滤
    if destination and destination != '不限':
        query = query.filter(models.Hotels.location == destination)

    # 根据关键词过滤 (标题或者描述是否包含关键词)
    if keyword:
        query = query.filter((models.Hotels.title.contains(keyword)) | (models.Hotels.description.contains(keyword)))

    # 根据入住和离店日期过滤
    query = query.filter(models.Hotels.checkin_date <= checkin_date, models.Hotels.checkout_date >= checkout_date)

    hotels = query.all()

    return render_template('hotel.html', hotels=hotels)


@app.route('/hotel/<int:hotel_id>')
def get_hotel_details(hotel_id):
    # 查询数据库中对应的酒店信息
    hotel = models.Hotels.query.get_or_404(hotel_id)
    hotel_detail = models.HotelDetails.query.get_or_404(hotel_id)
    hotelrooms = models.HotelRooms.query.filter_by(hotel_id=hotel_id).all()
    hotelreviews = models.HotelReviews.query.filter_by(hotel_id=hotel_id).all()
    hotelreviews_cnt = len(hotelreviews)

    # 提取数据库hotelreviews对应酒店的评论
    comments = " ".join([review.content for review in hotelreviews])
    # print(comments)
    # 获取token和调用接口
    token = fetch_token()
    url = COMMENT_TAG_URL + "?charset=UTF-8&access_token=" + token
    # 发送评论分析请求
    response = make_request(url, comments)
    print(type(response))

    # 处理响应
    processed_comments = response  # 假设 response 已经是字典类型

    print("API Response:", response)  # 打印响应以便调试
    return render_template('hotel_detail.html',
                           hotel=hotel, hotel_detail=hotel_detail,
                           hotelrooms=hotelrooms,
                           hotelreviews=hotelreviews,
                           hotelreviews_cnt=hotelreviews_cnt,
                           processed_comments=processed_comments)


@app.route('/submit-review/<int:hotel_id>', methods=['POST'])
def submit_review(hotel_id):
    # 获取评论数

    hotel_reviews = models.HotelReviews.query.filter_by(hotel_id=hotel_id).all()  # 获取评论列表
    review_count = len(hotel_reviews)  # 计算评论数量

    # 检查用户是否已登录
    if 'user_id' not in session:
        flash('请先登录')
        return redirect(url_for('login'))  # 重定向到登录页面

    # 获取用户输入的点评内容和评分
    review_content = request.form.get('review')
    rating = int(request.form.get('rating'))

    # 从 session 获取 user_id
    user_id = session['user_id']

    # 创建新评论对象并保存到数据库
    new_review = models.HotelReviews(
        hotel_id=hotel_id,
        user_id=user_id,
        content=review_content,
        rating=rating)
    db.session.add(new_review)
    db.session.commit()
    return redirect(url_for('get_hotel_details', hotel_id=hotel_id))


# 酒店预定
@app.route('/room-booking/<int:room_id>', methods=['GET', 'POST'])
def book_room(room_id):
    room = models.HotelRooms.query.get_or_404(room_id)
    # room.hotel_id 的外键是 hotels.id ，查询到对应酒店标题
    hotel = models.Hotels.query.get_or_404(room.hotel_id)

    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            flash('请先登录')
            return redirect(url_for('login'))

        # 进出日期
        checkin_date = request.form['checkin']
        checkout_date = request.form['checkout']
        room_count = request.form['room-count']

        # 创建用户信息列表 循环读取
        guest_info = []
        for i in range(1, int(room_count) + 1):
            # 游客资料
            guest_name = request.form[f'guest-name-{i}']
            guest_email = request.form[f'guest-email-{i}']
            guest_phone = request.form[f'guest-phone-{i}']
            guest_info.append({'name': guest_name, 'email': guest_email, 'phone': guest_phone})

            # 检查必填项是否有空
            if not guest_name or not guest_phone:
                flash('请填写完整的住客信息')
                return redirect(url_for('hotel_detail_booking', room=room, hotel=hotel))

        for guest in guest_info:
            booking = models.HotelBooking(
                user_id=user_id,
                room_id=room.id,
                checkin_date=datetime.strptime(checkin_date, '%Y-%m-%d').date(),
                checkout_date=datetime.strptime(checkout_date, '%Y-%m-%d').date(),
                guest_name=guest['name'],
                guest_email=guest['email'],
                guest_phone=guest['phone'],
                hotel_id=hotel.id
            )
            print(user_id, room_id, checkin_date, checkout_date, guest_email, guest_phone)
            db.session.add(booking)
        db.session.commit()
        return render_template('buy_success.html', room=room, hotel=hotel)

    return render_template('hotel_detail_booking.html', room=room, hotel=hotel)


@app.route('/buy_success')
def buy_success():
    return render_template('buy_success.html')


@app.route('/travel_guide')
def travel_guide():
    guides = models.TravelGuides.query.all()
    structured_guides = []
    for guide in guides:
        user = Users.query.get(guide.user_id)
        images = [img.travel_img for img in models.UserImages.query.filter_by(user_id=guide.user_id).all()]

        structured_guides.append({
            'title': guide.title,
            'username': user.username,
            'created_at': guide.created_at,
            'head_img': guide.head_img,  # 如果存储头图
            'images': images,
            'start_date': guide.start_date,
            'days': guide.days,
            'guide_id': guide.guide_id
        })
    user_id = session.get('user_id')
    return render_template('travel_guide.html', guides=structured_guides, user_id=user_id)


@app.route('/travel_guide_write/<int:user_id>')
def travel_guide_write(user_id):
    # 查询用户上传的所有图片
    user_images = models.UserImages.query.filter_by(user_id=user_id).all()
    image_paths = [image.travel_img for image in user_images]

    # 渲染模板，并传递照片路径
    return render_template('travel_guide_write.html', image_paths=image_paths)


UPLOAD_FOLDER = 'static/uploads/user_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/upload_user_image', methods=['POST'])
def upload_user_image():
    user_id = session.get('user_id')  # 假设已知用户ID
    files = request.files.getlist('images')

    image_paths = []
    for file in files:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # 确认文件路径是否正确
        print("Saving to path:", file_path)

        try:
            # 保存文件到服务器
            file.save(file_path)

            # 将路径转换为相对路径，并标准化为适合网页显示的格式
            web_path = '/' + os.path.normpath(file_path).replace('\\', '/')

            # 将标准化后的路径存储到数据库
            image_record = models.UserImages(user_id=user_id, travel_img=web_path)
            db.session.add(image_record)
            db.session.commit()

            # 添加路径到返回列表
            image_paths.append(web_path)

        except FileNotFoundError as e:
            print("文件保存错误:", e)
            return jsonify({'success': False, 'message': f'文件保存错误: {e}'}), 500

    return jsonify({'success': True, 'image_paths': image_paths})


UPLOAD_FOLDER = 'static/uploads/guide_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 在应用启动时检查目录是否存在，不存在则创建
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/upload_head_image', methods=['POST'])
def upload_head_image():
    title = request.form.get('title')
    head_img = request.files.get('head_img')

    # 检查并创建目录
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # 保存头图
    head_img_path = None
    if head_img:
        # 使用安全的文件名
        filename = secure_filename(head_img.filename)
        head_img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # 保存文件
        head_img.save(head_img_path)

    # 保存标题和路径到数据库的其他逻辑...

    return jsonify({'success': True, 'head_img_path': head_img_path})


# 发表攻略
@app.route('/submit_guide', methods=['POST'])
def submit_guide():
    # 获取基本信息
    title = request.form.get('title')
    user_id = session.get('user_id')
    head_img = request.files.get('head_img')
    start_date = request.form.get('start_time')
    days = request.form.get('days')
    avg_cost = request.form.get('avgCost')

    # 调试输出接收到的数据
    print("Title:", title)
    print("Start Date:", start_date)
    print("Days:", days)
    print("Average Cost:", avg_cost)

    # 保存头图
    head_img_path = None
    if head_img:
        head_img_path = os.path.join('static/uploads/guide_images', head_img.filename)
        head_img.save(head_img_path)

    # 创建 TravelGuide 实例
    new_guide = models.TravelGuides(
        user_id=user_id,
        title=title,
        head_img=head_img_path,
        start_date=start_date,
        days=days,
        avg_cost=avg_cost
    )
    db.session.add(new_guide)
    db.session.commit()

    # 处理并保存每个 section
    sections = []
    for key, value in request.form.items():
        if key.startswith('sections'):
            index = int(key.split('[')[1].split(']')[0])
            while len(sections) <= index:
                sections.append({'section_pre': '', 'section_title': '', 'section_content': ''})
            if 'section_pre' in key:
                sections[index]['section_pre'] = value
            elif 'section_title' in key:
                sections[index]['section_title'] = value
            elif 'section_content' in key:
                sections[index]['section_content'] = value

    # 保存每个 section
    for section in sections:
        new_section = models.TravelGuideSections(
            guide_id=new_guide.guide_id,
            section_pre=section['section_pre'],
            section_title=section['section_title'],
            section_content=section['section_content']
        )
        db.session.add(new_section)
    db.session.commit()
    print("Received sections:", sections)
    return jsonify({'success': True})


@app.route('/travel_guide_show/<int:guide_id>')
def travel_guide_show(guide_id):
    guide = models.TravelGuides.query.get_or_404(guide_id)
    # 获取作者信息
    author = models.Users.query.get(guide.user_id)
    # 获取攻略的详细内容（段落）
    sections = models.TravelGuideSections.query.filter_by(guide_id=guide_id).all()
    # print("Sections:", sections)  # 调试输出
    # for section in sections:
    #     print("Section ID:", section.section_id)
    #     print("Guide ID:", section.guide_id)
    #     print("Section Pre:", section.section_pre)
    #     print("Section Title:", section.section_title)
    #     print("Section Content:", section.section_content)
    #     print("Created At:", section.created_at)
    #     print("-" * 20)  # 用于分隔每个 section 的输出，方便阅读

    comments = models.TravelComments.query.filter_by(guide_id=guide_id).all()
    # 获取用户名列表
    comments_username = []
    for comment in comments:
        user = models.Users.query.get(comment.user_id)
        comments_username.append(
            {
                'comment': comment,
                'username': user.username
            }
        )

    return render_template('travel_guide_show.html', guide=guide, author=author, sections=sections, comments=comments,
                           comments_username=comments_username)


# 发表评论
@app.route('/post_comment/<int:guide_id>', methods=['POST'])
def post_comment(guide_id):
    content = request.form.get('content')
    user_id = session.get('user_id')
    new_comment = models.TravelComments(guide_id=guide_id, user_id=user_id, content=content)
    print(f"Guide ID: {guide_id}, User ID: {user_id}, Content: {content}")
    try:
        db.session.add(new_comment)
        db.session.commit()
        flash('评论成功发表！', 'success')
    except Exception as e:
        db.session.rollback()
        flash('评论发表失败，请重试。', 'danger')

    return redirect(url_for('travel_guide_show', guide_id=guide_id))


@app.route('/post_reply/<int:guide_id>/<int:parent_id>', methods=['POST'])
def post_reply(guide_id, parent_id):
    content = request.form.get('content')
    user_id = session.get('user_id')

    if not user_id:
        flash('用户未登录，请先登录。', 'warning')
        return redirect(url_for('travel_guide_show', guide_id=guide_id))

    new_reply = models.TravelComments(guide_id=guide_id, user_id=user_id, content=content, parent_id=parent_id)

    try:
        db.session.add(new_reply)
        db.session.commit()
        flash('回复成功发表！', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        flash('回复发表失败，请重试。', 'danger')

    return redirect(url_for('travel_guide_show', guide_id=guide_id))


@app.route("/travel_guide_personal/<int:user_id>")
def travel_guide_personal(user_id):
    # 获取用户信息
    user = models.Users.query.get_or_404(user_id)

    # 获取用户的关注数
    following_count = models.TravelFollows.query.filter_by(follower_id=user_id).count()

    # 获取用户的粉丝数
    followers_count = models.TravelFollows.query.filter_by(followed_id=user_id).count()

    # 获取用户的旅游攻略
    travel_guides = models.TravelGuides.query.filter_by(user_id=user_id).all()

    return render_template('travel_guide_personal.html', user=user, travel_guides=travel_guides,
                           following_count=following_count, followers_count=followers_count)


@app.route("/post_follow/<int:followed_id>", methods=['POST'])
def post_follow(followed_id):
    follower_id = session.get('user_id')

    if follower_id == followed_id:
        flash('您不能关注自己！', 'danger')
        return redirect(request.referrer)

    # 检查是否已关注
    existing_follow = models.TravelFollows.query.filter_by(follower_id=follower_id, followed_id=followed_id).first()
    if existing_follow:
        flash('您已经关注过此用户！', 'warning')
    else:
        new_follow = models.TravelFollows(follower_id=follower_id, followed_id=followed_id)
        db.session.add(new_follow)
        db.session.commit()
        flash('关注成功！', 'success')

    return redirect(request.referrer)


# 餐厅
@app.route("/catering")
def catering():
    caterings = models.Catering.query.all()
    return render_template('catering.html', caterings=caterings)


# 餐厅详情页面
@app.route("/catering_show/<int:catering_id>")
def catering_show(catering_id):
    catering = models.Catering.query.get_or_404(catering_id)
    catering_reviews = models.CateringReview.query.filter_by(catering_id=catering_id).all()
    return render_template('catering_show.html', catering=catering, catering_reviews=catering_reviews)


@app.route("/catering_show_booking/<int:catering_id>")
def catering_show_booking(catering_id):
    # 获取餐厅信息
    catering = models.Catering.query.get_or_404(catering_id)
    # 获取该餐厅所有的评论

    return render_template('catering_show_booking.html', catering=catering)


@app.route('/submit_reservation/<int:catering_id>', methods=['POST'])
def submit_reservation(catering_id):
    # 从请求中获取数据
    data = request.get_json()
    user_id = session.get('user_id')
    # 提取并验证数据
    dining_date = data.get('dining_date')
    dining_time = data.get('dining_time')
    guest_count = data.get('guest_count')
    table_condition = data.get('table_condition')
    contact_name = data.get('contact_name')
    contact_phone = data.get('contact_phone')
    remarks = data.get('remarks')

    # 数据转换（如有需要）
    try:
        reservation_date = datetime.strptime(dining_date, '%Y-%m-%d').date()
        reservation_time = datetime.strptime(dining_time, '%H:%M').time()
        guest_count = int(guest_count)

        # 创建新的预订记录
        new_reservation = models.CateringBookings(
            catering_id=catering_id,  # 假设已有餐厅 ID，根据需要调整
            user_id=user_id,  # 假设已有用户 ID，根据需要调整
            reservation_date=reservation_date,
            reservation_time=reservation_time,
            guest_count=guest_count,
            table_condition=table_condition,
            contact_name=contact_name,
            contact_phone=contact_phone,
            remarks=remarks
        )

        # 保存到数据库
        db.session.add(new_reservation)
        db.session.commit()

        return jsonify(success=True)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify(success=False)


@app.route("/daoyou")
def daoyou():
    daoyous = models.TourGuide.query.all()
    return render_template('daoyou.html', daoyous=daoyous)


@app.route("/daoyou_detail/<int:guide_id>")
def daoyou_detail(guide_id):
    user_id = session.get('user_id')
    daoyou_info = models.TourGuide.query.filter_by(guide_id=guide_id).first()
    # 查询与该导游相关的评价，获取用户名、评价内容、评分和创建时间
    reviews = (
        models.TourGuidesReview.query
        .filter_by(guide_id=guide_id)
        .join(models.Users, models.TourGuidesReview.user_id == models.Users.user_id)
        .add_columns(
            models.Users.username,  # 用户名
            models.TourGuidesReview.rating,  # 评分
            models.TourGuidesReview.content,  # 评价内容
            models.TourGuidesReview.created_at  # 评价时间
        )
        .all()
    )
    return render_template('daoyou_detail.html', daoyou_info=daoyou_info, reviews=reviews, user_id=user_id)


@app.route('/submit_booking', methods=['POST'])
def submit_booking():
    data = request.get_json()

    # 提取并解析数据
    service_date = data.get('service_date')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    adult_count = data.get('adult_count')
    child_count = data.get('child_count')
    contact_name = data.get('contact_name')
    contact_phone = data.get('contact_phone')
    message = data.get('message')
    guide_id = data.get('guide_id')
    user_id = session.get('user_id')

    # 将日期和时间组合
    try:
        service_start = datetime.strptime(f"{service_date} {start_time}", '%Y-%m-%d %H:%M')
        service_end = datetime.strptime(f"{service_date} {end_time}", '%Y-%m-%d %H:%M')

        # 创建新的预约记录
        new_booking = models.TourGuideBooking(
            guide_id=guide_id,
            service_start=service_start,
            service_end=service_end,
            adult_count=int(adult_count),
            child_count=int(child_count),
            contact_name=contact_name,
            contact_phone=contact_phone,
            message=message,
            user_id=user_id
        )

        db.session.add(new_booking)
        db.session.commit()

        return jsonify(success=True)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify(success=False)


@app.route('/tour_bookings/<int:tour_id>', methods=['POST'])
def tour_bookings(tour_id):
    tour = models.Tour.query.filter_by(id=tour_id).first()
    data = request.get_json()
    date = data.get('date')
    adults = int(data.get('adults'))
    children = int(data.get('children'))
    total_price = data.get('totalPrice')
    return render_template('tour_bookings.html', tour=tour, date=date, adults=adults, children=children,
                           total_price=total_price)


@app.route('/submit_tours_booking', methods=['POST'])
def submit_tours_booking():
    data = request.get_json()
    user_id = session.get('user_id')
    # 提取并检查必要的字段
    tour_id = data.get("tour_id")
    departure_date = data.get("departure_date")
    adult_count = data.get("adult_count")
    child_count = data.get("child_count")
    contact_name = data.get("contact_name")
    contact_phone = data.get("contact_phone")
    travelers = data.get("travelers")

    # 验证 departure_date 是否存在和正确
    if not departure_date:
        return jsonify(success=False, message="Departure date is missing."), 400

    try:
        # 将 departure_date 字符串转换为日期格式
        departure_datetime = datetime.strptime(departure_date + " 10:00", '%Y-%m-%d %H:%M')
    except ValueError:
        return jsonify(success=False, message="Invalid departure date format."), 400

    # 创建并保存预订记录
    try:
        new_booking = models.ToursBooking(
            tour_id=tour_id,
            departure_date=departure_datetime,
            adult_count=adult_count,
            child_count=child_count,
            contact_name=contact_name,
            contact_phone=contact_phone,
            message=data.get("message", ""),
            created_at=datetime.now(),
            user_id=user_id
        )
        models.db.session.add(new_booking)
        models.db.session.commit()

        # 为每位游客创建记录
        for traveler in travelers:
            new_traveler = models.ToursBookingsTraveler(
                tours_booking_id=new_booking.booking_id,
                name=traveler["name"],
                nationality=traveler["nationality"],
                id_number=traveler["id_number"],
                phone=traveler["phone"]
            )
            models.db.session.add(new_traveler)

        models.db.session.commit()
        return jsonify(success=True)

    except Exception as e:
        print(f"Error saving booking: {e}")
        models.db.session.rollback()
        return jsonify(success=False, message=str(e))


# 评论导游
@app.route("/submit_guide_review", methods=["POST"])
def submit_guide_review():
    guide_id = request.form.get("guide_id")
    user_id = request.form.get("user_id")
    rating = request.form.get("rating")
    content = request.form.get("content")

    # 创建并保存新的导游评论
    review = models.TourGuidesReview(guide_id=guide_id, user_id=user_id, rating=rating, content=content)

    try:
        db.session.add(review)
        db.session.commit()
        flash("评价提交成功！", "success")
    except Exception as e:
        db.session.rollback()
        flash("评价提交失败，请重试。", "error")
        print(f"Error saving guide review: {e}")

    return redirect(url_for("user_profile", user_id=user_id))


@app.route("/submit_catering_review", methods=["POST"])
def submit_catering_review():
    catering_id = request.form.get("catering_id")
    user_id = request.form.get("user_id")
    rating = request.form.get("rating")
    content = request.form.get("content")

    # 创建并保存新的餐饮评价
    review = models.CateringReview(catering_id=catering_id, user_id=user_id, rating=rating, content=content)

    try:
        db.session.add(review)
        db.session.commit()
        flash("评价提交成功！", "success")
    except Exception as e:
        db.session.rollback()
        flash("评价提交失败，请重试。", "error")
        print(f"Error saving catering review: {e}")

    return redirect(url_for("user_profile", user_id=user_id))


@app.route("/submit_hotel_review", methods=["POST"])
def submit_hotel_review():
    hotel_id = request.form.get("hotel_id")
    user_id = request.form.get("user_id")
    rating = request.form.get("rating")
    content = request.form.get("content")

    # 创建并保存新的酒店评价
    review = models.HotelReviews(hotel_id=hotel_id, user_id=user_id, rating=rating, content=content)

    try:
        db.session.add(review)
        db.session.commit()
        flash("评价提交成功！", "success")
    except Exception as e:
        db.session.rollback()
        flash("评价提交失败，请重试。", "error")
        print(f"Error saving hotel review: {e}")
    return redirect(url_for("user_profile", user_id=user_id))


@app.route("/submit_tour_review", methods=["POST"])
def submit_tour_review():
    tour_id = request.form.get("tour_id")
    user_id = request.form.get("user_id")
    rating = request.form.get("rating")
    content = request.form.get("content")

    # 创建并保存新的旅游评价
    review = models.ToursReview(tour_id=tour_id, user_id=user_id, rating=rating, content=content)

    try:
        db.session.add(review)
        db.session.commit()
        flash("评价提交成功！", "success")
    except Exception as e:
        db.session.rollback()
        flash("评价提交失败，请重试。", "error")
        print(f"Error saving tour review: {e}")

    return redirect(url_for("user_profile", user_id=user_id))


if __name__ == '__main__':
    app.run(port=5001,debug=True)
