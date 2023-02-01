# -*- coding: utf-8 -*-
import flask
import flask_sqlalchemy
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, AddClient, AddOrder, Checkbox
from app.models import User, Clients, OrderClient, PreProduct, Works, SlabWorks


@app.route('/')
@app.route('/index')
@login_required
def index():
    client_order = OrderClient.query.all()
    user_spec = current_user.specialization_id
    if user_spec == 2:
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('workplace')
        return redirect(next_page)
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


@app.route('/add_order', methods=['GET', 'POST'])
@login_required
def add_order():
    def add_data(self):
        db.session.add(self)  # add data to table OrderClient
        db.session.commit()

    form_add_client = AddClient()
    if 'first_name' in request.form:  # Chesk that flask-form (AddClient) from add_order send data
        if form_add_client.is_submitted():
            client = Clients(first_name=form_add_client.first_name.data, last_name=form_add_client.last_name.data,
                             phone_number=form_add_client.phone.data)  # geta form AddClient
            add_data(self=client)  # connect to data base
            flash('Клиент добавлен в базу')
            return redirect(url_for('add_order'))

    form = AddOrder()
    form.client_id.choices = [(client.id, " ".join((client.first_name, client.last_name, client.phone_number))) for
                              client in  # update data from table Client for choices flask-form (AddOrder)
                              (db.session.query(Clients).all())]
    if 'name_order' in request.form:  # Chesk that flask-form (AddOrder) from add_order send data
        if form.is_submitted():
            client_order = OrderClient(clients_id=form.client_id.data, title_order=form.name_order.data,
                                       title_stone=form.stone.data,
                                       # получение данных c формы AddOrder для добавления в базу данных
                                       object_description=form.object_description.data, address=form.address.data,
                                       deadline=form.deadline.data, measurements=form.checkbox_measurements.data,
                                       project_drawing=form.checkbox_blueprint.data, control=form.checkbox_control.data)

            add_data(self=client_order)  # add data to table OrderClient
            flash('Заказ покупателя добавлен')

            # check - if fields of form (checkbox_measurements,checkbox_blueprint, checkbox_control) sends True
            # save data to database
            if form.checkbox_measurements.data == True:
                order_client = (db.session.query(OrderClient).order_by(OrderClient.id.desc()).first()).id
                work = Works.query.get(48).id
                work_staf = PreProduct(number_order_client=order_client, work_type=work)
                add_data(self=work_staf)
            if form.checkbox_blueprint.data == True:
                order_client = (db.session.query(OrderClient).order_by(OrderClient.id.desc()).first()).id
                work = Works.query.get(49).id
                work_staf = PreProduct(number_order_client=order_client, work_type=work)
                add_data(self=work_staf)
            if form.checkbox_control.data == True:
                order_client = (db.session.query(OrderClient).order_by(OrderClient.id.desc()).first()).id
                work = Works.query.get(50).id
                work_staf = PreProduct(number_order_client=order_client, work_type=work)
                add_data(self=work_staf)

            return redirect(url_for('index'))
    return render_template("add_order.html", title='Создание заказа клиента', form=form,
                           form_add_client=form_add_client)


@app.route('/kanban', methods=['GET', 'POST'])
@login_required
def kanban():
    order_manufacture = PreProduct.query.all()
    return render_template("kanban.html", title='Kanban', order_manufacture=order_manufacture)


@app.route('/workplace', methods=['GET', 'POST'])
@login_required
def workplace():
    order_manufacture = PreProduct.query.filter_by(set_worker=current_user.id).all()
    return render_template("workplace.html", title='Workplace', order_manufacture=order_manufacture)


@app.route('/order_client', methods=['GET', 'POST'])
@login_required
def order_client():
    name_field = ['measurements', 'project_drawing', 'control']  # transfer list to HTML for Jinja
    work_dic = {'measurements': 'Замеры', 'project_drawing': 'Чертежи', 'control': 'Контроль'}
    form = Checkbox()
    q = request.args.get('q')  # get data about Number of order_client from HTML after сlick on the button
    order_client = OrderClient.query.get(q)
    preproduct_work = PreProduct.query.filter_by(number_order_client=q).all()

    if form.is_submitted():
        for work in preproduct_work:
            if work.work_type == 48:
                add_workrer = PreProduct.query.get(
                    (PreProduct.query.filter_by(number_order_client=q, work_type=48).first()).id)
                add_workrer.set_worker = form.user_id_1.data
                db.session.commit()

            if work.work_type == 49:
                add_workrer = PreProduct.query.get(
                    (PreProduct.query.filter_by(number_order_client=q, work_type=49).first()).id)
                add_workrer.set_worker = form.user_id_2.data
                db.session.commit()

            if work.work_type == 50:
                add_workrer = PreProduct.query.get(
                    (PreProduct.query.filter_by(number_order_client=q, work_type=50).first()).id)
                add_workrer.set_worker = form.user_id_3.data
                db.session.commit()

    return render_template("order_client.html", title="Заказ клиента", order_client=order_client, form=form,
                           name_field=name_field, work_dic=work_dic)


@app.route('/add_slab', methods=['GET', 'POST'])
@login_required
def add_slab():
    user = User.query.all()
    q = request.args.get('q')  # get data about Number of order_client from HTML after сlick on the button
    order_client = OrderClient.query.get(q)
    check_data = SlabWorks.query.filter_by(oreder_of_client=q).all()

    if request.method == 'POST':
        number = request.form['number']
        thickness = request.form['thickness']
        type = request.form['type']
        if len(number)==0 or len(thickness)==0 or len(type)==0:
            print("Поля формы пустые")
            flash('Заполенены не все поля формы добавления сляба')

        elif order_client.id==q and check_data.number_slab==number:
            flash('Сляб с такими параметрами уже добавлен')
        else:
            slab_data = SlabWorks(number_slab=number, thickness=thickness, oreder_of_client=order_client.id, slab_works=0,
                                  set_worker=0)
            db.session.add(slab_data)
            db.session.commit()
            flash('Сляб добавлен к карте заказа')

    slab=SlabWorks.query.filter_by(oreder_of_client=order_client.id).all()
    return render_template("add_slab.html", title='Добавление слябов', user=user, order_client=order_client, slab=slab)


@app.route('/add_part', methods=['GET', 'POST'])
@login_required
def add_part():
    return render_template("add_part.html", title='Добавление деталей')
