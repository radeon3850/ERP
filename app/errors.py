from flask import render_template
from app import app, db


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html', title='error 404'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html', title='error 500'), 500

# this commented code from file route.py for check to check function calls - errors 404, 500

from flask import abort
@app.route('/error404')
def error_404():
    # Спровокуємо помилку 404
    abort(404)

@app.route('/error500')
def error_500():
    # Спровокуємо помилку 500
    abort(500)
