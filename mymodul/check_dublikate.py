from app.models import SlabWorks, PartWorks

def is_duplicate_slab(data_slab):
    existing_slab = SlabWorks.query.filter(
        SlabWorks.number_slab == data_slab.number_slab,
        SlabWorks.order_of_client == data_slab.order_of_client,
        SlabWorks.slab_works == data_slab.slab_works,
        SlabWorks.stone_id == data_slab.stone_id).first()
    return existing_slab is not None

def is_duplicate_part(data_part):  # check if dublicate in DB
    existing_part = PartWorks.query.filter(
        PartWorks.number_part == data_part.number_part,
        PartWorks.order_of_client == data_part.order_of_client,
        PartWorks.part_works == data_part.part_works,
        PartWorks.stone_id == data_part.stone_id).first()  # compares if the form data and the data from the database are the same
    return existing_part is not None

if __name__ == '__main__':
    is_duplicate_slab()
    is_duplicate_part()