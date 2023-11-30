from app import app, db
from app.models import User, PerformanceWork, SlabWorks, PreProduct, PartWorks, OrderClient, Clients, Works, \
    Specialization

from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)



@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User,
            'PerformanceWork': PerformanceWork, 'PreProduct': PreProduct,'PartWorks': PartWorks, 'SlabWorks': SlabWorks,
            'OrderClient': OrderClient, 'Clients': Clients, 'Works': Works, 'Specialization':Specialization,
            }


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')