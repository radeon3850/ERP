from flask import Blueprint

report_blueprint = Blueprint('report', __name__, template_folder='templates')

from .report import report

report_blueprint.add_url_rule('/report', 'report', report)
