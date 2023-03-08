"""Как получать данные с формы HTML без использования wtf_form"""
# if request.method == 'POST':
#     number = request.form['number']
#     thickness = request.form['thickness']
#     type = request.form['type']
#     if len(number) == 0 or len(thickness) == 0 or len(type) == 0:
#         print("Поля формы пустые")
#         flash('Заполенены не все поля формы добавления сляба')
#
#     elif order_client.id == q and check_data.number_slab == number:
#         flash('Сляб с такими параметрами уже добавлен')
#     else:
#         slab_data = SlabWorks(number_slab=number, thickness=thickness, oreder_of_client=order_client.id,
#                               slab_works=0,
#                               set_worker=0)
#         db.session.add(slab_data)
#         db.session.commit()
#         flash('Сляб добавлен к карте заказа')
#         return render_template("add_slab.html", title='Добавление слябов', user=user, order_client=order_client)