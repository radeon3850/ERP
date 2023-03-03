from app import app, db
from app.models import User, PerformanceWork, SlabWorks, PreProduct, PartWorks, OrderClient, Clients, Works, Specialization, UploadFile


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User,
            'PerformanceWork': PerformanceWork, 'PreProduct': PreProduct,
            'PartWorks': PartWorks, 'SlabWorks': SlabWorks,
            'OrderClient': OrderClient, 'Clients': Clients, 'Works': Works}


if __name__ == "__main__":
    app.run(debug=True)