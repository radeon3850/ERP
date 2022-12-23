from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# create table "Specialization" - one to many
class Specialization (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # job_departmet = db.Column(db.String(200), index=True)
    job_title = db.Column(db.String(150), index=True, unique=True)
    users = db.relationship('User', backref='employee', lazy=True) # this is not a table field, the code sets the relation of the specialization

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
    specialization_id = db.Column(db.Integer, db.ForeignKey('specialization.id'), nullable = False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f' {self.username}, {self.password_hash}, {self.first_name} {self.last_name}, {self.phone}'

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id).order_by(
            Post.timestamp.desc())


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)



# create table Works abous all types of jobs
class Works (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    works_title = db.Column(db.String(150))
    works_type = db.Column(db.String(150))

    def __repr__(self):
        return f'<Works {self.works_title} {self.works_type}>'



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

#create teable orer of client
class OrderClient (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_order = db.Column(db.String(300))
    title_stone = db.Column(db.String(300))
    object_description = db.Column(db.String(2000))
    address = db.Column(db.String(5000)) # address of project
    deadline = db.Column(db.DateTime) # when do we need to finish the project
    measurements = db.Column(db.Boolean, default=False, nullable=False) # choice - Fals/True, do we need measures
    project_drawing = db.Column(db.Boolean, default=False, nullable=False) # choice - Fals/True, do we need project drawing
    control = db.Column(db.Boolean, default=False, nullable=False)
    clients_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False) # relationship to table "clients" meny to one

    def __repr__(self):
        return f'Заказ клиента: {self.id} {self.title_order}, {self.address}, Конечная дата: {self.deadline}'


# create table Oreder of Manufacture(product), all column besides id - have type Boollean
class OrderManufacture (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    raskroj= db.Column(db.Boolean, default=False, nullable=False)
    porezka = db.Column(db.Boolean, default=False, nullable=False)
    cpu = db.Column(db.Boolean, default=False, nullable=False)
    montag = db.Column(db.Boolean, default=False, nullable=False)
    vidacha = db.Column(db.Boolean, default=False, nullable=False)
    oreder_of_client = db.Column(db.Integer, db.ForeignKey('order_client.id'), nullable=False)



# table about assigns work on the slab
class SlabWorks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_slab = db.Column(db.String(16), index=True)
    thickness = db.Column(db.String(150), index=True)
    value = db.Column(db.String(150), index=True)
    deadline_slab = db.Column(db.DateTime)
    oreder_of_manufacture = db.Column(db.Integer, db.ForeignKey('order_manufacture.id'), nullable=False) #relationship to table "OrderManufacture" one to many
    slab_works = db.Column(db.Integer, db.ForeignKey('works.id'), nullable=False) #relationship to table "Works" One to many

    def __repr__(self):
        return f'<OrderClient {self.number_slab}, {self.oreder_of_manufacture}, {self.slab_works}, {self.deadline_slab}>'


# table about assigns work on the parts
class PartWorks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_part = db.Column(db.String(16), index=True)
    thickness = db.Column(db.String(150), index=True)
    value = db.Column(db.String(150), index=True)
    deadline_part = db.Column(db.DateTime)
    oreder_of_manufacture = db.Column(db.Integer, db.ForeignKey('order_manufacture.id'), nullable=False) #relationship to table "OrderManufacture" one to many
    # num_slab = db.Column(db.Integer, db.ForeignKey('SlabWorks.id'),nullable=False)  # relationship to table "SlabWorks" Many to One
    part_works = db.Column(db.Integer, db.ForeignKey('works.id'), nullable=False) #relationship to table "Works" One to many

    def __repr__(self):
        return f'<OrderClient {self.num_slab}, {self.number_part},{self.oreder_of_manufacture}, {self.part_works}, {self.deadline_part}>'


# create table preroduct
class PreProduct (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_order_client = db.Column(db.Integer, db.ForeignKey('order_client.id'), nullable=False)
    work_type = db.Column(db.Integer, db.ForeignKey('works.id'), nullable=False)


#create table performance_work
class PerformanceWork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    connection_work_slabs= db.Column(db.Integer, db.ForeignKey('slab_works.id'), nullable=False)
    connection_work_part = db.Column(db.Integer, db.ForeignKey('part_works.id'), nullable=False)
    connection_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    status_start = db.Column(db.Boolean, default=False, nullable = False)
    status_end = db.Column(db.Boolean, default=False, nullable=False)
    lead_time = db.Column(db.Integer, nullable=False)