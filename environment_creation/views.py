from django.shortcuts import render, redirect
from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic.edit import FormView
from django.utils.datastructures import MultiValueDictKeyError

from braces import views as braces_mixins

from users.models import User

from .forms import ExcelImport

class ParseExcel(braces_mixins.LoginRequiredMixin, braces_mixins.StaffuserRequiredMixin, FormView):
    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'

    template_name = 'environment_creation/upload.html'
    form_class = ExcelImport
    success_url = reverse_lazy("subjects:home")

    def form_valid(self, form):
        
        return super().form_valid(form)

    def post(self, request, format=None):
        try:
            excel_file = request.FILES['excelFile']
        except MultiValueDictKeyError:
            return redirect(self.get_success_url())

        if (str(excel_file).split('.')[-1] == "xls"):
            data = xls_get(excel_file, column_limit = 12)
        elif (str(excel_file).split('.')[-1] == "xlsx"):
            data = xlsx_get(excel_file, column_limit = 12)

        users = data["Usuarios"]
        categories = data["Cursos"]
        subjects = data["Disciplinas"]

        if (len(users) > 1):
            for user in users:
                if (len(user) > 0):
                    if (user[0] != '#'):
                        if (len(user) < 5):
                            i = len(user)

                            while (i < 5):
                                user.append("")

                                i += 1

                        print(user)
                        """if not User.objects.filter(email = user[1]).exists():
                            User.objects.create(
                                email = user[1],
                                username = user[2],
                                last_name = user[3],
                                is_staff = user[4]
                            )"""

        return redirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        context = super(ParseExcel, self).get_context_data(**kwargs)

        context['title'] = _('Bulk Creation')

        return context
