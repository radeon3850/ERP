from app.models import PerformanceWork, PreProduct, SlabWorks, PartWorks

"""this function calculate the progress of the customer's order"""
def progres(order_id):
    # Get all_work from table PreProduct, SlabWorks, PartWorks iforder == "oreder_id" and status_start==None
    get_all_preproduct_none = PreProduct.query.filter_by(order_of_client=order_id) \
        .join(PerformanceWork, PerformanceWork.id_preproduct == PreProduct.id) \
        .filter(PerformanceWork.status_end.is_(None)).all()
    get_all_slabworks_none = SlabWorks.query.filter_by(order_of_client=order_id) \
        .join(PerformanceWork, PerformanceWork.id_work_slabs == SlabWorks.id) \
        .filter(PerformanceWork.status_end.is_(None)).all()
    get_all_partworks_none = PartWorks.query.filter_by(order_of_client=order_id) \
        .join(PerformanceWork, PerformanceWork.id_work_part == PartWorks.id) \
        .filter(PerformanceWork.status_end.is_(None)).all()

    #create list all work thah isn't started the job
    get_all_work_none = get_all_preproduct_none + get_all_slabworks_none + get_all_partworks_none

    # Get all_work from table PreProduct, SlabWorks, PartWorks iforder == "oreder_id" and status_end==True
    get_all_preproduct = PreProduct.query.filter_by(order_of_client=order_id) \
        .join(PerformanceWork, PerformanceWork.id_preproduct == PreProduct.id) \
        .filter(PerformanceWork.status_end == 1).all()
    get_all_slabworks = SlabWorks.query.filter_by(order_of_client=order_id) \
        .join(PerformanceWork, PerformanceWork.id_work_slabs == SlabWorks.id) \
        .filter(PerformanceWork.status_end == 1).all()
    get_all_partworks = PartWorks.query.filter_by(order_of_client=order_id) \
        .join(PerformanceWork, PerformanceWork.id_work_part == PartWorks.id) \
        .filter(PerformanceWork.status_end == 1).all()

    # create list all work thah is ending
    get_all_work_true = get_all_preproduct + get_all_slabworks + get_all_partworks

    try :
        progres = (len(get_all_work_true)) / (len(get_all_work_true) + len(get_all_work_none)) * 100 #this formula calculate precent
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    if len(get_all_work_true) == 0:
        progres = 0.0


    return progres


if __name__=="__main__":
    progres()