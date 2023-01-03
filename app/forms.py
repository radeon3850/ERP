from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, TextField, \
    RadioField, validators
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Optional
from wtforms.widgets import TextArea
from app.models import User,  Clients, Specialization
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
    object_description = TextField ('Описание Обэкта: ', validators=[validators.Optional()], widget=TextArea())
    address = StringField('Адрес объекта: ', validators=[DataRequired()])
    deadline = DateField('Конечная дата: ',validators=[validators.Optional()], format='%Y-%m-%d')
    checkbox_measurements= BooleanField('Замеры', default=False)
    checkbox_blueprint = BooleanField('Чертежи', default=False)
    checkbox_control = BooleanField('Контроль', default=False)
    submit = SubmitField('Создать')

class Checkbox(FlaskForm):
    choices = [(user.id, " ".join((user.first_name, user.last_name))) for user in (User.query.all())]

    checkbox = BooleanField('Выбрать', default=False)
    # radio_batton = RadioField('Label', choices=[('value','description'),('value_two','whatever')])
    user_id = SelectField('Выбрать ответсвенного', choices=choices)
    save = SubmitField('Сохранить')
