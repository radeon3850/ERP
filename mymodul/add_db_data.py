from app.models import db


def add_data(self):
    try:
        db.session.add(self)  # add data to table OrderClient
        db.session.commit()
    except Exception as error:
        db.session.rollback()  # Відміна змін у разі помилки
        return f'An error occurred: {str(error)}', 500


if __name__ == '__main__':
    add_data()
