from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, TextField, \
    validators, FileField, RadioField
from wtforms.validators import DataRequired, EqualTo, Regexp, Length
from wtforms.widgets import TextArea, ListWidget
from app.models import User, Clients, Specialization, Works, Stone
from app import db
from wtforms import ValidationError


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    choices = [(spec.id, spec.job_title) for spec in (db.session.query(Specialization).all())]
    choices.insert(0, (0, 'Выбрать специализацию'))
    specialization_id = SelectField('Выбрать специализацию', choices=choices)
    username = StringField('Логин', validators=[DataRequired()])
    phone = StringField('Телефон', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторить пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Регистрация')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста введите другой логин.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста введите другой email')


# this form added client to DB
class AddClient(FlaskForm):
    first_name = StringField('Имя:', validators=[DataRequired()])
    last_name = StringField('Фамилия:', validators=[DataRequired()])
    phone = StringField('Номер телефона:', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class AddOrder(FlaskForm):
    # get data for db Table "clietn" and creat list for transfer to choices
    choices_client = [(client.id, (client.first_name, client.last_name, client.phone_number)
                ) for client in (db.session.query(Clients).all())]
    client_id = SelectField('Выбрать Клиента', choices=choices_client)
    name_order = StringField('Название заказа: ', validators=[DataRequired()])
    object_description = TextField('Описание Обэкта: ', validators=[validators.Optional()], widget=TextArea())
    address = StringField('Адрес объекта: ', validators=[DataRequired()])
    deadline = DateField('Конечная дата: ', validators=[validators.Optional(), DataRequired()], format='%Y-%m-%d')
    checkbox_measurements = BooleanField('Замеры', default=False)
    checkbox_blueprint = BooleanField('Чертежи', default=False)
    checkbox_control = BooleanField('Контроль', default=True)
    submit = SubmitField('Создать заказ')

    def validate_client_id(self, checkbox_control):
        if checkbox_control.data == "0":
            raise ValidationError('Необхідно вибрати клієнта зі списку.')


# this form for adedd slabs or parst to db on page manage_work_order.html -viewfunctiom - manage_work_order()
class AddWork(FlaskForm):
    data_first_column = Works.query.with_entities(Works.work_title).distinct().all() # get list work_title (table - works)

    choices_work = [(work.work_title, work.work_title) for work in data_first_column if work.work_title is not None and
                    work.work_title!='ПРЕДПРОИЗВОДСТВЕННАЯ' and work.work_title!='КОНТРОЛЬ']
    choices_thickness = [('2', '2 см'), ('3', '3 см')]

    choices_work.insert(0, (0, 'Выбрать вид работы'))
    choices_thickness.insert(0, (0, 'Выбрать толщину'))

    number_work = StringField('Номер', validators=[DataRequired(), Regexp('^\d+(\.\d{1,3})?$',
                                            message='Не верный формат, только для числовых значений')])
    stone = SelectField('Выбрать камень')
    name_stone = StringField('Название камня')

    s_p_work = SelectField('Выбрать направление *', choices=[(0, 'Выбрать направление'), ('Cляб', 'Сляб'), ('Деталь', 'Деталь')])
    thickness = SelectField('Толщина', choices=choices_thickness, coerce=int,
                            validators=[DataRequired(message="Не выбрана толщина камня")])
    work_title = SelectField('Вид Работ', choices=choices_work)
    work_type = SelectField('Тип Работ', choices=[], coerce=int, validate_choice=False)
    work_subtype = SelectField('Подтип работ', choices=[], coerce=int, validate_choice=False)

    value_work = StringField('Значение', validators=[DataRequired(), Regexp('^\d+(\.\d{1,3})?$',
                                        message='Не верный формат, только для числовых значений')])
    submit = SubmitField('Сохранить')



# form setting worker for work_slab and work_part
class AddWorker(FlaskForm):
    workers = User.query.all()
    choices = [(str(worker.id), f"{worker.first_name} {worker.last_name}") for worker in workers]
    choices.insert(0, ('0', 'Выбрать из списка'))

    set_worker = SelectField('Выбрать ответственного', choices=choices)  # field of choice worker
    start_date = DateField("Дата начала работ", validators=[validators.Optional(), validators.DataRequired(
        message='Не установлена дата начала')], format='%Y-%m-%d')  # date start work
    end_date = DateField("Дата окончания", validators=[validators.Optional(), validators.DataRequired(
        message='Не установлена дата окончания')], format='%Y-%m-%d')  # date end work
    submit = SubmitField('Сохранить')  # button submit


# form for download file to server
class UploadForm(FlaskForm):
    files = FileField('', validators=[FileRequired(message='Не вибрано жодного файлу')], render_kw={'multiple': True})
    submit = SubmitField('Загрузить')  # buttom load


# form aded stone client's order
class AddStone(FlaskForm):
    choice_stone = [(stone.id, stone.type_stone) for stone in Stone.query.all()]  # list of choice stone in form
    choice_stone.insert(0,('0', 'выбрать из списка'))
    stone = SelectField('Выбрать камень', choices=choice_stone)  # choices stone form
    stone_name = StringField('Название камня')  # set color stone


class TestWorkForm(FlaskForm):
    data_first_column = Works.query.with_entities(Works.work_title).distinct().all()
    choices_work = [(work.work_title, work.work_title) for work in data_first_column]

    work_title = SelectField('Work Title', choices=choices_work)
    work_type = SelectField('Work Type', choices=[], validate_choice=False)
    work_subtype = SelectField('Work Subtype', choices=[], validate_choice=False)


class CustomListWidget(ListWidget):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('name', field.name)
        return super().__call__(field, **kwargs)

def custom_validator(kanban_form, field):
    value = field.data
    if value == '0' or value == 1:
        raise validators.ValidationError("Не вибран вид работ!")

def titlerwork_validator(kanban_form, field):
    value = field.data
    if value == '0' or value == 1:
        raise validators.ValidationError("Не вибран вид работ!")

# this form added works to table slab_works, part_works, performance_wrork // views function kanban()
class KanbanEvents(FlaskForm):
    data_first_column = Works.query.with_entities(Works.work_title).distinct().all()
    choices_work = [(work.work_title, work.work_title) for work in data_first_column if work.work_title is not None and
                    work.work_title!='ПРЕДПРОИЗВОДСТВЕННАЯ' and work.work_title!='КОНТРОЛЬ']
    choices_thickness = [('2', '2 см'), ('3', '3 см')]

    choices_work.insert(0, (0, ''))
    choices_thickness.insert(0, (0, ''))
    order_client = SelectField('Order', choices=[])
    radio_field = RadioField('Radio Field',
                             choices=[('slab', 'Слябы'), ('part', 'Детали')],
                             validators=[validators.DataRequired()],
                             widget=CustomListWidget(prefix_label=False),
                             render_kw={'class': 'form-check-input'})
    order_checkbox = BooleanField()

    number = StringField('Номер сляба', validators=[DataRequired(), Regexp('^\d+(\.\d{1,3})?$',
                                        message='Не верный формат, только для числовых значений')])
    stone = SelectField('Выбрать камень')
    name_stone = StringField('Название камня')
    thickness = SelectField('Толщина', choices=choices_thickness, coerce=int,
                            validators=[validators.DataRequired()])
    work_title = SelectField('Вид Работ', choices=choices_work, validators=[titlerwork_validator,
                                                                            validators.DataRequired()] )
    work_type = SelectField('Тип Работ', choices=[], validate_choice=False)
    work_subtype = SelectField('Подтип работ', choices=[], coerce=int, validate_choice=False)
    value_work = StringField('Значение', validators=[DataRequired(), Regexp('^\d+(\.\d{1,3})?$',
                                        message='Не верный формат, только для числовых значений')])
    button_submit = SubmitField('Добавить работу')


# this form for set and changes work that we added to tables. // views function kanban()
class KanbanEventsChange(FlaskForm):
    data_first_column = Works.query.with_entities(Works.work_title).distinct().all()
    workers = User.query.all()
    choices_work = [(work.work_title, work.work_title) for work in data_first_column if work.work_title is not None and
                    work.work_title!='ПРЕДПРОИЗВОДСТВЕННАЯ' and work.work_title!='КОНТРОЛЬ']

    choices_stone = [(0, 'Выбрать камень')] + [(stone.id, stone.type_stone) for stone in Stone.query.all()]
    choices_thickness = [('2', '2 см'), ('3', '3 см')]

    choices_work.insert(0, (0, ''))
    choices_thickness.insert(0, (0, ''))

    choices_worker = [(str(worker.id), f"{worker.first_name} {worker.last_name}") for worker in workers]
    choices_worker.insert(0, ('0', 'Выбрать сотрудника'))

    set_worker_change = SelectField('Выбрать ответственного', choices=choices_worker)  # field of choice worker
    start_date_change = DateField("Дата начала работ", validators=[validators.Optional(), validators.DataRequired(
        message='Не установлена дата начала')], format='%Y-%m-%d')  # date start work
    end_date_change = DateField("Дата окончания", validators=[validators.Optional(), validators.DataRequired(
        message='Не установлена дата окончания')], format='%Y-%m-%d')  # date end work

    order_client_change = StringField('Order',validators=[DataRequired()])
    radio_field_change = RadioField('Radio Field',
                             choices=[('slab', 'Слябы'), ('part', 'Детали')],
                             validators=[validators.DataRequired()],
                             widget=CustomListWidget(prefix_label=False),
                             render_kw={'class': 'form-check-input'})
    # order_checkbox_change = BooleanField()

    number_change = StringField('Номер сляба', validators=[DataRequired(), Regexp('^\d+(\.\d{1,3})?$',
                                                message='Не верный формат, только для числовых значений')])
    stone_change = SelectField('Выбрать камень', choices=choices_stone)
    name_stone_change = StringField('Название камня')
    thickness_change = SelectField('Толщина', choices=choices_thickness, coerce=int,
                            validators=[validators.DataRequired()])
    work_title_change = SelectField('Вид Работ', choices=choices_work,
                                    validators=[titlerwork_validator, validators.DataRequired()] )
    work_type_change = SelectField('Тип Работ', choices=[], validate_choice=False)
    work_subtype_change = SelectField('Подтип работ', choices=[], coerce=int, validate_choice=False)
    value_work_change = StringField('Значение', validators=[DataRequired(), Regexp('^\d+(\.\d{1,3})?$',
                                                message='Не верный формат, только для числовых значений')])


#  form for changes login and password
class ChangeLoginPasswordForm(FlaskForm):
    username = StringField('Новый логин', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('Новый пароль', validators=[DataRequired()])
    submit = SubmitField('Изменить')
