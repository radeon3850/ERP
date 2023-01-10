# -*- coding: utf-8 -*-
import flask
import flask_sqlalchemy
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm,AddClient ,AddOrder, Checkbox
from app.models import User, Clients, OrderClient, PreProduct


@app.route('/')
@app.route('/index')
@login_required
def index():
    client_order= OrderClient.query.all()
    return render_template('index.html', title='Главная', client_order=client_order)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Войти', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, phone=form.phone.data,
                    first_name=form.first_name.data, last_name=form.last_name.data,
                    specialization_id=form.specialization_id.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


@app.route('/add_order', methods = ['GET', 'POST'])
@login_required
def add_order():
    form_add_client = AddClient()
    if 'first_name' in request.form: # Chesk that flask-form (AddClient) from add_order send data
        if form_add_client.is_submitted():
            client = Clients(first_name=form_add_client.first_name.data, last_name=form_add_client.last_name.data, phone_number=form_add_client.phone.data) # geta form AddClient
            db.session.add(client)  # add data to table Client
            db.session.commit() # connect to data base
            flash('Клиент добавлен в базу')
            flash('Клиент добавлен в базу')
            return redirect(url_for('add_order'))
    form = AddOrder()
    form.client_id.choices = [(client.id, " ".join((client.first_name, client.last_name, client.phone_number)))for client in # update data from table Client for choices flask-form (AddOrder)
                              (db.session.query(Clients).all())]
    if 'name_order' in request.form: # Chesk that flask-form (AddOrder) from add_order send data
        if form.is_submitted():
            client_order=OrderClient(clients_id=form.client_id.data, title_order=form.name_order.data, title_stone=form.stone.data, # получение данных c формы AddOrder для добавления в базу данных
                                     object_description=form.object_description.data, address=form.address.data,
                                     deadline=form.deadline.data, measurements=form.checkbox_measurements.data,
                                     project_drawing=form.checkbox_blueprint.data, control=form.checkbox_control.data)
            # dt=request.get_data("POST")
            # print(dt)
            db.session.add(client_order) # add data to table OrderClient
            db.session.commit() # connect to data base
            flash('Заказ покупателя добавлен')
            return redirect(url_for('index'))
    return render_template("add_order.html", title='Создание заказа клиента', form=form, form_add_client=form_add_client)


@app.route('/kanban')
@login_required
def kanban():
    posts = [
        {'worker': 'Starchenko', 'body': ' wokr with slab №1'},
        {'worker': 'Ivanov', 'body': ' wokr with part №5'}
    ]
    return render_template("kanban.html", title='Заполните форму для создания заказа',  posts=posts )

@app.route('/order_client', methods=['GET', 'POST'])
@login_required
def order_client():
    name_field = ['measurements', 'project_drawing', 'control']
    form=Checkbox()
    q=request.args.get('q')
    order_client = OrderClient.query.get(q)
    if form.is_submitted():
        set_worker=PreProduct(number_order_client=order_client.id, )
    return render_template("order_client.html", title="Заказ клиента", order_client=order_client, form=form, name_field=name_field )