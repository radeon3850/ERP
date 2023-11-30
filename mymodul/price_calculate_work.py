from app.models import PriсeWork

def get_price_work(stone, thickness, get_price, work):
    # iteration dictionary where keys there is a tupl (stone, thickness) and their values in get_price
    if work.query_slabworks or work.query_partworks:
        price_mapping = {
            (1, 2): get_price.marble_2sm,
            (1, 3): get_price.marble_3sm,
            (2, 2): get_price.granite_import_2sm,
            (2, 3): get_price.granite_import_3sm,
            (3, 2): get_price.granite_uk_2sm,
            (3, 3): get_price.granite_uk_3sm,
            (4, 2): get_price.travertine_2sm,
            (4, 3): get_price.travertine_3sm,
            (5, 2): get_price.onyx_2sm,
            (5, 3): get_price.onyx_3sm,
        }
        price = float(price_mapping.get((stone, thickness), 0))

        return price


def calculate_price_work(work):
    stone = None
    thickness = None
    value = None
    get_price = None
    price_work = None
    # in block if - check what kind of work
    if work.query_slabworks:
        stone = int(work.query_slabworks.stone_id)
        thickness = int(work.query_slabworks.thickness)
        if "," in work.query_slabworks.value:
            correct_value = (work.query_slabworks.value).replace(",", ".")
            value = float(correct_value)
        else:
            value = float(work.query_slabworks.value)
        get_price = PriсeWork.query.get(work.query_slabworks.slab_works)

    if work.query_partworks:
        stone = int(work.query_partworks.stone_id)
        thickness = int(work.query_partworks.thickness)
        if "," in work.query_partworks.value:
            correct_value = (work.query_partworks.value).replace(",", ".")
            value = float(correct_value)
        else:
            value = float(work.query_partworks.value)
        get_price = PriсeWork.query.get(work.query_partworks.part_works)

    if work.query_slabworks or work.query_partworks:
        price = get_price_work(stone=stone, thickness=thickness, get_price=get_price, work=work)
        price_work = float(price) * float(value)
        return price_work





if __name__ == '__main__':
    calculate_price_work()