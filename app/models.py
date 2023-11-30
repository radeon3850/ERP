from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# create table "Specialization" - one to many
class Specialization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_departmet = db.Column(db.String(200), index=True)
    job_title = db.Column(db.String(150), index=True, unique=True)
    users = db.relationship('User', backref='employee',
                            lazy=True)  # this is not a table field, the code sets the relation of the specialization

    def __repr__(self):
        return f'{self.id}, {self.job_title}'


# create table "User" One to Many
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), index=True)
    last_name = db.Column(db.String(150), index=True)
    phone = db.Column(db.String(120), index=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    specialization_id = db.Column(db.Integer, db.ForeignKey('specialization.id'), nullable=False)
    online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)
        db.session.commit()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'id:{self.id}||{self.username}||{self.password_hash}||{self.first_name}||{self.last_name}||' \
               f'{self.phone}||spec:{self.specialization_id}'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    date_time = db.Column(db.DateTime)  # date and time when was  added this row
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('order_client.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body, self.order_id)


# create table Works abous all types of jobs
class Works(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    work_title = db.Column(db.String(150))
    work_type = db.Column(db.String(150))
    work_kind = db.Column(db.String(150), index=True)

    def __repr__(self):
        return f'{self.work_title} | {self.work_type} | id {self.id}'


# create table "Clients"
class Clients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), index=True)
    last_name = db.Column(db.String(150), index=True)
    phone_number = db.Column(db.String(40), index=True, unique=True)
    order_client = db.relationship('OrderClient', backref='client_of_order', lazy=True)
    # back_up_phone = db.Column(db.String(40), index=True, unique=True)
    # order_of_client = db.relationship('OrderClient', backref='order_of_client', lazy='dynamic')

    def __repr__(self):
        return f'{self.first_name} {self.last_name}, {self.phone_number}, {self.id}'


# create teable orer of client
class OrderClient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_order = db.Column(db.String(300))
    object_description = db.Column(db.String(2000))
    address = db.Column(db.String(5000))  # address of project
    deadline = db.Column(db.DateTime)  # when do we need to finish the project
    measurements = db.Column(db.Boolean, default=False, nullable=False)  # choice - Fals/True, do we need measures
    project_drawing = db.Column(db.Boolean, default=False,
                                nullable=False)  # choice - Fals/True, do we need project drawing
    control = db.Column(db.Boolean, default=False, nullable=False)
    clients_id = db.Column(db.Integer, db.ForeignKey('clients.id'),
                           nullable=False)  # relationship to table "clients" meny to one
    order_apruved = db.Column(db.Boolean,
                              default=False)  # check whether the order has been accepted before starting production
    order_status = db.Column(db.String())  # set statusp for order: work, closed
    progres = db.Column(db.String())  # precent of completed all works for this order
    date_time = db.Column(db.DateTime)  # date and time when was  added this row
    preproduct = db.relationship('PreProduct', backref='order_client', cascade='all, delete')

    def __repr__(self):
        return f'Заказ №: {self.id} {self.title_order}, {self.address}, Конечная дата: {self.deadline}, ' \
               f'Замеры: {self.measurements}, Чертежи: {self.project_drawing}, Контроль: {self.control}, Утверждён:{self.order_apruved}, order_status: {self.order_status}'


# table about assigns work on the slab
class SlabWorks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_slab = db.Column(db.String(5), index=True)
    stone_id = db.Column(db.Integer, db.ForeignKey('stone.id'))
    stone_name = db.Column(db.String(50), index=True)
    thickness = db.Column(db.String(20), index=True)
    value = db.Column(db.String(10), index=True)
    order_of_client = db.Column(db.Integer, db.ForeignKey('order_client.id'), nullable=False)
    slab_works = db.Column(db.Integer, db.ForeignKey('works.id'),
                           nullable=False)  # relationship to table "Works" One to many
    set_worker = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_work_date = db.Column(db.DateTime)
    end_work_date = db.Column(db.DateTime)
    date_time = db.Column(db.DateTime)  # date and time when was  added this row
    # work_sequence = db.Column(db.String(3))  #  послудовательность для работ
    work_set = db.relationship("Works", backref='work_set', lazy='subquery')
    worker = db.relationship("User", backref='worker_set', lazy='subquery')
    order_client = db.relationship("OrderClient", backref='order_client_sl', lazy='subquery')
    query_slabworks = db.relationship("PerformanceWork", backref='query_slabworks', cascade='all, delete',
                                      lazy='subquery')
    stone = db.relationship('Stone', backref='slabworks')

    def __repr__(self):
        return f'<slab_works, id:{self.id}, Slab№ {self.number_slab},Заказ: {self.order_of_client}, id_work:{self.slab_works}, id_user{self.set_worker}, start: {self.start_work_date}, end: {self.end_work_date}, stone_name:{self.stone_name} >'


# table about assigns work on the parts
class PartWorks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_part = db.Column(db.String(16), index=True)
    stone_id = db.Column(db.Integer, db.ForeignKey('stone.id'))
    thickness = db.Column(db.String(150), index=True)
    value = db.Column(db.String(150), index=True)
    start_work_date = db.Column(db.DateTime)
    end_work_date = db.Column(db.DateTime)
    order_of_client = db.Column(db.Integer, db.ForeignKey('order_client.id'), nullable=False)
    part_works = db.Column(db.Integer, db.ForeignKey('works.id'),
                           nullable=False)  # relationship to table "Works" One to many
    set_worker = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # work_sequence = db.Column(db.String(3)) #  послудовательность для работ
    date_time = db.Column(db.DateTime)  # date and time when was  added this row
    work_set_part = db.relationship("Works", backref='work_set_part', lazy='subquery')
    worker = db.relationship("User", backref='worker_part', lazy='subquery')
    order_client = db.relationship("OrderClient", backref='orderclient_pt', lazy='subquery')
    query_partworks = db.relationship("PerformanceWork", backref='query_partworks', cascade='all, delete',
                                      lazy='subquery')
    stone = db.relationship('Stone', backref='partworks')

    def __repr__(self):
        return f'part_works, id: {self.id}, Part# {self.number_part}, заказ_кл:{self.order_of_client}, {self.part_works}, Дата начала:{self.start_work_date}>'


# create table preroduct
class PreProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_of_client = db.Column(db.Integer, db.ForeignKey('order_client.id'), nullable=False)
    work_type = db.Column(db.Integer, db.ForeignKey('works.id'), nullable=False)
    set_worker = db.Column(db.Integer, db.ForeignKey('user.id'))
    work = db.relationship('Works', backref='work', lazy='subquery')
    worker = db.relationship('User', backref='worker', lazy='subquery')
    start_work_date = db.Column(db.DateTime)
    end_work_date = db.Column(db.DateTime)
    # work_sequence = db.Column(db.String(3))  # послудовательность для работ
    date_time = db.Column(db.DateTime)  # date and time when was  added this row
    query_preproduct = db.relationship("PerformanceWork", backref='query_preproduct', lazy='subquery',
                                       cascade='all, delete')

    def __repr__(self):
        return f'< preproduct, id: {self.id},id_order: {self.order_of_client},' \
               f'work_id: {self.work_type}, user_id: {self.set_worker} >'


# table for saved path of fails that we added to project.
class UploadFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename = db.Column(db.String(255))
    file_path = db.Column(db.String(255))
    order_client_id = db.Column(db.Integer, db.ForeignKey('order_client.id'))
    date_time = db.Column(db.DateTime)  # date and time when was  added this row
    user = db.relationship('User', backref=db.backref('upload_files', lazy=True))

    def __repr__(self):
        return f'{self.id},\n {self.filename}, \n {self.file_path}, {self.order_client_id}'


# create table performance_work
class PerformanceWork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_preproduct = db.Column(db.Integer, db.ForeignKey('pre_product.id'))
    id_work_slabs = db.Column(db.Integer, db.ForeignKey('slab_works.id'))
    id_work_part = db.Column(db.Integer, db.ForeignKey('part_works.id'))
    status_start = db.Column(db.Boolean)
    status_pause = db.Column(db.Boolean)
    status_end = db.Column(db.Boolean)
    status_problem = db.Column(db.Boolean)
    date_time = db.Column(db.DateTime) # date and time when was  added this row

    def __repr__(self):
        return f'id_preproduct_work: {self.id_preproduct} || id_slabwork: {self.id_work_slabs} ' \
               f'|| id_part_work: {self.id_work_part} || status_start: {self.status_start} ' \
               f'|| status_end: {self.status_end}'


#  create table work execution time table
class TimeWork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_performance_work = db.Column(db.Integer, db.ForeignKey('performance_work.id'))
    start_date = db.Column(db.DateTime)
    pause_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    problem_date = db.Column(db.DateTime)
    lead_time = db.Column(db.Integer, nullable=True)
    resume_date = db.Column(db.DateTime)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    query_performance_work = db.relationship("PerformanceWork", backref='query_time', lazy='subquery')

    def __repr__(self):
        return f'< id_performance: {self.id_performance_work} || start_data: {self.start_date} || {self.resume_date} || ' \
               f'{self.pause_date} || {self.end_date} || {self.problem_date} || {self.lead_time} || user: {self.id_user}> '


# model for add data sometimes
class Transit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    some_data = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    s_p = db.Column(db.String(5))

    def __repr__(self):
        return f"< id: {self.some_data}>< table: {self.s_p}>"


# table Stones
class Stone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_stone = db.Column(db.String(100))

    def __repr__(self):
        return f"id: {self.id} ,камень: {self.type_stone}"


# table stones in order_client
class ListOrderStone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_stone = db.Column(db.Integer, db.ForeignKey('stone.id'))  # id stone from table Stone
    order_of_client = db.Column(db.Integer, db.ForeignKey('order_client.id'))  # id order_clietn
    stone_name = db.Column(db.String(100))  # color or name stone
    date_time = db.Column(db.DateTime)  # date when added  data to table
    query_stone = db.relationship("Stone", foreign_keys=[id_stone], backref='list_order_stones')  # Ship table stone

    def __repr__(self):
        return f'stone: {self.id_stone} order: {self.order_of_client}  color: {self.stone_name} date: {self.date_time}'


class PriсeWork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_works = db.Column(db.Integer, db.ForeignKey('works.id'))
    marble_2sm = db.Column(db.REAL)
    marble_3sm = db.Column(db.REAL)
    granite_import_2sm = db.Column(db.REAL)
    granite_import_3sm = db.Column(db.REAL)
    granite_uk_2sm = db.Column(db.REAL)
    granite_uk_3sm = db.Column(db.REAL)
    travertine_2sm = db.Column(db.REAL)
    travertine_3sm = db.Column(db.REAL)
    onyx_2sm = db.Column(db.REAL)
    onyx_3sm = db.Column(db.REAL)

    def __repr__(self):
        return f'id_work: {self.id_works}, marble_2:{self.marble_2sm}, marble_3: {self.marble_3sm},granite_import_2: ' \
               f'{self.granite_import_2sm}, granite_import_3: {self.granite_import_3sm}, granite_uk_2: ' \
               f'{self.granite_uk_2sm}, granite_uk_3: {self.granite_uk_3sm}, travertine_2: ' \
               f'{self.travertine_2sm}, travertine_3: {self.travertine_3sm}, onyx_2: {self.onyx_2sm}, onyx_3: {self.onyx_3sm}'


# create table statistics_user
class StatisticsUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_works = db.Column(db.Integer, db.ForeignKey('works.id'))
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    id_performance_work = db.Column(db.Integer, db.ForeignKey('performance_work.id'))
    all_time_work = db.Column(db.Integer)
    value_work = db.Column(db.String(10))
    date_fact_end = db.Column(db.DateTime)
    price_work = db.Column(db.REAL)
    factor_price = db.Column(db.REAL, default=1)
    query_works = db.relationship('Works', backref='works', lazy='subquery')
    query_user = db.relationship('User', backref='user', lazy='subquery')
    performance_work = db.relationship('PerformanceWork', backref='performance', lazy='subquery')

    def __repr__(self):
        return f'id: {self.id} || user: {self.id_user} || fact_end:{self.date_fact_end} ' \
               f'|| price: {self.price_work} || time_work:{self.all_time_work} ' \
               f'|| factor_price:{self.factor_price}'

# this model is save data about work status_problem of that is True, we get id, status if problem is completed and date
class ProblemWork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_performancework = db.Column(db.Integer, db.ForeignKey('performance_work.id'))
    problem_solved = db.Column(db.Boolean)
    resume_after_solved = db.Column(db.Boolean, default=False)
    date_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'problem solved status:{self.problem_solved} || id_performance: {self.id_performancework}'
