from app.models import PreProduct, SlabWorks, PartWorks, PerformanceWork


def all_work_order(order):
    work_order_preproduct = PreProduct.query.filter_by(order_of_client=order).all()
    work_order_slab = SlabWorks.query.filter_by(order_of_client=order).all()
    work_order_part = PartWorks.query.filter_by(order_of_client=order).all()

    all_work = work_order_preproduct + work_order_slab + work_order_part

    return all_work


def get_status_previous(order, sequence):
    for i in all_work_order(order):
        if i.work_sequence == f'{sequence}':
            if i.__class__ == PreProduct:
                for status in i.query_preproduct:
                    return status.status_end
            if i.__class__ == SlabWorks:
                for status in i.query_slabworks:
                    return status.status_end
            if i.__class__ == PartWorks:
                for status in i.query_partworks:
                    return status.status_end


def get_work_sequence(id_works):
    get_work = PerformanceWork.query.get(id_works)
    if get_work.id_preproduct != None:
        sequence = PreProduct.query.get(get_work.id_preproduct)
        return sequence.work_sequence
    if get_work.id_work_slabs != None:
        sequence = SlabWorks.query.get(get_work.id_work_slabs)
        return sequence.work_sequence
    if get_work.id_work_part != None:
        sequence = PartWorks.query.get(get_work.id_work_part)
        return sequence.work_sequence


if __name__ == '__main__':
    all_work_order()
    get_status_previous()
    get_work_sequence()
