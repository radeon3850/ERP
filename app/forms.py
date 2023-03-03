from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, TextField, \
    RadioField, validators, TextAreaField, MultipleFileField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Optional
from wtforms.widgets import TextArea, html_params, Select
from app.models import User, Clients, Specialization, Works
from app import db


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    choices = [(spec.id, spec.job_title) for spec in (db.session.query(Specialization).all())]
    specialization_id = SelectField('Select specializtion', choices=choices)
    username = StringField('Username', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class AddClient(FlaskForm):
    first_name = StringField('Имя клиента: ', validators=[DataRequired()])
    last_name = StringField('Фамилия клиента: ', validators=[DataRequired()])
    phone = StringField('Номер телефона клиента: ', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class AddOrder(FlaskForm):
    choices_client = [(client.id, (client.first_name, client.last_name, client.phone_number)
                       ) for client in (db.session.query(Clients).all())]

    client_id = SelectField('Выбрать Клиента', choices=choices_client)
    name_order = StringField('Название заказа: ', validators=[DataRequired()])
    stone = StringField('Камень: ', validators=[DataRequired()])
    object_description = TextField('Описание Обэкта: ', validators=[validators.Optional()], widget=TextArea())
    address = StringField('Адрес объекта: ', validators=[DataRequired()])
    deadline = DateField('Конечная дата: ', validators=[validators.Optional(True)], format='%Y-%m-%d')
    checkbox_measurements = BooleanField('Замеры', default=False)
    checkbox_blueprint = BooleanField('Чертежи', default=False)
    checkbox_control = BooleanField('Контроль', default=True)
    submit = SubmitField('Создать заказ')


class Checkbox(FlaskForm):
    choices = [(user.id, " ".join((user.first_name, user.last_name))) for user in (User.query.all())]
    option_select = choices.insert(0, (0, 'Выбрать сотрудника'))
    user_id_1 = SelectField('Замеры',
                            choices=choices)  # choise firstname and last name, but save to database are user_idfrom table user
    user_id_2 = SelectField('Чертежи',
                            choices=choices)  # choise firstname and last name, but save to database are user_idfrom table user
    user_id_3 = SelectField('Контроль',
                            choices=choices)  # choise firstname and last name, but save to database are user_idfrom table user
    save = SubmitField('Сохранить')


class Add_slab(FlaskForm):
    choices = [(work.id, work.work_type) for work in (Works.query.all())]
    option_select=choices.insert(0,(0, 'Выбрать тип работы'))
    number_slab = StringField("Номер сляба", validators=[DataRequired()])
    thickness = StringField("Толщина", validators=[DataRequired()])
    type_slab = SelectField('Вид работ', choices=choices)
    value_work = StringField("Значение ", validators=[DataRequired()])
    submit = SubmitField('Сохранить')

class Add_part(FlaskForm):
    choices = [(work.id, work.work_type) for work in (Works.query.all())]
    option_select=choices.insert(0,(0, 'Выбрать тип работы'))
    number_part = StringField("Номер детали", validators=[DataRequired()])
    thickness = StringField("Толщина", validators=[DataRequired()])
    value_work = StringField("Значение ", validators=[DataRequired()])
    deadline = DateField('Конечная дата: ', validators=[validators.Optional()], format='%Y-%m-%d')
    part_work = SelectField('Вид работ', choices=choices)
    submit = SubmitField('Сохранить')

class AddWorker(FlaskForm):
    choices = [(worker.id, (worker.first_name, worker.last_name)) for worker in (User.query.all())]
    option_select=choices.insert(0,(0, 'Выбрать из списка'))
    set_worker = SelectField('Выбрать ответственного', choices=choices)
    start_date = DateField("Дата начала работ", validators=[validators.Optional()], format='%Y-%m-%d')
    end_date = DateField("Дата окончания", validators=[validators.Optional()], format='%Y-%m-%d')
    submit = SubmitField('Сохранить')

#form for download file to server
class UploadForm(FlaskForm):
    files = FileField('', validators=[FileRequired(message='Не вибрано жодного файлу')],
                      render_kw={'multiple': True})
    submit=SubmitField('Загрузить')