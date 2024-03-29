from flask import render_template
from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_required

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        allowed_user_ids = ['главный менеджер', 'директор']  # List of user IDs that have access to the admin panel
        if current_user.employee.job_title in allowed_user_ids:
            return current_user.is_authenticated
        return False

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return render_template('admin/forbidden.html')
        return super(MyAdminIndexView, self)._handle_view(name, **kwargs)


