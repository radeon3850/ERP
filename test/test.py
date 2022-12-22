from flask import Flask, render_template
from  flask_sqlalchemy import SQLAlchemy



apl=Flask(__name__)
apl.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
apl.config['SECRET_KEY'] = 'some string'
base=SQLAlchemy(apl)


class Student(base.Model):
    id=base.Column('stident_id', base.Integer, primary_key=True)
    name=base.Column(base.String(100))
    city = base.Column(base.String(100))

    def __init__(self, name, city):
        self.name=name
        self.city=city

student = Student(name='Roman', city='Kiev')
base.session.add(student)
base.session.commit()



@apl.route('/')
@apl.route('/index')
def home():
    return 'My home page'





if __name__ == "__main__":
    base.create_all()
    apl.run(debug=True)