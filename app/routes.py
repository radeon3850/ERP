# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime, timedelta
from flask import flash, redirect, url_for, request, g, send_file, jsonify, session
from flask import render_template
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import desc
from werkzeug.urls import url_parse
from app import app, db, errors
from app.forms import LoginForm, RegistrationForm, AddClient, AddOrder, AddWork, AddWorker, UploadForm, \
    AddStone, KanbanEvents, KanbanEventsChange, ChangeLoginPasswordForm
from app.models import User, Clients, OrderClient, PreProduct, Works, SlabWorks, PartWorks, UploadFile, PerformanceWork, \
    TimeWork, Post, Transit, ListOrderStone, Stone, StatisticsUser, ProblemWork
from mymodul.price_calculate_work import calculate_price_work
from flask_wtf.csrf import generate_csrf
from mymodul.add_db_data import add_data
from mymodul.progres import progres
import re

# this functiom is called JS function to show swetalert
def show_notification(message, notification_type):
    return jsonify({'message': message, 'type': notification_type})

# this function set date-time now
def date_time_now():
    now_datetime = datetime.now()
    return now_datetime

access_list=['архитектор', 'начальник производства', 'главный менеджер', 'директор', 'менеджер']

# function is checked format of number for corrected save to data
def check_data(value):
    new_value=value.replace(" ", "")
    try:
        float_value = float(new_value)  # Спроба перетворення в число
        pattern = r'^\d+(\.\d+)?$'
        if re.match(pattern, value):
            correct_value = value.replace(",", ".")
            return correct_value
        else:
            return None

    except ValueError as e:
        print(e)
        return None

# main page
@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    current_page = "Основная панель"
    user_spec = current_user.specialization_id  # user specialization

    try:
        if user_spec == 2:
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('workplace')
            return redirect(next_page)

        online_user = User.query.filter_by(online=True).all()
        number_user_online = len(online_user)
        # get data  - orders whose work is in progress and not completed at the moment
        order_actiw_slabworks = OrderClient.query.join(SlabWorks).join(PerformanceWork)\
            .filter(PerformanceWork.status_start == True, PerformanceWork.status_end == None)\
            .order_by(OrderClient.id.desc()).all()
        order_actiw_partworks = OrderClient.query.join(PartWorks).join(PerformanceWork) \
            .filter(PerformanceWork.status_start == True, PerformanceWork.status_end == None)\
            .order_by(OrderClient.id.desc()).all()

        order_no_dublicate = list(set(order_actiw_slabworks + order_actiw_partworks)) # del dublicate if there and marge two list

        # get all works that performed this time, if status_start=Trut and status_end=None
        slab_works = SlabWorks.query.join(PerformanceWork).filter_by(status_start=True, status_end=None).all()
        part_works = PartWorks.query.join(PerformanceWork).filter_by(status_start=True, status_end=None).all()

        #create list work, that order is not close for slabs and part.
        not_close_order_slab = [i for i in slab_works if
                                i.order_client is not None and i.order_client.order_status != 'closed'
                                and not any(item.status_end for item in i.query_slabworks)] + \
                               [sl for sl in slab_works if sl.order_of_client == 0
                                and not any(item.status_end for item in sl.query_slabworks)]

        not_close_order_part = [i for i in part_works if
                                i.order_client is not None and i.order_client.order_status != 'closed'
                                and not any(item.status_end for item in i.query_partworks)] + \
                               [prt for prt in part_works if prt.order_of_client == 0
                                and not any(item.status_end for item in prt.query_partworks)]

        # cancat lists all work if order_client not closed and status end is None
        list_active_work = not_close_order_slab + not_close_order_part

        number_orders_inprogres = len(order_no_dublicate)
        number_works = len(list_active_work)

    except Exception as error: return f'An error occured {str(error)}', 500

    return render_template('index.html', title='Главная', current_page=current_page,
                           client_order=order_no_dublicate, list_active_work=list_active_work,
                           number_order=number_orders_inprogres, number_works=number_works, online_user=online_user,
                           number_user_online=number_user_online)


@app.route('/orders')
@login_required
def orders():
    # checking whether access is allowed to the user
    if current_user.employee.job_title in access_list:
        current_page = 'Заказы'  # name to display on the page
        client_order = OrderClient.query.order_by(OrderClient.id.desc()).all()  # get all order client

        files = UploadFile.query.all()  # send all files to view on page
        datetime_now = date_time_now()  # set date_time now
        stone_list = ListOrderStone.query.all()

        return render_template('orders.html', title='Заказы', client_order=client_order, current_page=current_page,
                               datetime_now=datetime_now, files=files, stone_list=stone_list)
    else:
        return render_template('error_access.html')

# function for validation users
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            user.ping()  # Ця функція встановлює час останнього входу користувача в додаток
            user.online = True
            db.session.commit()

            # Перевірка пароля
            if user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash('Вход выполнен успешно', 'info')

                # Перенаправлення на наступну сторінку або на головну сторінку
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('index')
                return redirect(next_page)
        else:
            flash('Неверный логин или пароль проверьте правильность вводимых данных', 'error')

    return render_template('login.html', title='Вход', form=form)

# this function check how much time has passed since the user logged in
@app.before_request
def check_session_timeout():
    if current_user.is_authenticated:
        get_data_user = User.query.filter_by(id=current_user.id).first()
        get_time = get_data_user.last_seen

        if datetime.now() - get_time > app.config['PERMANENT_SESSION_LIFETIME']:
            # logout if time more 11 hours from time that users is login
            logout_user()
            flash('Сесія завершена через неактивність', 'warning')
    # this code is check all users and set status for field 'online' is False
    all_users = User.query.all() # get list of all users
    # iterate list ofusers and set for all users status False if PERMANENT_SESSION_LIFETIME more than
    for user in all_users:
        if user.last_seen is not None and datetime.now()\
                - user.last_seen > app.config['PERMANENT_SESSION_LIFETIME']:
            user.online = False
            db.session.commit()


# function logut
@app.route('/logout')
@login_required
def logout():
    user = current_user
    user.online = False
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))


# function for register user
@app.route('/register', methods=['GET', 'POST'])
def register():
    # checking whether access is allowed to the user
    if current_user.employee.job_title in access_list:
        current_page = 'Регистрация'
        # check if user is authenticated redirect page home (index) or register users if form is validate
        # if current_user.is_authenticated:
        #     return redirect(url_for('index'))
        form = RegistrationForm()
        if form.validate_on_submit():  # validation form
            # great instance of the class User
            user = User(username=form.username.data, phone=form.phone.data,
                        first_name=form.first_name.data, last_name=form.last_name.data,
                        specialization_id=form.specialization_id.data)
            user.set_password(form.password.data)
            add_data(user) # this function is added data to db Users
            flash('Новый пользователь зарегистрирован', 'info')
            return redirect(url_for('login'))  # open page login for autentification
        return render_template('register.html', title='Регистрация', form=form, current_page=current_page)

    else: return render_template('error_access.html')

@app.route('/change_login_password', methods=['GET', 'POST'])
@login_required
def change_login_password():
    current_page = 'Изменить логин/пароль'
    form = ChangeLoginPasswordForm()
    if form.validate_on_submit():
        if form.username.data:
            current_user.username = form.username.data
        if form.password.data:
            current_user.set_password(form.password.data)
        db.session.commit()
        flash('Ваш логин/пароль был изменён', 'info')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('change_login_password.html', title='Изменение логина/пароля', form=form, current_page=current_page)

@app.route('/profile')
@login_required
def profile():
    current_page = 'Личный профиль'

    def weekdays():
        today = date_time_now()
        day_of_week = today.weekday() # week_day - 0 - Monday, 1 - Tuesday ... 6 - Sunday
        return day_of_week

    try:
        get_all_statistic = StatisticsUser.query.filter_by(id_user=current_user.id).all() # data from table statistics_user
        # create date for start period and end period
        period_start = (datetime.now() - timedelta(days=weekdays())).date()
        period_end = (datetime.now() + timedelta(days= (6-weekdays()))).date()

        # Get data from all works table Slabworks, Preproduct, Partworks.We used filter timedelta (from data start), status_starr=None, if currennt_user.id == user.id from work table who have to do a task.
        preproduct_with_status_none = PreProduct.query.join(PerformanceWork,
                                                            PreProduct.id == PerformanceWork.id_preproduct) \
            .filter(PerformanceWork.status_start == None, PreProduct.set_worker == current_user.id,
                    db.func.date(PreProduct.start_work_date) >= period_start,
                    db.func.date(PreProduct.start_work_date) >= period_start).all()
        slabworks_with_status_none = SlabWorks.query.join(PerformanceWork,
                                                          SlabWorks.id == PerformanceWork.id_work_slabs) \
            .filter(PerformanceWork.status_start == None, SlabWorks.set_worker == current_user.id,
                    db.func.date(SlabWorks.start_work_date) <= period_end,
                    db.func.date(SlabWorks.start_work_date) >= period_start).all()
        partworks_with_status_none = PartWorks.query.join(PerformanceWork, PartWorks.id == PerformanceWork.id_work_part) \
            .filter(PerformanceWork.status_start == None, PartWorks.set_worker == current_user.id,
                    db.func.date(PartWorks.start_work_date) <= period_end,
                    db.func.date(PartWorks.start_work_date) >= period_start).all()

        # create list events for the time_line on the page
        events = []
        # iterate list that we get from Table Class Preproduct
        for event in preproduct_with_status_none:
            if event.order_client:
                if event.order_client.order_status !="closed":
                    event_data = {
                        'amount': f'{event.work.work_title}',
                        'title': f'{event.work.work_type}',
                        'type': '',
                        'date': f'{event.start_work_date.isoformat()}',
                        'description': f'{event.work.work_type}'
                    }
                    events.append(event_data)  # add  data to list
            else:
                event_data = {
                    'amount': f'{event.work.work_title}',
                    'title': f'{event.work.work_type}',
                    'type': '',
                    'date': f'{event.start_work_date.isoformat()}',
                    'description': f'{event.work.work_type}'
                }
                events.append(event_data)  # add  data to list

        # iterate list that we get from Table Class Slabworks
        for event in slabworks_with_status_none:
            if event.order_client:
                if event.order_client.order_status != "closed":
                    event_data = {
                        'amount': f'{event.work_set.work_title}',
                        'title': f'{event.work_set.work_type}',
                        'type': f'{event.work_set.work_kind}',
                        'date': f'{event.start_work_date.isoformat()}',
                        'description': f'{event.work_set.work_type}'
                    }
                    events.append(event_data)
            else:
                event_data = {
                    'amount': f'{event.work_set.work_title}',
                    'title': f'{event.work_set.work_type}',
                    'type': f'{event.work_set.work_kind}',
                    'date': f'{event.start_work_date.isoformat()}',
                    'description': f'{event.work_set.work_type}'
                }
                events.append(event_data)

        # iterate list that we get from Table Class Parts
        for event in partworks_with_status_none:
            if event.order_client:
                if event.order_client.order_status != "closed":
                    event_data = {
                        'amount': f'{event.work_set_part.work_title}',
                        'title': f'{event.work_set_part.work_type}',
                        'type': f'{event.work_set_part.work_kind}',
                        'date': f'{event.start_work_date.isoformat()}',
                        'description': f'{event.work_set_part.work_type}'
                    }
                    events.append(event_data)  # add  data to list
            else:
                event_data = {
                    'amount': f'{event.work_set_part.work_title}',
                    'title': f'{event.work_set_part.work_type}',
                    'type': f'{event.work_set_part.work_kind}',
                    'date': f'{event.start_work_date.isoformat()}',
                    'description': f'{event.work_set_part.work_type}'
                }
                events.append(event_data)  # add  data to list
    except Exception as error:
        return f'An error: {str(error)}', 400
    return render_template('profile.html', all_statistic=get_all_statistic,title='Мой профиль' , current_page=current_page, events=events)


@app.route('/add_order', methods=['GET', 'POST'])
@login_required
def add_order():
    # checking whether access is allowed to the user
    if current_user.employee.job_title in access_list:
        current_page = "Добавить заказ"  # to display on the page

        form_add_client = AddClient()  # creat instans of the class form  AddClient
        if 'first_name' in request.form:  # Chesk that flask-form (AddClient) from add_order send data
            if request.method == "POST" and form_add_client.is_submitted():
                # creat instance class Clients model with atribut
                client = Clients(first_name=form_add_client.first_name.data, last_name=form_add_client.last_name.data,
                                 phone_number=form_add_client.phone.data)  # geta form AddClient
                add_data(self=client)  # connect to data base and add data to DB
                return redirect(url_for('add_order'))

        form = AddOrder()  # creat instance of class form AddOrder
        form.client_id.choices = [('0', 'Выбрать из списка')] + [
            (client.id, " ".join((client.first_name, client.last_name, client.phone_number))) for
            client in (db.session.query(Clients).all())]  # update data from table Client for choices flask-form (AddOrder)

        if 'name_order' in request.form:  # Chesk that flask-form (AddOrder) from add_order send data
            if form.validate_on_submit():
                if form.deadline.data > datetime.now().date() or form.client_id.data != "0":  # check if date is not set
                    # create instance of OrderClient class model for add data to BD
                    client_order = OrderClient(clients_id=form.client_id.data, title_order=form.name_order.data,
                                               # получение данных c формы AddOrder для добавления в базу данных
                                               object_description=form.object_description.data, address=form.address.data,
                                               deadline=form.deadline.data, measurements=form.checkbox_measurements.data,
                                               project_drawing=form.checkbox_blueprint.data, control=1, date_time=date_time_now())

                    add_data(self=client_order)  # add data to table OrderClient
                    flash('Заказ покупателя добавлен', 'info')

                    # check - if fields of form (checkbox_measurements,checkbox_blueprint, checkbox_control) sends True
                    # save data to database
                    if form.checkbox_measurements.data == True:
                        order_client = (db.session.query(OrderClient).order_by(OrderClient.id.desc()).first_or_404()).id
                        work = Works.query.get(115).id

                        work_staf = PreProduct(order_of_client=order_client, work_type=work)
                        add_data(self=work_staf)

                        # add id_Preproduct to Table PerformanceWork
                        get_id_preproduct = PreProduct.query.filter_by(order_of_client=order_client, work_type=work).first_or_404()
                        add_id_to_performance_work = PerformanceWork(id_preproduct=get_id_preproduct.id, date_time=date_time_now())
                        add_data(self=add_id_to_performance_work)
                    # check if form include checkbox_blueprint and check-box is true, we add this work to table Preproduct
                    if form.checkbox_blueprint.data == True:
                        order_client = (db.session.query(OrderClient).order_by(OrderClient.id.desc()).first_or_404()).id
                        work = Works.query.get(116).id

                        work_staf = PreProduct(order_of_client=order_client, work_type=work, date_time=date_time_now())
                        add_data(self=work_staf)

                        # add id_Preproduct to Table PerformanceWork
                        get_id_preproduct = PreProduct.query.filter_by(order_of_client=order_client, work_type=work).first_or_404()
                        add_id_to_performance_work = PerformanceWork(
                            id_preproduct=get_id_preproduct.id)  # instance class PreProduct with atribut
                        add_data(
                            self=add_id_to_performance_work)  # function call "add_data" and send instance class PreProduct model to data
                    # this code always add work "control" to DB during class instance creation OrderClient
                    order_client = (db.session.query(OrderClient).order_by(OrderClient.id.desc()).first_or_404()).id
                    work = Works.query.get(117).id
                    work_staf = PreProduct(order_of_client=order_client,
                                           work_type=work, date_time=date_time_now())  # creat instance class PreProduct for work control
                    add_data(self=work_staf)  # function call "add_data" and send instance class PreProduct model to data

                    # add id_Preproduct to Table PerformanceWork
                    get_id_preproduct = PreProduct.query.filter_by(order_of_client=order_client, work_type=work).first_or_404()
                    add_id_to_performance_work = PerformanceWork(id_preproduct=get_id_preproduct.id, date_time=date_time_now())
                    add_data(self=add_id_to_performance_work)
                    return redirect(url_for('orders'))
                else:
                    flash('Заказ не отправлен - проверьте поля формы', 'error')
        return render_template("add_order.html", title='Создание заказа клиента', form=form,
                               form_add_client=form_add_client, current_page=current_page)
    else:
        return render_template('error_access.html')


@app.route('/kanban', methods=['GET', 'POST'])
@login_required
def kanban():
    # checking whether access is allowed to the user
    if current_user.employee.job_title in access_list:
        current_page = 'Kanban'  # send name to page "kanban" for display
        workers = User.query.all()  # get all users
        preproduct_works = PreProduct.query.order_by(PreProduct.id.desc()).all()  # All preproduct work
        slab_works = SlabWorks.query.order_by(SlabWorks.id.desc()).all()  # get all data
        part_works = PartWorks.query.order_by(PartWorks.id.desc()).all()  # get all part works
        all_orders_not_close = OrderClient.query.filter(OrderClient.order_status != 'closed').all()
        get_list_stone = Stone.query.all()
        add_worker_form = AddWorker()

        # form kanban events
        kanban_form = KanbanEvents()
        kanban_form_change = KanbanEventsChange()
        kanban_form.order_client.choices = [(0, 'Номер заказа')] + [(order.id, order.id) for order in
                                                                    all_orders_not_close]
        kanban_form.stone.choices = [(0, 'Выбрать камень')] + [(stone.id, stone.type_stone) for stone in
                                                               get_list_stone]

        if kanban_form.is_submitted() and request.method == 'POST' and kanban_form.stone.data:
            order_checkbox = kanban_form.order_checkbox.data
            order_client = kanban_form.order_client.data
            if order_checkbox == True:
                order_client = None

        # create lists works if works is not from order that is closed and status_end is None
        # not_close_order_preproduct = [i for i in preproduct_works if
        #                               i.order_client is not None and i.order_client.order_status != 'closed'
        #                               and not any(item.status_end for item in i.query_preproduct)]

        not_close_order_slab = [i for i in slab_works if
                                i.order_client is not None and i.order_client.order_status != 'closed'
                                and not any(item.status_end for item in i.query_slabworks)] + \
                               [sl for sl in slab_works if sl.order_of_client == 0
                                and not any(item.status_end for item in sl.query_slabworks)]

        not_close_order_part = [i for i in part_works if
                                i.order_client is not None and i.order_client.order_status != 'closed'
                                and not any(item.status_end for item in i.query_partworks)] + \
                               [prt for prt in part_works if prt.order_of_client == 0
                                and not any(item.status_end for item in prt.query_partworks)]

        # cancat lists all work if order_client not closed and status end is None
        lis_active_work = not_close_order_slab + not_close_order_part

        # create lists works if works is not from order that is closed and status_end is None
        list_finish_preproduct_work = [i for i in preproduct_works if any(item.status_end for item in i.query_preproduct)]
        list_finish_slab_work = [i for i in slab_works if any(item.status_end for item in i.query_slabworks)]
        list_finish_part_work = [i for i in part_works if any(item.status_end for item in i.query_partworks)]
        # cancat lists all work if order_client not closed and status end is None
        lis_finish_work = list_finish_preproduct_work + list_finish_slab_work + list_finish_part_work

        # check if condition is true  - if form validate and request method is "POST" we get data from form
        if add_worker_form.submit() and request.method == "POST" and add_worker_form.set_worker.data:
            get_str_table = request.form.get('value1')  # get data from page
            get_id_works_table = request.form.get('value2')  # get data from page

            # check what type work (from table) we get for set worker and dates
            try:
                if 'preproduct' in get_str_table:
                    # set order_status is "work" if we set worker for work from table PreProduct
                    get_order_id = PreProduct.query.get(get_id_works_table).order_of_client
                    order_client = OrderClient.query.get(get_order_id)
                    if order_client.order_status == None:
                        order_client.order_status = 'work'  # set status for order of client
                    get_work_from_db = PreProduct.query.get(get_id_works_table)  # get row from table pre_product of DB
                    get_work_from_db.set_worker = add_worker_form.set_worker.data  # assign a worker who will perform the work
                    get_work_from_db.start_work_date = add_worker_form.start_date.data  # set date of starts work
                    get_work_from_db.end_work_date = add_worker_form.end_date.data  # set date of end work
                    db.session.commit()  # save changes to db for table preproduct
                # check if slab_works in list how returned after get data
                if 'slab_works' in get_str_table:
                    get_work_from_db = SlabWorks.query.get(get_id_works_table)  # get row from table slab_works
                    get_work_from_db.set_worker = add_worker_form.set_worker.data  # assign a worker who will perform the work
                    get_work_from_db.start_work_date = add_worker_form.start_date.data  # set date when work should be started
                    get_work_from_db.end_work_date = add_worker_form.end_date.data  # set date when the work should be ended
                    db.session.commit()  # save changes to db for table Slabworks
                # chech if part_works in list how returned after get data
                if 'part_works' in get_str_table:
                    get_work_from_db = PartWorks.query.get(get_id_works_table)  # get row from table part_works
                    get_work_from_db.set_worker = add_worker_form.set_worker.data  # assign a worker who will perform the work
                    get_work_from_db.start_work_date = add_worker_form.start_date.data  # set data when work should be started
                    get_work_from_db.end_work_date = add_worker_form.end_date.data  # set data when works should be ended
                    db.session.commit()
            except Exception as error:
                db.session.rollback()  # Відміна змін у разі помилки
                return f'An error occurred: {str(error)}', 500
        return render_template("kanban.html", title='Kanban', workers=workers, lis_active_work=lis_active_work,
                               lis_work_end_true=lis_finish_work, current_page=current_page,
                               add_worker_form=add_worker_form, kanban_form=kanban_form,
                               kanban_form_change=kanban_form_change)
    else: return render_template('error_access.html')


@app.route('/workplace', methods=['GET', 'POST'])
@login_required
def workplace():
    current_page = 'Workplace'

    performance_work = PerformanceWork.query.order_by(PerformanceWork.id).filter_by(
        status_end=None).all()  # get all performance work
    finish_performance_work = PerformanceWork.query.order_by(PerformanceWork.id).filter_by(status_start=True,status_end=True).all()  # get all works if finish
    list_not_close_order = []  # create empty list
    # append work in list_not_close_order if order is not closed
    for work in performance_work:
        # add work to list if order is not close or order == 0 and r
        if work.id_preproduct:
            if work.query_preproduct.order_of_client == 0:
                list_not_close_order.append(work)
            if work.query_preproduct.order_client and work.query_preproduct.order_client.order_status != 'closed':
                list_not_close_order.append(work)

        if work.id_work_slabs:
            if work.query_slabworks.order_of_client == 0:
                list_not_close_order.append(work)
            if work.query_slabworks.order_client and work.query_slabworks.order_client.order_status != 'closed':
                list_not_close_order.append(work)

        if work.id_work_part:
            if work.query_partworks.order_of_client == 0:
                list_not_close_order.append(work)
            if work.query_partworks.order_client and work.query_partworks.order_client.order_status != 'closed':
                list_not_close_order.append(work)

    return render_template("workplace.html", title='Задания', performance_work=list_not_close_order,
                           current_page=current_page, finish_performance_work=finish_performance_work)


# работаем с шаблоном order_client.html
@app.route('/order_client', methods=['GET', 'POST'])
@login_required
def order_client():
    # checking whether access is allowed to the user
    if current_user.employee.job_title in access_list:
        # form = Checkbox()
        q = request.args.get('q')  # get data about Number of order_client from HTML after сlick on the button
        order_client = OrderClient.query.get(q)
        # preproduct_work = PreProduct.query.filter_by(order_of_client=q).all()
        user_add_preproduct = User.query.all()  # get all users
        current_page = "Заказ клиента"
        preproduct_id = request.args.get('work_id')  # get slab_id from html (js - param : slab_id)
        order_client_status = order_client.order_status  # get status order

        access_list_button = ['главный менеджер', 'начальник производства']  # this list contains user - for which functions are available that are limited to others

        if preproduct_id is not None:
            try:
                Transit.query.filter(Transit.user_id == current_user.id).delete()
                db.session.commit()  # save data
            except Exception as e:
                print("Error:", e)
                print('В базе отсутвует')

            # add some temporary data
            id_part = Transit(some_data=preproduct_id, user_id=current_user.id)
            add_data(self=id_part) # save data

        # Добавление коментария
        if request.method == 'POST' and request.json:  # проверка если "post" и содержит content
            content = request.json['content']  # получаем переданое значение - content
            coment = Post(body=content, user_id=current_user.id, order_id=q, date_time=date_time_now())  # создаём экземляр класа модели Post
            add_data(self=coment) # save data
            return jsonify({'success': True})  # return result


        # Присваиваем ответсвенного предроектных работ с проверкой
        try:
            set_worker_form = AddWorker()  # передаём форму
            if 'set_worker' in request.form:
                if set_worker_form.validate_on_submit():  # validate form
                    get_id_work = Transit.query.filter_by(user_id=current_user.id).first_or_404()  # get work id
                    get_id_preproduct_work = PreProduct.query.filter_by(id=get_id_work.some_data).first_or_404()  # get id preproduct

                    # assign values to fields
                    get_id_preproduct_work.set_worker = set_worker_form.set_worker.data  # присваиваем исполнителя работ "предпроектные работы"
                    get_id_preproduct_work.start_work_date = set_worker_form.start_date.data
                    get_id_preproduct_work.end_work_date = set_worker_form.end_date.data

                    # установка статуса для заказа если статус не установлен
                    if order_client_status == None:
                        order_client.order_status = 'work'

                    # commit DB
                    db.session.commit()
                    # delete row from DB table Transit
                    get_row_del = Transit.query.filter_by(user_id=current_user.id).first_or_404()  # get row
                    if get_row_del is not None:  # check if Not None
                        db.session.delete(get_row_del)  # del row
                        db.session.commit()
        except Exception as error:
            db.session.rollback()
            return f'An error occurred: {str(error)}', 500

        slab = SlabWorks.query.filter_by(order_of_client=q).all()  # get all wors of slab
        preproduct_work = PreProduct.query.filter_by(order_of_client=q).all()  # get all preproduc work
        parts = PartWorks.query.filter_by(order_of_client=q).all()  # get all works of part
        files = UploadFile.query.filter_by(order_client_id=q).all()  # get all files to show on the page
        posts = Post.query.filter_by(order_id=q).all()  # get list of posts
        stone_form = AddStone()
        all_stone_this_order = ListOrderStone.query.filter_by(
            order_of_client=q).all()  # get all stone for this order_client

        csrf_token = generate_csrf()

        return render_template("order_client.html", title="Заказ клиента",csrf_token=csrf_token, order_client=order_client,
                               set_worker_form=set_worker_form,
                               user_add_preproduct=user_add_preproduct, slab=slab,
                               preproduct_work=preproduct_work, parts=parts, files=files, posts=posts, order=q,
                               current_page=current_page, stone_form=stone_form, stone_lits_orders=all_stone_this_order, access=access_list_button)
    else: return render_template('error_access.html')

# this function for added work of slabs/parts and assign responsibility
# for completing work within an order without going to the kanban page
@app.route('/managework', methods=['GET', 'POST'])
@login_required
def manage_work_order():
    # checking whether access is allowed to the user
    if current_user.employee.job_title in access_list:
        g.work_id = None
        g.s_p_data = None
        current_page = 'Управление работами заказа'
        user = User.query.all()
        q = request.args.get('q')  # get data about Number of order_client from HTML after сlick on the button
        order_client = OrderClient.query.get(q)  # get order client
        form = AddWork()  # class instance AddSlab
        button_data = request.args.get('work_id')  # get work_id from html (js - param : work_id) if we click button "Назначить"
        if button_data is not None:
            g.work_id = button_data[1:]
            g.s_p_data = button_data[0]

        slab = SlabWorks.query.filter_by(order_of_client=q).all()  # get all slabof this orderclient
        parts = PartWorks.query.filter_by(order_of_client=q).all()  # get list all work_parts equal this order_client

        get_list_stone = ListOrderStone.query.filter_by(order_of_client=q).all()  # get all stone for this order_client
        form.stone.choices = [(stone.id_stone, stone.query_stone.type_stone) for stone in
                              get_list_stone]  # send to flask-form list of choices

        access_list_button = ['главный менеджер', 'начальник производства'] # list of access

        # check dublicate
        def is_duplicate_slab(data_slab):
            existing_slab = SlabWorks.query.filter(
                SlabWorks.number_slab == data_slab.number_slab,
                SlabWorks.order_of_client == data_slab.order_of_client,
                SlabWorks.slab_works == data_slab.slab_works,
                SlabWorks.stone_id == data_slab.stone_id).first()
            return existing_slab is not None

        def is_duplicate_part(form_data_part):  # check if dublicate in DB
            existing_part = PartWorks.query.filter(
                PartWorks.number_part == form_data_part.number_part,
                PartWorks.order_of_client == form_data_part.order_of_client,
                PartWorks.part_works == form_data_part.part_works,
                PartWorks.stone_id == form_data_part.stone_id).first()  # compares if the form data and the data from the database are the same
            return existing_part is not None

        # add id_slab to DB table transit if on page we clicked button "Назначить" -
        # data aded to table Transit
        '''what data is aded to table transit: 
            - id-tabls (slab_work/part_work) in table - this is a some_data;
            - user_id - who is added this data to table'''
        if g.work_id is not None:
            # check if such data is missing  for deleted than return exception that "not defined in DB"
            try:
                Transit.query.filter(Transit.user_id == current_user.id).delete()  # del this data for this User (id)
                db.session.commit()  # connect db for del data
            except Exception as e:
                print("Error:", e)
                print('В базе отсутвует')

            id_data = Transit(some_data=g.work_id, user_id=current_user.id, s_p=g.s_p_data)  # creat class instance Transit
            add_data(self=id_data) # save data to DB

        # check if form returnted s_p_work=="Сляб" execute code to save data in table Slabworks

        if form.s_p_work.data == "Cляб":  # check if form include number_slab
            if form.is_submitted():  # if user send form to server (push button)
                check_correct_number = check_data(value=form.number_work.data) #create variable
                check_correct_value = check_data(value=form.value_work.data) #create variable

                #check if check_correct_number and check_correct_value is number
                if check_correct_number is not None and check_correct_value is not None:
                    print(" Its Work")
                    # creat class instance Slabworks for added data to DB
                    try:
                        data_slab = SlabWorks(number_slab=form.number_work.data, thickness=form.thickness.data,
                                              value=form.value_work.data, order_of_client=q,
                                              slab_works=form.work_subtype.data,
                                              set_worker=0, stone_id=form.stone.data,
                                              stone_name=form.name_stone.data, date_time=date_time_now())
                        # Check dublicate
                        if not is_duplicate_slab(data_slab):
                            add_data(self=data_slab) # add data DB SlabWorks and save to db
                            flash(f'Работа для сляба №{form.number_work.data} присвоена', 'info')

                            get_id_slab = SlabWorks.query.filter_by(order_of_client=q,
                                                                    slab_works=form.work_subtype.data,
                                                                    number_slab=form.number_work.data,
                                                                    stone_id=form.stone.data).first_or_404()  # get id slab

                            # add id_slab to table PeformanceWork
                            data_performance_work = PerformanceWork(id_work_slabs=get_id_slab.id, date_time=date_time_now())
                            add_data(self=data_performance_work) # add data_performance_work to Slabworks
                            if q != '0':
                                from mymodul.progres import progres  # import my modul progres for equals precent of progres
                                progres_order = progres(q)
                                get_order = OrderClient.query.get(q)
                                get_order.progres = progres_order
                                try:
                                    db.session.commit()
                                except Exception as error:
                                    db.session.rollback()
                                    return f'An error occurred: {str(error)}', 500

                            return redirect(url_for('manage_work_order', q=q, slab=slab))
                        else:
                            flash(f'Такая работа уже присвоена этому слябу', 'error')
                    except Exception as error:
                        return f'An error occurred: {str(error)}', 500
                else:
                    flash('Ошибка не верно введен "номер" сляба или "значение"', 'error')
            else:
                flash(f'Данные не добавлены! Проверьте правильность ввода данных в '
                      f'соответсвующие поля или соответствие вводимых данных полю формы', 'error')

        if form.s_p_work.data == "Деталь":  # check if list include "Деталь"
            if request.method == 'POST' and form.is_submitted():  # check validation
                check_correct_number = check_data(value=form.number_work.data)  # create variable
                check_correct_value = check_data(value=form.value_work.data)  # create variable

                # check if check_correct_number and check_correct_value is number
                if check_correct_number is not None and check_correct_value is not None:
                    try:
                        # create class instance Partworks model and assign value for atribut this class
                        form_data_part = PartWorks(number_part=form.number_work.data, thickness=form.thickness.data,
                                                   value=form.value_work.data, order_of_client=q,
                                                   part_works=form.work_subtype.data, set_worker=0,
                                                   stone_id=form.stone.data, date_time=date_time_now())

                        if not is_duplicate_part(form_data_part):  # check if table PartWorks and AddPart contains the same values
                            add_data(self=form_data_part) # add data to db
                            flash(f'Работа для детали № {form.number_work.data} добавлена к карте заказа',
                                  'info')  # if the code is executed successfully display flash_mesage

                            get_id_part = PartWorks.query.filter_by(order_of_client=q,
                                                                    part_works=form.work_subtype.data,
                                                                    number_part=form.number_work.data,
                                                                    stone_id=form.stone.data).first_or_404()  # get id part_works for added to table Performance_work
                            # add id_part to table PeformanceWork
                            data_performance_work = PerformanceWork(id_work_part=get_id_part.id, date_time=date_time_now())  # create class instance PerformanceWork
                            add_data(self=data_performance_work)
                            if q != '0':
                                from mymodul.progres import progres  # import my modul progres for equals precent of progres
                                progres_order = progres(q)
                                get_order = OrderClient.query.get(q)
                                get_order.progres = progres_order
                                try:
                                    db.session.commit()
                                except Exception as error:
                                    db.session.rollback()
                                    return f'An error occurred: {str(error)}', 500
                            return redirect(url_for('manage_work_order', q=q, parts=parts))
                        else:
                            flash('Такая работа уже присвоена детали', 'error')

                    except Exception as error:
                        return f'An error occurred: {str(error)}', 500
                else:
                    flash('Ошибка не верно введен "номер" детали или "значение"', 'error')
            else:
                flash(
                    f'Данные не добавлены! Проверьте правильность ввода данных в соответсвующие поля или соответствие вводимых данных полю формы',
                    'error')
                return redirect(url_for('manage_work_order', q=q, slab=slab))

        set_worker_form = AddWorker()  # greate class instance flask-form AddWorker
        if 'set_worker' in request.form:  # if form include "set_worker"
            try:
                if set_worker_form.validate_on_submit():  # if form is validate
                    get_data_transit = Transit.query.filter_by(
                        user_id=current_user.id).first()  # get first data if current_user.id this user from table Transit
                    if get_data_transit.s_p == "S":
                        get_id_work = SlabWorks.query.filter_by(
                            id=get_data_transit.some_data).first()  # get a slab to which you need to assign a work contractor
                        status_work = PerformanceWork.query.filter_by(id_work_slabs=get_id_work.id).first()
                    else:
                        get_id_work = PartWorks.query.filter_by(
                            id=get_data_transit.some_data).first()  # get a slab to which you need to assign a work contractor
                        status_work = PerformanceWork.query.filter_by(id_work_part=get_id_work.id).first()
                    # assign values to fields

                    get_id_work.set_worker = set_worker_form.set_worker.data  # присваиваем исполнителя работ "слябы"
                    get_id_work.start_work_date = set_worker_form.start_date.data  # set date when strted work
                    get_id_work.end_work_date = set_worker_form.end_date.data  # set deadlinet for work

                    if status_work.status_start is None or status_work.status_pause == 1:
                        # save changes to db
                        db.session.commit()  # save data which we added
                        flash(f'Работник назначен', 'info')  # flash mesage after succses execute cod
                    else:
                        flash(
                            'Ошибка назначения - Назнчать cотрудника разрешено только для "Новых работ" или "Приостановленых"',
                            'error')
                    return redirect(url_for('manage_work_order', q=q, slab=slab))

            except Exception as error:
                return f'An error : {str(error)}', 400

        return render_template("manage_work_order.html", title='Управление работами заказа', user=user, order_client=order_client,
                               slab=slab, form=form, set_worker_form=set_worker_form, current_page=current_page,
                               access=access_list_button, parts=parts)
    else:
        return render_template('error_access.html')

# this function is load file from users and save files to folder, and path of files added to DB
@app.route('/upload_file', methods=['GET', 'POST'])
@login_required
def upload_file():
    from mymodul.create_mini_image import create_thumbnail
    from mymodul.check_format import is_supported_image
    current_page = "Загрузка файлов"

    q = request.args.get('q')  # get id order_client
    form = UploadForm()  # create class instance UploadForm flask-form for download files
    if form.validate_on_submit():  # check if validate is true
        files = request.files.getlist('files')  # get list of files from form
        filenames = []  # create empty list
        file_paths = []  # create empty list
        for file in files:  # iterate list of "files"
            filename = file.filename  # get filename from request form
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # save file to folder
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # geth path to folder
            filenames.append(filename)  # add file_name to list filenames
            file_paths.append(file_path)  # add path to list file_paths
            # Create thumbnail if format is ok
            if is_supported_image(file_path):
                thumbnail_filename = 'thumb_' + filename  # Rename the thumbnail file (optional)
                thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER'], thumbnail_filename)
                create_thumbnail(file_path, thumbnail_path)
        for i in range(len(filenames)):  # iterated lenght of filenames and added filename and file_path to DB
            # create class instance UploadFile model for added data to DB table UploadFile
            f = UploadFile(filename=filenames[i], file_path=file_paths[i], user_id=current_user.id, order_client_id=q,
                           date_time=date_time_now())
            add_data(self=f)  # add path to db for files

        return f'Загружено {len(filenames)} файлов'

    files = UploadFile.query.filter_by(order_client_id=q).all()  # get list of all files to db
    return render_template('upload_file.html', form=form, files=files, title='Загрузка файлов',
                           current_page=current_page)


# a function that allows you to download a file from the server to the device does not return "html"
@app.route('/download/<filename>', methods=['GET', 'POST'])
@login_required
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # get path of folder for download data acros server
    return send_file(file_path, as_attachment=True)

# This function is designed to receive and send a thumbnail image of a file with the given name filename. It works for GET requests on a URL
@app.route('/thumbnail/<filename>')
def thumbnail(filename):
    # Отримайте шлях до міні-копії за допомогою імені файлу (filename)
    # Наприклад, якщо міні-копії зберігаються в окремій папці, то змініть код відповідно
    thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER'], 'thumb_' + filename) # get path of folder wehere is tfile thunb_ and show icon this image to page order_client
    return send_file(thumbnail_path, as_attachment=True)
# this function is get signal from page performance_work

# views function to delete files that will be downloads before
@app.route('/delete_file/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    response_data = {"success": False, "message": "Помилка видалення файлу"}

    file = UploadFile.query.get_or_404(file_id)  # Отримуємо файл з бази даних за його ідентифікатором
    if file.user_id == current_user.id:  # Перевірка, чи файл належить поточному користувачеві
        file_path = file.file_path
        print('file delited')
        if os.path.exists(file_path):  # Переконуємось, що файл існує перед видаленням
            os.remove(file_path)  # Видаляємо файл зі шляху
            try:
                db.session.delete(file)  # Видаляємо запис з бази даних
                db.session.commit()
                response_data["success"] = True
                response_data["message"] = "Файл був успішно видалений"
                # flash show_notification("Файл был удалён с базы данных", 'info')
            except Exception as e:
                db.session.rollback()  # Відміна всіх змін у сесії, які не були збережені
                print("Во времмя удаления файла произошла ошибка:", str(e))
            # flash('Файл був видалений', 'info')
    else:
        response_data["message"] = "У вас немає прав на видалення цього файлу"
    return jsonify(response_data)

@app.route('/making_product', methods=['GET', 'POST'])
@login_required
def making_product():
    # all requests regarding production process control using AJAX and JS
    current_page = 'Управление заданием'  # send this page name to display on page
    q = request.args.get('q')  # get id work from table performanse work
    order = request.args.get('order')  # get id order
    signal = request.args.get('signal')  # get signal from users after pushed buttom
    work = PerformanceWork.query.get(q)  # get data id=q
    get_status_solved = ProblemWork.query.filter_by(id_performancework=q).order_by(desc(ProblemWork.id)).first()
    access_list = ['главный менеджер', 'начальник производства']  # list of access


    # create global varible assign id work if queru is not None
    g.get_works_id = None
    g.value_work = None
    if work.query_preproduct != None:
        g.get_works_id = work.query_preproduct.work.id
    if work.query_partworks != None:
        g.get_works_id = work.query_partworks.work_set_part.id
        g.value_work = work.query_partworks.value
    if work.query_slabworks != None:
        g.get_works_id = work.query_slabworks.work_set.id
        g.value_work = work.query_slabworks.value

    def check_status_order_status_apruved(oreder=order):
        get_apruved_status = OrderClient.query.get(oreder).order_apruved
        return get_apruved_status

    if request.method == 'POST':
        content = request.json['content']  # get from page data json 'content'
        order_id = request.json['value']  # get from page data json 'value'
        coment = Post(body=content, user_id=current_user.id, order_id=order_id, date_time=date_time_now())  # create classes instance Post model
        add_data(self=coment) # add coment to db
        return jsonify({'success': True})  # send response function for add content on the page (JS from chat.html)

    if signal == 'start':  # if signal from users start (click button "НАЧАТЬ")
        if (work.id_work_slabs!=None or work.id_work_part!=None) and order!='0':
            if check_status_order_status_apruved() is True:
                # if work.status_start is None and status_end_previous is True: # if work is not started "start"
                if work.status_start is None:  # if work is not started "start"
                    work.status_start = True  # asign (присвоить) "True" if pocess is not started
                    db.session.commit()
                    time_work = TimeWork(id_performance_work=q, start_date=date_time_now(),
                                         resume_date=date_time_now())  # create class instanse (экземпляр класса) TimeWork and asign value of atributs
                    # add data to table Timework
                    add_data(self=time_work)
                    return jsonify({'status': 'success', 'message': f"Виполняється: {date_time_now().strftime('%Y-%m-%d %H:%M:%S')}"})
                else:
                    return jsonify({'status': 'error', 'message': "Робота уже была начата"})  # alert (mesage) about error
            else: return jsonify({'status': 'error', 'message': "Заказ по которому присвоена работа, не был утверждён главным менеджером"}) # alert (mesage) about error

        # if work.status_start is None and status_end_previous is True: # if work is not started "start"
        else:
            if work.status_start is None:  # if work is not started "start"
                work.status_start = True  # asign (присвоить) "True" if pocess is not started
                db.session.commit()
                time_work = TimeWork(id_performance_work=q, start_date=date_time_now(),
                                     resume_date=date_time_now())  # create class instanse (экземпляр класса) TimeWork and asign value of atributs

                add_data(self=time_work)
                return jsonify({'status': 'success', 'message': f"Виполняється: {date_time_now().strftime('%Y-%m-%d %H:%M:%S')}"})
            else: return jsonify({'status': 'error', 'message': "Робота уже была начата"})  # alert (mesage) about error


    if signal == 'pause':  # if signal from users start (click button "ПРИОСТАНОВИТЬ")
        if PerformanceWork.query.get(q).status_start != None and PerformanceWork.query.get(
                q).status_pause != True and PerformanceWork.query.get(q).status_problem != True:
            PerformanceWork.query.get(q).status_pause = True  # if work is not pause asign atribut "status_start"  of Class PerformanceWork value=True

            db.session.commit() # save changes of status work "pause"

            lead_time = (date_time_now() - (TimeWork.query.filter_by(id_performance_work=q).all())[
                -1].resume_date).seconds / 3600  # this code calculates the time (часах) between the start of the execution of the work and pressing the pause
            time_work = TimeWork(id_performance_work=q, pause_date=date_time_now(), lead_time=lead_time,
                                 id_user=current_user.id)  # create class instance TimeWork model to add DB
            # add and save data to DB
            add_data(self=time_work)
            return jsonify({'status': 'success', 'message': "Приостановлено"})
        else:
            return jsonify({'status': 'error', 'message': "Работа не начата или выполнение работ уже приостановлено"})  # alert (mesage) about error

    # resum proces manufacture
    if signal == 'resume':
        change_status = PerformanceWork.query.get(q)  # get id works for setings status
        if change_status.status_start != None and (
                change_status.status_pause != None or change_status.status_problem != None):  # check if status_start=True and status_pause=True or status_problem = True
            # this block of code work if status_pause = True, and we set status_pause = False and save to DB
            if change_status.status_pause != None:
                PerformanceWork.query.get(q).status_pause = None
                db.session.commit()
                time_work = TimeWork(id_performance_work=q,
                                     resume_date=date_time_now())  # create class instanse Timework to added Table time when work is resume

                # add and save data to table TimeWork (DB)
                add_data(self=time_work)
                return jsonify({'status': 'success', 'message': "Производство возобновлено"})  # mesage about successfully (успешном) change status

                # this block of code work if status_problem = True, and we set status_problem = False and save to DB
            if change_status.status_problem != None:
                # get row with data from table (model ProblemWork) for checking of status "problem_solved"
                status_problemwork_solved = ProblemWork.query.filter_by(id_performancework=q)\
                    .order_by(desc(ProblemWork.id)).first_or_404()
                #check if problem_solveda is True we resume a work
                if status_problemwork_solved.problem_solved == True:
                    PerformanceWork.query.get(q).status_problem = None  # asign status_problem = False
                    status_problemwork_solved.resume_after_solved = True # asign resume_after_solved = True for table ProblemWork
                    db.session.commit()

                    time_work = TimeWork(id_performance_work=q,
                                         resume_date=date_time_now())  # create class instanse Timework to added Table time when work is resume
                    # add data to Timework
                    add_data(self=time_work)
                    return jsonify({'status': 'success', 'message': "Производство возобновлено"})  # mesage about successfully (успешном) change status

                else: return jsonify({'status': 'error',
                            'message': "Производство не может быть возобновлено, "
                                       "проблема не решена"})  # alert (mesage) about error
        else:
            return jsonify({'status': 'error',
                            'message': "Процес производства уже был возобновлён ранее, "
                                       "невозможно возобновить повторно"})  # alert (mesage) about error

    if signal == 'stop':
        # Закончить производство
        change_status = PerformanceWork.query.get(q)
        if change_status.status_start != None and (
                change_status.status_pause != True and change_status.status_end != True):
            PerformanceWork.query.get(q).status_end = True  # set for status_end - TRUE

            db.session.commit() #save changes  - status "stop"
            lead_time = ((date_time_now() - (TimeWork.query.filter_by(id_performance_work=q).all()[-1]).resume_date)).seconds / 3600

            # create class instance 'time_work' for added to BD table TimeWork
            time_work = TimeWork(id_performance_work=q, end_date=date_time_now(), lead_time=lead_time,
                                 id_user=current_user.id)
            # add data to TimeWork
            add_data(self=time_work)

            # this block is responsible for adding comments from users (этот блок отвечает за добавления коментария от пользователей)
            # function is import from mymodul.price_calculate_work
            get_all_time_work = TimeWork.query.filter_by(id_performance_work=q).all()
            all_time = sum([time.lead_time for time in get_all_time_work if
                            time.lead_time != None])  # получить все времмя по конкретной работе затраченное

            get_price = calculate_price_work(work)
            list_uniq_user_id = set([user.id_user for user in get_all_time_work if user.id_user != None])

            if len(list_uniq_user_id) > 1:
                user_list = []
                for user in get_all_time_work:
                    if user.id_user not in user_list and user.id_user != None:
                        user_list.append(user.id_user)

                for user in user_list:
                    get_time_work_user = TimeWork.query.filter_by(id_performance_work=q, id_user=f'{user}').all()
                    all_time_user = sum([time.lead_time for time in get_time_work_user if time.lead_time != None])
                    real_price = (float(all_time_user) / float(all_time)) * (get_price)

                    # crete class instance StatisticsUser for aded data that we get from customer page
                    add_data_statistic_user = StatisticsUser(id_user=user, all_time_work=all_time_user,
                                                             date_fact_end=date_time_now(), price_work=real_price,
                                                             id_works=g.get_works_id, value_work=g.value_work,
                                                             id_performance_work=q)

                    add_data(self=add_data_statistic_user) # function is save data to table StatisticsUser


            else:
                #crete class instance StatisticsUser for aded data that we get from customer page
                add_data_statistic_user = StatisticsUser(id_user=current_user.id, all_time_work=all_time,
                                                         date_fact_end=date_time_now(), price_work=get_price,
                                                         id_works=g.get_works_id, value_work=g.value_work,
                                                         id_performance_work=q)
                add_data(self=add_data_statistic_user)

            if order!= '0':
                from mymodul.progres import progres  # import my modul progres for equals precent of progres
                progres_order = progres(order)
                get_order = OrderClient.query.get(order)
                get_order.progres=progres_order
                try:
                    db.session.commit()
                except Exception as error:
                    db.session.rollback()
                    return f'An error occurred: {str(error)}', 500

            return jsonify({'status': 'success', 'message': "Производство завершено"})  # alert about finished works
        else:
            return jsonify({'status': 'error',
                            'message': "Производство уже было завершено или процес производства не был начат"}) # alert about error

    #     Проверка есть ли в get запросе 'problem' и проверка статуса
    if signal == 'problem':
        change_status = PerformanceWork.query.get(q)  # get id work for change status/

        if change_status.status_start != None and (
                change_status.status_problem != True and change_status.status_pause != True and
                change_status.status_end != True):
            # assign a new value (boolean) for status_problem
            change_status.status_problem = True
            # create an instance of the data model (table) class Problem Work
            data_problemwork_table = ProblemWork(id_performancework=change_status.id, problem_solved=False,
                                                 date_time=date_time_now())
            add_data(self=data_problemwork_table) # save date to DB

            lead_time = (date_time_now() - (TimeWork.query.filter_by(id_performance_work=q).all())[
                -1].resume_date).seconds / 3600  # this code calculates the time (часах) between the start of the execution of the work and pressing the pause

            time_work = TimeWork(id_performance_work=q, problem_date=date_time_now(), lead_time=lead_time,
                                 id_user=current_user.id)  # create class instanse and added data to DB table TimeWork

            add_data(self=time_work) # this function added data to TimeWork
            return jsonify({'status': 'success', 'message': "Уведомление о проблеме отправлено"})  # alert about finished works

        else:
            return jsonify({'status': 'error',
                            'message': 'Статус "проблема" уже установлен или процес производства не был начат'})  # alert about error

    files = UploadFile.query.filter_by(order_client_id=order).all()  # get all files to display on the page
    posts = Post.query.filter_by(order_id=order).all()  # get all posts to display on the page

    return render_template('making_product.html', work=work, posts=posts, title="Управление производством", files=files,
                           order=order, current_page=current_page, order_client=order, status_solved=get_status_solved, access=access_list)


# delete data from DB table order_client and related tables, delete order client
@app.route('/del_data', methods=['POST'])
@login_required
def del_data():
    try:
        order_client_id = request.form['order']
        slab = SlabWorks.query.filter_by(order_of_client=order_client_id).all()  # get all Slabworks
        parts = PartWorks.query.filter_by(order_of_client=order_client_id).all()  # get all partworks
    except Exception as ex:
        print('Key "order" is not defined')

    # check if name: q_or_cl in post we work withs order client
    if 'q_or_cl' in request.form:
        order_id = request.form['q_or_cl']  # get argument name:'q_or_cl'
        order = OrderClient.query.get(order_id)  # find row (order) in table "order_clients"
        try:
            db.session.delete(order)  # del data
            db.session.commit()
            flash(f'Заказ клиента № {order_id} удалён', 'error')
        except Exception as error:
            db.session.rollback()
            return f'An error occurred: {str(error)}', 500
        return redirect(url_for('orders'))

    if 'q_sl_id' in request.form:
        slab_id_get = request.form['q_sl_id']  # get id from page
        work_slab_del = SlabWorks.query.get(slab_id_get)  # get id slabworks

        try:
            db.session.delete(work_slab_del)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            return f'An error occurred: {str(error)}', 500
        try:
            progres_order = progres(order_client_id)
            get_order = OrderClient.query.get(order_client_id)  # get order client
            get_order.progres = progres_order

            db.session.commit()  # save data
        except Exception as error:
            db.session.rollback()
            return f'An error occurred: {str(error)}', 500

        flash(f'Работа для сляба № {work_slab_del.number_slab} удалена', 'error')

        return redirect(url_for('manage_work_order', q=order_client_id, parts=parts, slab=slab, title='Управление работами заказа'))

    # check include post "q_prt_id"
    if 'q_prt_id' in request.form:
        part_id_get = request.form['q_prt_id']  # get id_part from page
        work_part_del = PartWorks.query.get(part_id_get)
        print('Part')
        try:
            db.session.delete(work_part_del)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            return f'An error occurred: {str(error)}', 500

        try:
            progres_order = progres(order_client_id)
            get_order = OrderClient.query.get(order_client_id)  # get order client
            get_order.progres = progres_order

            db.session.commit()  # save data
        except Exception as error:
            db.session.rollback()
            return f'An error occurred: {str(error)}', 500

        flash(f'Работа для детали № {work_part_del.number_part} удалена', 'error')

        return redirect(url_for('manage_work_order', q=order_client_id, parts=parts, slab=slab, title='Управление работами заказа'))


# Check how mutch works is new or work is not started. Display count of work for this user (bell). Send count to JS function shows the number of jobs not started as a notification
# Эта функция отвечает за отображение количества присвоенных не начатых работ - калакольчик с красным уведомлением с цифрой сверху находится в "new_base_bootstrap"
@app.route('/check_job')
@login_required
def check_job():
    from sqlalchemy import or_
    from sqlalchemy.orm import subqueryload

    # request for find id from PreProduct, SlabWorks та PartWorks, де OrderClient.order_status != "closed"
    preproduct_subq = PreProduct.query.join(PreProduct.order_client).filter(
        OrderClient.order_status != "closed").with_entities(PreProduct.id)
    slabworks_subq = SlabWorks.query.join(SlabWorks.order_client).filter(
        OrderClient.order_status != "closed").with_entities(SlabWorks.id)
    partworks_subq = PartWorks.query.join(PartWorks.order_client).filter(
        OrderClient.order_status != "closed").with_entities(PartWorks.id)


    slab_list_work = SlabWorks.query.filter_by(order_of_client='0', set_worker=current_user.id).all()
    part_list_work = PartWorks.query.filter_by(order_of_client='0', set_worker=current_user.id).all()

    work_all_0_list = slab_list_work + part_list_work

    # Find PerformanceWork, that status_start=None and id_preproduct, id_work_slabs or id_work_part include in request
    jobs_start_none = PerformanceWork.query.filter(
        PerformanceWork.status_start.is_(None),
        or_(
            PerformanceWork.id_preproduct.in_(preproduct_subq),
            PerformanceWork.id_work_slabs.in_(slabworks_subq),
            PerformanceWork.id_work_part.in_(partworks_subq)
        )
    ).options(subqueryload(PerformanceWork.query_preproduct)).all()

    job_list = []  # create empty list
    # jobs_start_none = PerformanceWork.query.filter_by(
    #     status_start=None).all()  # get all works status_start=False (None)
    for jobs in jobs_start_none:
        # Check not None and avoid mistakes
        if jobs.query_slabworks != None:
            if jobs.query_slabworks.set_worker == current_user.id:  # check this work appointed user or not
                job_list.append(jobs)  # add job_list
        if jobs.query_partworks != None:
            if jobs.query_partworks.set_worker == current_user.id:  # check this work appointed user or not
                job_list.append(jobs)  # add job_list
        if jobs.query_preproduct != None:
            if jobs.query_preproduct.set_worker == current_user.id:  # check this work appointed user or not
                job_list.append(jobs)  # add job_list

    for work in work_all_0_list:
        if work.__class__ == SlabWorks:
           if work.query_slabworks:
               for i in work.query_slabworks:
                    if i.status_start is not True:
                        job_list.append(i)
        if work.__class__ == PartWorks:
            if work.query_partworks:
                for i in work.query_partworks:
                    if i.status_start is not True:
                        job_list.append(i)

    all_jobs = len(job_list)  # get len of list

    return f'{all_jobs}'  # send to JS for showt count works this user work_status=False


# function is get signal to close order client if all works of order is finished
@app.route('/order_finish_work', methods=['POST'])
@login_required
def order_finish_work():
    data = request.json  # get from page request json (ajax)
    order_client = data.get('q')
    chenge_status_order = OrderClient.query.get(order_client)
    chenge_status_order.order_status = 'closed'  # assign 'closed'
    try:
        db.session.commit()
    except Exception as error:
        db.session.rollback()  # Відміна змін у разі помилки
        return f'An error occurred: {str(error)}', 500
    return jsonify({'success': True})

# This function added status aproved (утверждение заказов для продолжения производсттва) to client_order
@app.route('/approved', methods=['GET', 'POST'])
@login_required
def approved():
    # Here we used 2 methods for changed status_aproved: POST used JS (ajax) to add data table and
    # GET used standart method send requests and get responce

    # used method send data JS (ajax)
    if request.json:
        data = request.json
        order_client = data.get('q')
        get_order_change = OrderClient.query.get(order_client)
        # Встановлення order_apruved=True та збереження у БД
        get_order_change.order_apruved = 1
        db.session.commit()
        return jsonify({'success': True})

    if request.method == "GET":
        order_client = request.args.get('q')
        get_order_change = OrderClient.query.get(order_client)
        # Встановлення order_apruved=True та збереження у БД
        get_order_change.order_apruved = 1
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()  # Відміна змін у разі помилки
            return f'An error occurred: {str(error)}', 500
        return redirect(url_for("orders"))


# function is add stone to db
@app.route('/add_stone', methods=['POST'])
@login_required
def add_stone():
    stone_form = AddStone()  # create class instance flask-form AddStone
    # get data from form
    if request.method == "POST" and stone_form.validate_on_submit():
        order_client_id = request.form['q']
        form_stone_id = request.form['stone']
        form_stone_name = request.form['stone_name']
        # create an instance of a class ListOrderStone and add data form
        data_list_stone_add = ListOrderStone(id_stone=form_stone_id, order_of_client=order_client_id,
                                             stone_name=form_stone_name, date_time=date_time_now())

        # function is checking dublicate stone in db
        def is_duplicate(data_list_stone_add):
            existing_stone = ListOrderStone.query.filter(
                ListOrderStone.id_stone == form_stone_id,
                ListOrderStone.order_of_client == order_client_id,
                ListOrderStone.stone_name == form_stone_name
            ).first()
            return existing_stone is not None

        # check if not dublicat
        if not is_duplicate(data_list_stone_add):
            # add and comit BD
            add_data(self=data_list_stone_add)
            flash(f'Камень: "{(Stone.query.get(form_stone_id)).type_stone}" добавлен к заказу', 'info')
        else:
            pass
            # flash('Такой камень уже добавлен к заказу', 'error')

    return redirect(url_for('order_client', q=order_client_id))


# the function receives data after selecting the name of the work and transfer list of type_works after chois title_work
@app.route('/get_work_types', methods=['POST'])
@login_required
def get_work_types():
    work_title = request.form.get('work_title')  # get choic from customer

    if work_title:
        # Виконання запиту до бази даних для отримання варіантів `work_type`
        data_second_column = Works.query.filter_by(work_title=work_title).with_entities(
            Works.work_type).distinct().all()  # get a list of work types for a certain work_title from DB
        choices_work_types = [(work.work_type, work.work_type) for work in
                              data_second_column]  # we pass a list of available types of work for a certain work_title

        return jsonify({'choices': choices_work_types})

    return jsonify({'choices': []})


# this function is the same as get_work_types, the difference is that we get the available list of work_subtype after the user selects work_title and work_title
@app.route('/get_work_subtypes', methods=['POST'])
@login_required
def get_work_subtypes():
    # get from page data (ajax function)
    work_title = request.form.get('work_title')
    work_type = request.form.get('work_type')

    if work_title and work_type:
        # Виконання запиту до бази даних для отримання варіантів `work_subtype` (database query to get a list of available work_subtypes values)
        data_third_column = Works.query.filter_by(work_title=work_title,
                                                  work_type=work_type).all()  # get all works if work_title= and work_type= (work_title and work_type is value that we get from page)
        choices_work_subtypes = [(work.id, work.work_kind) for work in data_third_column]  # list of available works
        return jsonify({'choices': choices_work_subtypes})

    return jsonify({'choices': []})


# add events to full calendar
@app.route('/get_events', methods=['POST', 'GET'])
@login_required
def get_events():
    try:
        get_work_preproduct_all = (PreProduct.query.filter_by(set_worker=current_user.id).all())
        get_work_slabworks_all = (SlabWorks.query.filter_by(set_worker=current_user.id).all())
        get_work_partworks_all = (PartWorks.query.filter_by(set_worker=current_user.id).all())

        event_list = []

        for event in get_work_preproduct_all:
            if event.start_work_date != None:
                event_data = {
                    'title': f'{event.work.work_type}',
                    'start': event.start_work_date.isoformat(),
                    'end': event.end_work_date.isoformat()
                }
                event_list.append(event_data)

        for event in get_work_slabworks_all:
            if event.start_work_date != None:
                event_data = {
                    'title': f'{event.work_set.work_type}',
                    'start': event.start_work_date.isoformat(),
                    'end': event.end_work_date.isoformat()
                }
                event_list.append(event_data)

        for event in get_work_partworks_all:
            if event.start_work_date != None:
                event_data = {
                    'title': f'{event.work_set_part.work_type}',
                    'start': event.start_work_date.isoformat(),
                    'end': event.end_work_date.isoformat()
                }
                event_list.append(event_data)

        events = event_list
        return jsonify(events)
    except Exception as error:
        return f'Not found {error}', 404


@app.route('/get_form_kanban', methods=['POST', 'GET'])
@login_required
def get_form_kanban():
    from mymodul.check_dublikate import is_duplicate_slab, is_duplicate_part
    from mymodul.add_db_data import add_data
    from mymodul.progres import progres

    try:
        data = request.get_json()
        stone = Stone.query.get(data['selectstone']).type_stone
        subtype_work = Works.query.get(data['selectworksubtype']).work_kind
        get_number_order = data['selectorder']
        get_sp = data['radiofieldwork']

        if get_number_order == "0":
            g.order = '0'
        else:
            g.order = get_number_order

        if get_sp == 'slab':
            sp = 'сляб'
        else:
            sp = 'деталь'

        # variable for send to DB table_data
        number_order = get_number_order
        number = data['number']
        stone_id = data['selectstone']
        stone_name = data['stonename']
        work_id = data['selectworksubtype']
        thickness = data['selectthickness']
        value = data['valuework']

        if thickness == '2 см':
            thickness = '2'
        if thickness == '3 см':
            thickness = '3'

        checked_value=check_data(value=value) # check if value is float or integer
        checked_number_value=check_data(value=number)

        # блок добавления в соответсвующую таблицу workslabs/workparts
        if get_sp == 'slab':
            if checked_value is not None and checked_number_value is not None:
                print(checked_value)
                print(checked_number_value)
                work_data = SlabWorks(order_of_client=number_order, number_slab=number, stone_id=stone_id,
                                      stone_name=stone_name, thickness=thickness, value=checked_value, set_worker=0,
                                      slab_works=work_id, date_time=date_time_now())
                if number_order != '0':
                    if not is_duplicate_slab(data_slab=work_data):
                        add_data(self=work_data)  # save data to table - before calling the function add_data(self=work_data)

                    else:
                        return jsonify({'status':'error', 'message': 'Найден дубликат'}), 400
                else:
                    add_data(
                        self=work_data)  # save data to table - before calling the function add_data(self=work_data)
            else:
                print("Ошибка - не верный формат данных")
                return jsonify({'status':'error', 'message': 'Не правильный формат числа'}), 400
        # this block of code add work assignment if get_sp == part, for table PartWorks

        if get_sp == 'part':
            if checked_value is not None and checked_number_value is not None:
                work_data = PartWorks(order_of_client=number_order, number_part=number, stone_id=stone_id,
                                      thickness=thickness, value=checked_value, part_works=work_id, set_worker=0,
                                      date_time=date_time_now())
                if number_order != '0':
                    if not is_duplicate_part(data_part=work_data):
                        add_data(self=work_data)
                        # this code call function progres from my moduk for calculate completion percentage all work this order
                    else:
                        return jsonify({'status':'error', 'message': 'Найден дубликат'}), 400
                else:
                    add_data(self=work_data)  # function add_data() from mymodul is save data to table
            else:
                print("Ошибка - не верный формат данных")
                return jsonify({'status':'error', 'message': 'Не правильный формат числа'}), 400


        # блок отвечающий за добавление в  таблицу performance_work
        if get_sp == 'slab':
            get_id = SlabWorks.query.filter_by(order_of_client=number_order, number_slab=number,
                                               stone_id=stone_id,
                                               stone_name=stone_name, thickness=thickness, value=checked_value,
                                               slab_works=work_id, set_worker=0).order_by(desc(SlabWorks.id)).first_or_404()
            performance_data = PerformanceWork(id_work_slabs=get_id.id, date_time=date_time_now())
            add_data(self=performance_data)

            # this code call function progres from my moduk for calculate completion percentage all work this order
            try:
                if number_order !='0':
                    progres_order = progres(number_order)
                    get_order = OrderClient.query.get(number_order)  # get order client
                    get_order.progres = progres_order
                    db.session.commit()  # save data

            except Exception as error:
                db.session.rollback()
                return f'An error occurred: {str(error)}', 500

        # check what table work add this works slab_works or part_works
        if get_sp == 'part':
            get_id = PartWorks.query.filter_by(order_of_client=number_order, number_part=number, stone_id=stone_id,
                                               thickness=thickness, value=checked_value, part_works=work_id,
                                               set_worker=0).order_by(desc(PartWorks.id)).first_or_404()
            performance_data = PerformanceWork(id_work_part=get_id.id, date_time=date_time_now())  # set id work how we are aded to table of work

            add_data(self=performance_data)  # save data to table

            try:
                if number_order != '0':
                    progres_order = progres(number_order)
                    get_order = OrderClient.query.get(number_order)  # get order client
                    get_order.progres = progres_order

                    db.session.commit()  # save data
            except Exception as error:
                db.session.rollback()
                return f'An error occurred: {str(error)}', 500

        # response data to page table in modal window from page "kanban" with form
        response_data = {
            'id_table_work': get_id.id,
            'sp': sp,
            'number': data['number'],
            'selectorder': g.order,
            'selectstone': stone,
            'stonename': data['stonename'],
            'selectworktitle': data['selectworktitle'],
            'selectworktype': data['selectworktype'],
            'selectworksubtype': subtype_work,
            'selectthickness': data['selectthickness'],
            'valuework': data['valuework']
        }
        # send response
        return jsonify(response_data)

    except Exception as e:
        print("Error:", e)
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/dell_data_kanban', methods=['POST'])
@login_required
def dell_data_kanban():
    from mymodul.progres import progres
    message_error = 'Ошибка удаления задания! Начат процес производства.'
    message_success = 'Задание успешно удалено.'

    try:
        data = request.json  # get data AJAX request to JSON (get data from ajax-request in formular JSON)
        # get data and set to variable
        get_table_name = data['workTable'] #get table (name) BD
        get_id_work = data['workId'] #get id work from

        if  get_table_name == 'preproduct':
            get_work_table_preproduct_works = PreProduct.query.get(get_id_work)
            id_work = get_work_table_preproduct_works.id
            get_status_start = PerformanceWork.query.filter_by(id_preproduct=id_work).first_or_404().status_start
            if get_work_table_preproduct_works is not None and get_status_start is None:

                db.session.delete(get_work_table_preproduct_works)
                db.session.commit()

        # this code get from customer signal - dell works from table slab_works and performanse work
        if get_table_name == 'сляб' or get_table_name == 'slabworks':
            get_work_table_slab_works = SlabWorks.query.get(get_id_work)
            get_orderclient_id = get_work_table_slab_works.order_of_client
            id_work = get_work_table_slab_works.id
            get_status_start = PerformanceWork.query.filter_by(id_work_slabs=id_work).first_or_404().status_start
            if get_work_table_slab_works is not None and get_status_start is None:
                try:
                    db.session.delete(get_work_table_slab_works)
                    db.session.commit()

                    # this code call function progres from my moduk for calculate completion percentage all work this order
                    if get_orderclient_id != 0:
                        progres_order = progres(get_orderclient_id)
                        get_order = OrderClient.query.get(get_orderclient_id)  # get order client

                        get_order.progres = progres_order
                        db.session.commit()  # save data to db

                        response = {'status': 'successfully', 'message': f'{message_success}'}
                        return jsonify(response), 200

                except Exception as error:
                    db.session.rollback()
                    response = {'status': 'error', 'message': 'Ошибка удаления задания из базы'}
                    return jsonify(response), 500

                response = {'status': 'successfully', 'message': f'{message_success}'}
                return jsonify(response), 200

            else:
                response = {'status': 'error', 'message': f'{message_error}'}
                return jsonify(response), 500


        if get_table_name == 'деталь' or get_table_name == 'partworks':
            get_work_table_part_works = PartWorks.query.get(get_id_work)
            get_orderclient_id = get_work_table_part_works.order_of_client
            id_work = get_work_table_part_works.id
            get_status_start = PerformanceWork.query.filter_by(id_work_part=id_work).first_or_404().status_start

            if get_work_table_part_works is not None and get_status_start is None:
                db.session.delete(get_work_table_part_works)
                db.session.commit()

                # this code call function progres from my moduk for calculate completion percentage all work this order
                try:
                    if get_orderclient_id!=0:
                        progres_order = progres(get_orderclient_id)
                        get_order = OrderClient.query.get(get_orderclient_id)  # get order client
                        get_order.progres = progres_order

                        db.session.commit()  # save data

                        response = {'status': 'successfully', 'message': f'{message_success}'}
                        return jsonify(response), 200

                except Exception as error:
                    db.session.rollback()
                    response = {'status': 'error', 'message': 'Ошибка удаления задания из базы.'}
                    return jsonify(response), 500

                response = {'status': 'successfully', 'message': f'{message_success}'}
                return jsonify(response), 200
            else:
                response = {'status': 'error', 'message': f'{message_error}'}
                return jsonify(response), 500

    except Exception as error:
        print(error)
        response = {'status': 'error', 'message': 'Ошибка удаления из базы! Задание отсутвует.'}
        return jsonify(response), 404


# функция фильтрует данные которые мы получаем с таблицы StatisticsUser
def filter_data_by_date(start_date, end_date):
    all_statistic_data = StatisticsUser.query.all()
    data = []
    g.filtered_data = None
    for value in all_statistic_data:
        statistict_dict = {
            "name": f'{value.query_user.first_name} {value.query_user.last_name}',
            "work_title": value.query_works.work_title,
            "work_type": value.query_works.work_type,
            "work_kind": value.query_works.work_kind,
            "value_work": value.value_work,
            "date": value.date_fact_end.strftime('%Y-%m-%d'),
            "costs": value.price_work
        }
        data.append(statistict_dict)

    if len(start_date)!=0 or len(end_date)!=0:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        g.filtered_data_date = [entry for entry in data if start <= datetime.strptime(entry["date"], "%Y-%m-%d") <= end]
        g.filtered_data = [entry for entry in g.filtered_data_date if entry["name"] == f'{current_user.first_name} {current_user.last_name}']
    return g.filtered_data

# отправка даты для фильтрации данных и отрпавки с сервера отфильтрованых на страницу
@app.route('/get_data_statistic_work', methods=['GET'])
@login_required
def get_data():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        filtered_data = filter_data_by_date(start_date, end_date)

        return jsonify(filtered_data)
    except Exception as error:
        return f'Not found {error}', 404


# this function is checked tasks of works than change color block <tr></tr> table canban if  work have status problem
@app.route('/get_task_statuses', methods = ['GET'])
def get_task_statuses():
    task_statuses = {} # create empty dictionary

    get_list_active_work = PerformanceWork.query.filter_by(status_problem="1").all() # get data table performance_work all row status_problem of them is True
    #aded data to dictionary
    for task in get_list_active_work:
        task_statuses[task.id] = True

    return jsonify(task_statuses)

@app.route('/edit_work', methods=['POST'])
@login_required
def edit_work():
    # Get data from page: id_work from table slab_works or part_works,
    # and work_type and work_type which means data table:slab_works or part_works
    work_id = request.form.get('work_id')
    work_type = request.form.get('work_type')
    #create global variables to be reassigned if conditions are met
    g.get_work = None
    g.work = None
    g.number = None
    g.stone_name = None
    g.worker = None
    g.start_work_date = None
    g.end_work_date = None

    # check what varible "work_type" is return - if "slabworks" reassigned global variable
    if work_type == 'slabworks':
        # A database query to retrieve job data
        g.work = SlabWorks.query.get(work_id) # get data id=veriable(work_id)
        g.get_work= Works.query.get(g.work.slab_works) #get data from table Works id=g.work.slab_works
        g.number = g.work.number_slab # get number of slab from table DB
        g.stone_name = g.work.stone_name # get stone title
        g.worker = g.work.set_worker # get worker - user_id who does the work
        if g.work.start_work_date and g.work.end_work_date:
            g.start_work_date = g.work.start_work_date.strftime("%Y-%m-%d") #get set start date
            g.end_work_date = g.work.end_work_date.strftime("%Y-%m-%d") #get set end date

    # check what varible "work_type" is return - if "partworks" reassigned global variable
    if work_type == 'partworks':
        g.work = PartWorks.query.get(work_id) # get data id=veriable(work_id)
        g.get_work = Works.query.get(g.work.part_works) #get data from table Works id=g.work.part_works
        g.number = g.work.number_part # get number of part from table DB
        g.worker = g.work.set_worker  # get worker - user_id who does the work
        if g.work.start_work_date and g.work.end_work_date:
            g.start_work_date = g.work.start_work_date.strftime("%Y-%m-%d") #get set start date
            g.end_work_date = g.work.end_work_date.strftime("%Y-%m-%d") #get set end date

    if g.work:
        # Return data is format JSON - page
        return jsonify({
            'number': g.number,
            'stone_id': g.work.stone_id,
            'stone_name': g.stone_name,
            'thickness': g.work.thickness,
            'value': g.work.value,
            'order_of_client': g.work.order_of_client,
            'work_title' : g.get_work.work_title,
            'work_type': g.get_work.work_type,
            'work_subtype': g.get_work.id,
            'worker': g.worker,
            'start_date': g.start_work_date,
            'end_date': g.end_work_date
        })
    else:
        # if work is not found return error 404
        return jsonify({'error': 'Work not found'}), 404


# this function receives edited data from page Kanban - modalWindow
@app.route('/update_work/<int:work_id>', methods=['POST'])
@login_required
def update_work(work_id):
    # get signal what table is change data and get json (form-data)
    work_type = request.form.get('work_type')
    updated_data = json.loads(request.form.get('updated_data'))
    g.work = None #create variable = None
    g.status_work_start = None
    g.status_work_pause = None

    #check what table we need for change data for slab or for part
    if work_type == 'slabworks':
        g.work = SlabWorks.query.get(work_id) #reassign the variable - create an instance of the class SlabWorks
        g.status_work_start = PerformanceWork.query.filter_by(id_work_slabs=g.work.id).first_or_404().status_start
        g.status_work_pause = PerformanceWork.query.filter_by(id_work_slabs=g.work.id).first_or_404().status_pause

        if g.work:
            g.work.stone_name = updated_data.get('stone_name', g.work.stone_name) # We assign a new value to "stone_name" (only works of slabs)
            g.work.slab_works = updated_data['work_subtype'] # We assign a new value to "slab_wokrs" table Slabworks

    elif work_type == 'partworks':
        g.work = PartWorks.query.get(work_id) # reassign the variable - create an instance of the class PartWorks
        g.work.part_works=updated_data['work_subtype'] # We assign a new value to "slab_wokrs" table PartWorks
        g.status_work_start = PerformanceWork.query.filter_by(id_work_part=g.work.id).first_or_404().status_start
        g.status_work_pause = PerformanceWork.query.filter_by(id_work_part=g.work.id).first_or_404().status_pause

    try:
        # get datime (type data - str) and make type data - ditetime
        start_date = datetime.strptime(updated_data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(updated_data['end_date'], '%Y-%m-%d')

        # We check that start_date cannot be less than today's date and end_date cannot be less than start_date
        if start_date >= date_time_now() or end_date >= start_date:
            g.work.start_work_date = start_date
            g.work.end_work_date = end_date
        else:
            return jsonify({'error': 'Не верно указана дата'}), 500
    except Exception as e:
        print(f'{e} Даты не установлены')

    if g.work:
        # check if check_number/check_value is number
        check_number = check_data(value=updated_data['number'])
        check_value = check_data(value=updated_data['value'])

        # execute if check_number check_value not None
        if check_number is not None and check_value is not None:
            if g.status_work_start is None or (g.status_work_start is not None and g.status_work_pause is not None):
                # assign feelds value
                g.work.number_slab = updated_data['number']
                g.work.stone_id = updated_data['stone_id']
                g.work.thickness = updated_data['stone_thickness']
                g.work.value = updated_data['value']
                g.work.order_of_client = updated_data['order_client']
                g.work.set_worker = updated_data['set_worker']

                # save changes to db
                db.session.commit()
                return jsonify({'success': 'Work updated successfully'})
            else:
                return jsonify({'error':'Ошибка редактирования! Приостановите производство!'}), 404
        else:
            return jsonify({'error': 'Ошибка!!! Данные введены не верно'}), 404
    else:
        return jsonify({'error': 'Такая работа не найдена'}), 404


@app.route('/problem_solved', methods=['POST'])
@login_required
def change_status_problem_solved():
    #get id work from table performance work
    value = request.form.get('q')
    # get row (data) table problem_work for change problem_solved
    get_data_table_problemwork= ProblemWork.query.filter_by(id_performancework=value)\
        .order_by(desc(ProblemWork.id)).first_or_404()
    #change value problem_solved and save changes
    get_data_table_problemwork.problem_solved = True
    db.session.commit()
    # response message indicating successful completion of the request
    response = {'success': "Статус изменён - разрешено возобновление работы"}
    return jsonify(response)


@app.route('/change_multiplikate', methods=['POST'])
def chang_multiplikate():
    try:
        multiplikate = request.form.get('multiplikate') #get value from form (field_select)
        id_statisticuser = request.form.get('id') # get id from page
        order = request.form.get('order') # get value of order

        if id_statisticuser is not None:
            # get row from table statistics_user for set value of factor_price
            get_row_statisticsuser = StatisticsUser.query.get(id_statisticuser)

            # get value from page and assign this value "factor_price" table statistics_user
            get_row_statisticsuser.factor_price = multiplikate

            # save data to table
            db.session.commit()
    except Exception as error:
        db.session.rollback()
        print(f'There was an error saving data to the database: {error}'), 500
    return redirect(url_for('manage_work_order', q=order))


# this function is refres-h timeline - dinamic
@app.route('/refresh_timeline', methods=['POST'])
@login_required
def refresh_timeline():
    # this function return number day of week
    get_period_json=request.get_json()
    period_of_customer = get_period_json['period']

    # function is returned count of days than we get from page after select from selecfield
    def days():
        if period_of_customer == "1":
            g.period_days = 0
        elif period_of_customer == "7":
            g.period_days = 7
        elif period_of_customer == "14":
            g.period_days = 14
        else: g.period_days = 30

        return g.period_days

    try:
        # crete variable for set period from "period_start" to "period_end"
        period_start = (datetime.now()).date()
        period_end = (datetime.now() + timedelta(days=days())).date()

        # Get data from all works table Slabworks, Preproduct, Partworks.We used filter timedelta (from data start),
        # status_starr=None, if currennt_user.id == user.id from work table who have to do a task.
        preproduct_with_status_none = PreProduct.query.join(PerformanceWork,
                                                            PreProduct.id == PerformanceWork.id_preproduct) \
            .filter(PerformanceWork.status_start == None, PreProduct.set_worker == current_user.id,
                    db.func.date(PreProduct.start_work_date) >= period_start,
                    db.func.date(PreProduct.start_work_date) >= period_start).all()
        slabworks_with_status_none = SlabWorks.query.join(PerformanceWork,
                                                          SlabWorks.id == PerformanceWork.id_work_slabs) \
            .filter(PerformanceWork.status_start == None, SlabWorks.set_worker == current_user.id,
                    db.func.date(SlabWorks.start_work_date) <= period_end,
                    db.func.date(SlabWorks.start_work_date) >= period_start).all()
        partworks_with_status_none = PartWorks.query.join(PerformanceWork, PartWorks.id == PerformanceWork.id_work_part) \
            .filter(PerformanceWork.status_start == None, PartWorks.set_worker == current_user.id,
                    db.func.date(PartWorks.start_work_date) <= period_end,
                    db.func.date(PartWorks.start_work_date) >= period_start).all()

        # create list events for the time_line on the page
        events = []
        # iterate list that we get from Table Class Preproduct
        for event in preproduct_with_status_none:
            if event.order_client:
                if event.order_client.order_status !="closed":
                    event_data = {
                        'amount': f'{event.work.work_title}',
                        'title': '',
                        'type' : f'{event.work.work_kind}',
                        'date': f'{event.start_work_date.isoformat()}',
                        'description': f'{event.work.work_type}'
                    }
                    events.append(event_data)  # add  data to list
            else:
                event_data = {
                    'amount': f'{event.work.work_title}',
                    'title': f'{event.work.work_type}',
                    'type': '',
                    'date': f'{event.start_work_date.isoformat()}',
                    'description': f'{event.work.work_type}'
                }
                events.append(event_data)  # add  data to list

        # iterate list that we get from Table Class Slabworks
        for event in slabworks_with_status_none:
            if event.order_client:
                if event.order_client.order_status != "closed":
                    event_data = {
                        'amount': f'{event.work_set.work_title}',
                        'title': f'{event.work_set.work_type}',
                        'type': f'{event.work_set.work_kind}',
                        'date': f'{event.start_work_date.isoformat()}',
                        'description': f'{event.work_set.work_type}'
                    }
                    events.append(event_data)
            else:
                event_data = {
                    'amount': f'{event.work_set.work_title}',
                    'title': f'{event.work_set.work_type}',
                    'type': f'{event.work_set.work_kind}',
                    'date': f'{event.start_work_date.isoformat()}',
                    'description': f'{event.work_set.work_type}'
                }
                events.append(event_data)

        # iterate list that we get from Table Class Parts
        for event in partworks_with_status_none:
            if event.order_client:
                if event.order_client.order_status != "closed":
                    event_data = {
                        'amount': f'{event.work_set_part.work_title}',
                        'title': f'{event.work_set_part.work_type}',
                        'type': f'{event.work_set_part.work_kind}',
                        'date': f'{event.start_work_date.isoformat()}',
                        'description': f'{event.work_set_part.work_type}'
                    }
                    events.append(event_data)  # add  data to list
            else:
                event_data = {
                    'amount': f'{event.work_set_part.work_title}',
                    'title': f'{event.work_set_part.work_type}',
                    'type': f'{event.work_set_part.work_kind}',
                    'date': f'{event.start_work_date.isoformat()}',
                    'description': f'{event.work_set_part.work_type}'
                }
                events.append(event_data)  # add  data to list

        return jsonify(events)
    except Exception as error:
        return jsonify({'error': str(error)}), 400

