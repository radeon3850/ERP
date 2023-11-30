from flask import Blueprint
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app.admin.admin import MyAdminIndexView

admin_blueprint = Blueprint('admin_blueprint', __name__, template_folder='templates')
admin = Admin(name='ERP Admin', template_mode='bootstrap4')


# this frunction initializes Views for table of DB, their "Models"
def init_app(app):
    from app.models import User, Specialization, Post, Works, Clients, OrderClient, SlabWorks, PartWorks, PriсeWork
    from app import db
    # this vievs is show page or show table from db
    # admin.init_app - this class View is show "inaex" of page templates flask-admin
    # class MyAdminIndexView this viev from app.admin.admin import MyAdminIndexView
    admin.init_app(app, index_view=MyAdminIndexView(name='Главная'))
    admin.add_view(ModelView(User, db.session, name='Пользователь'))
    admin.add_view(ModelView(Specialization, db.session, name='Специализация'))
    admin.add_view(ModelView(Post, db.session, name='Чат сообщения'))
    admin.add_view(ModelView(Works, db.session, name='Работы'))
    admin.add_view(ModelView(Clients, db.session, name='Клиенты'))
    admin.add_view(ModelView(OrderClient, db.session, name='Заказы'))
    admin.add_view(ModelView(SlabWorks, db.session, name='Слябы'))
    admin.add_view(ModelView(PartWorks, db.session, name='Детали'))
    admin.add_view(ModelView(PriсeWork, db.session, name='Цена работ'))
