from . import report_blueprint
from flask import render_template,render_template, request, jsonify, g, send_file
from datetime import datetime
from xlsxwriter.workbook import Workbook
import io
from sqlalchemy import and_
from datetime import datetime, timedelta
from flask_login import current_user

access_list=['архитектор', 'начальник производства', 'главный менеджер', 'директор', 'менеджер']


@report_blueprint.route('/report')
def report():
    # checking whether access is allowed to the user
    if current_user.employee.job_title in access_list:
        from app.models import StatisticsUser
        from app.forms import AddWorker
        current_page = 'Стоимость работ'
        get_all_statistic = StatisticsUser.query.all()
        # list_work = [work for work in get_all_statistic]
        list_who_see_report_id_specialisation = [4,6]
        form_worker = AddWorker()

        return render_template('report.html', all_statistic=get_all_statistic, title = 'Отчёты',
                               current_page=current_page, who_see_link_report=list_who_see_report_id_specialisation,
                               form=form_worker)
    else:
        return render_template('error_access.html')

def filter_data_by_date(start_date, end_date, username):
    from app.models import StatisticsUser
    all_statistic_data = StatisticsUser.query.all()
    data = []
    g.filtered_data = None
    for value in all_statistic_data:
        statistict_dict ={
            "name" : f'{value.query_user.first_name} {value.query_user.last_name}',
            "work_title" : value.query_works.work_title,
            "work_type" : value.query_works.work_type,
            "work_kind": value.query_works.work_kind,
            "value_work": value.value_work,
            "date" : value.date_fact_end.strftime('%Y-%m-%d'),
            "costs" : value.price_work
        }
        data.append(statistict_dict)

    if len(start_date)!=0 or len(end_date)!=0:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        g.filtered_data = [entry for entry in data if start <= datetime.strptime(entry["date"], "%Y-%m-%d") <= end]
        if username != "Выбрать из списка":
            g.filtered_data = [entry for entry in g.filtered_data if entry["name"] == username]
            return g.filtered_data
    else: g.filtered_data = [entry for entry in data ]


    return g.filtered_data


@report_blueprint.route('/get_data', methods=['GET'])
def get_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    username = request.args.get('username')  # Додайте обробку параметра username

    filtered_data = filter_data_by_date(start_date, end_date, username)
    return jsonify(filtered_data)


@report_blueprint.route('/generate_excel', methods=['GET'])
def generate_excel():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    username = request.args.get('username')


    # Отримання відфільтрованих даних з бази даних (аналогічно вашому коду)
    filtered_data = filter_data_by_date(start_date, end_date, username)

    # Створення Excel-файлу
    output = io.BytesIO()
    workbook = Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Додавання рядка з назвами стовпців
    header_row = ["Исполнитель","Вид работ", "Тип работ", "Подтип работ", "Значение", "Дата завершения", "Стоимость работы"]
    for col, title in enumerate(header_row):
        worksheet.write(0, col, title)

    # Встановлення коліру фону для шапки
    header_format = workbook.add_format({'bold': True, 'bg_color': '#00BFFF'})  # Встановіть потрібний колір
    worksheet.set_row(0, cell_format=header_format)

    # Заповнення Excel-файлу даними
    for row, record in enumerate(filtered_data, start=1):
        worksheet.write(row, 0, record["name"])
        worksheet.write(row, 1, record["work_title"])
        worksheet.write(row, 2, record["work_type"])
        worksheet.write(row, 3, record["work_kind"])
        worksheet.write(row, 5, record["value_work"])
        worksheet.write(row, 5, record["date"])
        worksheet.write(row, 6, record["costs"])

    workbook.close()
    output.seek(0)

    # переназначение переменной для получения названия "всяя статистика" если не выбран" пользователь
    if username == "Выбрать из списка":
        username = "Вся статистика"

    # Відправка Excel-файлу користувачу
    return send_file(output, attachment_filename=f'Cтатистика_{username}_{start_date}_{end_date}.xlsx', as_attachment=True)


@report_blueprint.route('/reportworkcount', methods=['GET', 'POST'])
def reportworkcount():
    # checking whether access is allowed to the user
    if current_user.employee.job_title in access_list:
        from app.forms import AddWorker
        from ..models import StatisticsUser, User
        from app import db
        form_worker = AddWorker()

        current_page = "Количество работ"
        #this block code for show some static information in table
        get_list_all_work_finish = db.session.query(StatisticsUser).filter(StatisticsUser.id_works <= 57).all() #Все работы законченные для слябов и деталей
        get_count_user_work = db.session.query(StatisticsUser.id_user).distinct().filter(StatisticsUser.id_works <= 57).all()# получение уникальных значений (юзеров выполнявших работу)
        all_time_work = db.session.query(db.func.sum(StatisticsUser.all_time_work))\
        .filter(StatisticsUser.id_works <= 57)\
        .scalar() # cумма по столбцу all_time_work - время работы
        average_time_work = round((all_time_work/len(get_list_all_work_finish))*60, 2) # среднее время работы
        average_count_work_user = (len(get_list_all_work_finish)/len(get_count_user_work)) # среднее количество работ на сотрудника

        today = datetime.now()

        # Визначте початок і кінець поточного робочого тижня (пн-пт)
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=4)
        # Виберіть дані з бази даних за поточний робочий тиждень
        data_for_current_week = StatisticsUser.query.filter(
            StatisticsUser.date_fact_end>=start_of_week,
            StatisticsUser.date_fact_end<=end_of_week, StatisticsUser.id_works <= 57).all()

        number_ofworks_this_week = len(data_for_current_week) # number of works completed

        # Для отримання даних минулого тижня змініть діапазон дат
        start_of_last_week = start_of_week - timedelta(days=7)
        end_of_last_week = end_of_week - timedelta(days=7)

        data_for_last_week = StatisticsUser.query.filter(
            StatisticsUser.date_fact_end >= start_of_last_week,
            StatisticsUser.date_fact_end <= end_of_last_week,
            StatisticsUser.id_works <= 57
        ).all()

        # print(average_count_work_user)
        list_user_statistic_work = []
        for id_user in get_count_user_work:
            #get all work (we need count of work)
            all_work_of_user = db.session.query(StatisticsUser)\
            .filter(StatisticsUser.id_user == id_user[0], StatisticsUser.id_works <= 57)\
            .all()

            # sum all time for all work
            all_work_time = db.session.query(db.func.sum(StatisticsUser.all_time_work)) \
                .filter(StatisticsUser.id_user == id_user[0], StatisticsUser.id_works <= 57) \
                .scalar()
            # print(id_user[0])
            user = User.query.get(id_user) # get user from db than get their first- and last-name
            average_time = round((all_work_time*60)/len(all_work_of_user), 1) #calculate average time/work
            # dict data that we adding to list
            dict_statistic = {
                'name' : f'{user.first_name} {user.last_name}',
                'specialization' : user.employee.job_title,
                'count_work' : len(all_work_of_user),
                'average_time_work' : average_time
            }

            list_user_statistic_work.append(dict_statistic) # add dict to list for render it to table on page

        # dict that we show some statistic on page
        dict_work = {
            'count': len(get_list_all_work_finish),
            'average_time_work': average_time_work,
            'count_worker': average_count_work_user,
            'count_week': number_ofworks_this_week
        }

        return render_template('report_work_count.html', title='Отчёты',
                               current_page=current_page, form=form_worker, dict_work=dict_work,
                               list_statistic=list_user_statistic_work)
    return render_template('error_access.html')

@report_blueprint.route('/filter_data', methods=['POST'])
def filter_data():
    from ..models import StatisticsUser, User
    from app import db

    g.filtered_data=[] # create list
    g.get_filter_statistic = None
    g.count_user = None
    # Отримання параметрів фільтра з AJAX-запиту
    worker = request.form.get('worker')
    startDate = request.form.get('startDate')
    endDate = request.form.get('endDate')


    # get all worker that after filters
    if startDate and endDate and worker:
        # get filtered data from DB
        g.get_filter_statistic = db.session.query(StatisticsUser)\
                    .filter(StatisticsUser.id_works <= 57,
                    StatisticsUser.date_fact_end >= startDate,
                    StatisticsUser.date_fact_end <= endDate).filter_by(id_user=worker)\
                    .all()

    elif startDate and endDate:
        # get filtered data from DB
        g.get_filter_statistic = db.session.query(StatisticsUser).filter(StatisticsUser.id_works <= 57,
                                                                    StatisticsUser.date_fact_end >= startDate,
                                                                    StatisticsUser.date_fact_end <= endDate).all()

    else:
        # get filtered data from DB
        g.get_filter_statistic =db.session.query(StatisticsUser).filter(StatisticsUser.id_works <= 57).all()

    uniq_user_list = set([user.id_user for user in g.get_filter_statistic]) #get unic count of worker taht
    number=0
    #iter data unic list
    for user in uniq_user_list:
        number+=1 # number in table
        count_work = len([work for work in g.get_filter_statistic if work.id_user==user]) # The number of works that the employee completed
        all_user_time_work = sum([time.all_time_work for time in g.get_filter_statistic if time.id_user==user ]) # time of all work performed
        average_time = all_user_time_work / count_work*60 # average time of work
        name = User.query.get(user) # get data user if id=user

    # Return the result in JSON format
        dict_data = {
                'number': number,
                'worker': f'{name.first_name} {name.last_name}',
                'specialization':name.employee.job_title,
                'workCount': count_work,
                'averageTime': round(average_time,2)
            }
        g.filtered_data.append(dict_data) # append dict to list "filtered_data"

    return jsonify(g.filtered_data)