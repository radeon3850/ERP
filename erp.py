from app import app, db
from app.models import User, PerformanceWork, SlabWorks, PreProduct, PartWorks, OrderManufacture, OrderClient, Clients, Works, Specialization


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User,
            'PerformanceWork': PerformanceWork, 'PreProduct': PreProduct,
            'PartWorks': PartWorks, 'SlabWorks': SlabWorks, 'OrderManufacture': OrderManufacture,
            'OrderClient': OrderClient, 'Clients': Clients, 'Works': Works}


if __name__ == "__main__":
    app.run(debug=True)