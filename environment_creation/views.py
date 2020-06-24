import re, datetime
from django.shortcuts import render, redirect
from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic.edit import FormView
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

from braces import views as braces_mixins

from users.models import User
from categories.models import Category
from subjects.models import Subject, Tag

from .forms import ExcelImport


class ParseExcel(
    braces_mixins.LoginRequiredMixin, braces_mixins.StaffuserRequiredMixin, FormView
):
    login_url = reverse_lazy("users:login")
    redirect_field_name = "next"

    template_name = "environment_creation/upload.html"
    form_class = ExcelImport
    success_url = reverse_lazy("excel:import")

    def form_valid(self, form):
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        try:
            excel_file = request.FILES["excelFile"]
        except MultiValueDictKeyError:
            return redirect(self.get_success_url())

        if str(excel_file).split(".")[-1] == "xls":
            data = xls_get(excel_file, column_limit=15)
        elif str(excel_file).split(".")[-1] == "xlsx":
            data = xlsx_get(excel_file, column_limit=15)

        users = data["Usuarios"]
        categories = data["Cursos"]
        subjects = data["Disciplinas"]

        usersList = []
        usersErrors = []

        categoriesList = []
        categoriesErrors = []

        subjectsList = []
        subjectsErrors = []

        if len(users) > 1:
            usersList, usersErrors = importUsers(users)

        if len(categories) > 1:
            categoriesList, categoriesErrors = importCategories(categories, usersList)

        if len(subjects) > 1:
            subjectsList, subjectsErrors = importSubjects(
                subjects, usersList, categoriesList
            )

        messages.success(self.request, _("Environment imported successfully!"))

        context = self.get_context_data(**kwargs)
        context["usersErrors"] = usersErrors
        context["categoriesErrors"] = categoriesErrors
        context["subjectsErrors"] = subjectsErrors

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(ParseExcel, self).get_context_data(**kwargs)

        context["title"] = _("Bulk Creation")

        return context


def validateEmail(email):
    try:
        v_email = re.compile("[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}")

        if v_email.fullmatch(email) is None:
            return False

        return True
    except ValidationError:
        return False


def importUsers(usersSheet):
    usersList = []
    errorsList = []

    for user in usersSheet:
        if len(user) > 0:
            if user[0] != "#":
                if len(user) < 5:
                    i = len(user)

                    while i < 5:
                        user.append("")

                        i += 1

                if validateEmail(user[1]):
                    userDB = User.objects.filter(email=user[1])

                    if not userDB.exists():
                        if user[2].strip() != "" and user[3].strip() != "":
                            created = User.objects.create(
                                email=user[1],
                                username=user[2],
                                last_name=user[3],
                                is_staff=True if user[4] == "sim" else False,
                                password=make_password("amadeus"),
                            )

                            usersList.append(created)
                        else:
                            errorsList.append(
                                _("Line %s has username or lastname without values")
                                % (user[0])
                            )
                            usersList.append(None)
                    else:
                        usersList.append(userDB.get())
                else:
                    errorsList.append(_("Line %s has no valid email") % (user[0]))
                    usersList.append(None)

    return usersList, errorsList


def addCoordinators(category, coords, usersList):
    if len(coords) > 0:
        for coord in coords:
            if len(usersList) >= int(float(coord)):
                user = usersList[int(float(coord)) - 1]
                if not user is None and user not in category.coordinators.all():
                    category.coordinators.add(user)


def importCategories(categoriesSheet, usersList):
    categoriesList = []
    errorsList = []

    for category in categoriesSheet:
        if len(category) > 0:
            if category[0] != "#":
                if len(category) < 5:
                    i = len(category)

                    while i < 5:
                        category.append("")

                        i += 1

                if category[1].strip() != "":
                    categoryDB = Category.objects.filter(
                        name__unaccent__iexact=category[1]
                    )

                    coords = str(category[4]).split(";")

                    if not categoryDB.exists():
                        categoryDB = Category.objects.create(
                            name=category[1],
                            description=category[2],
                            visible=True if category[3] == "sim" else False,
                        )
                    else:
                        categoryDB = categoryDB.get()

                    addCoordinators(categoryDB, coords, usersList)

                    categoriesList.append(categoryDB)
                else:
                    errorsList.append(
                        _("Line %s has no value for name") % (category[0])
                    )
                    categoriesList.append(None)

    return categoriesList, errorsList


def validateSubjectInfo(subject):
    errorsList = []

    initSubDate = parse_datetime(str(subject[5]))

    if initSubDate is None:
        errorsList.append(
            _("Line %s doesn't have a valid subscription init date") % (subject[0])
        )
    elif initSubDate.date() < datetime.datetime.today().date():
        errorsList.append(
            _("Line %s has the subscription init date before today's date")
            % (subject[0])
        )

    endSubDate = parse_datetime(str(subject[6]))

    if endSubDate is None:
        errorsList.append(
            _("Line %s doesn't have a valid subscription end date") % (subject[0])
        )
    elif initSubDate is None or endSubDate.date() < initSubDate.date():
        errorsList.append(
            _("Line %s has the subscription end date before subscription init date")
            % (subject[0])
        )

    initDate = parse_datetime(str(subject[7]))

    if initDate is None:
        errorsList.append(_("Line %s doesn't have a valid init date") % (subject[0]))
    elif endSubDate is None or initDate.date() <= endSubDate.date():
        errorsList.append(
            _("Line %s has the init date before or equal subscription end date")
            % (subject[0])
        )

    endDate = parse_datetime(str(subject[8]))

    if endDate is None:
        errorsList.append(_("Line %s doesn't have a valid end date") % (subject[0]))
    elif initDate is None or endDate.date() < initDate.date():
        errorsList.append(
            _("Line %s has the end date before the init date") % (subject[0])
        )

    return errorsList


def addProfessors(subject, profs, usersList):
    if len(profs) > 0:
        for prof in profs:
            if len(usersList) >= int(float(prof)):
                user = usersList[int(float(prof)) - 1]
                if not user is None and not user in subject.professor.all():
                    subject.professor.add(user)


def addStudents(subject, students, usersList):
    if len(students) > 0:
        for student in students:
            if len(usersList) >= int(float(student)):
                user = usersList[int(float(student)) - 1]
                if not user is None and not user in subject.students.all():
                    subject.students.add(user)


def addTags(subject, tags):
    if len(tags) > 0:
        for tag in tags:
            tag = tag.strip()

            exist = Tag.objects.filter(name=tag).exists()

            if exist:
                new_tag = Tag.objects.get(name=tag)
            else:
                new_tag = Tag.objects.create(name=tag)

            if not new_tag in subject.tags.all():
                subject.tags.add(new_tag)


def importSubjects(subjectsSheet, usersList, categoriesList):
    subjectsList = []
    errorsList = []

    for subject in subjectsSheet:
        if len(subject) > 0:
            if subject[0] != "#":
                if len(subject) < 14:
                    i = len(subject)

                    while i < 14:
                        subject.append("")

                        i += 1

                errorsList = validateSubjectInfo(subject)

                if len(errorsList) == 0:
                    if subject[1].strip() != "":
                        if (
                            len(categoriesList) >= int(subject[4])
                            and not categoriesList[int(subject[4]) - 1] is None
                        ):
                            subjectDB = Subject.objects.filter(
                                name__unaccent__iexact=subject[1],
                                category=categoriesList[int(subject[4]) - 1],
                            )

                            if not subjectDB.exists():
                                subjectDB = Subject.objects.create(
                                    name=subject[1],
                                    description_brief=subject[2],
                                    description=subject[3],
                                    category=categoriesList[int(subject[4]) - 1],
                                    subscribe_begin=parse_datetime(str(subject[5])),
                                    subscribe_end=parse_datetime(str(subject[6])),
                                    init_date=parse_datetime(str(subject[7])),
                                    end_date=parse_datetime(str(subject[8])),
                                    visible=True if subject[9] == "sim" else False,
                                    display_avatar=True
                                    if subject[12] == "sim"
                                    else False,
                                )
                            else:
                                subjectDB = subjectDB.get()

                            profs = str(subject[10]).split(";")
                            students = str(subject[11]).split(";")
                            tags = subject[13].split(";")

                            print(profs)

                            addProfessors(subjectDB, profs, usersList)
                            addStudents(subjectDB, students, usersList)
                            addTags(subjectDB, tags)

                            subjectsList.append(subjectDB)
                        else:
                            errorsList.append(
                                _("Line %s has no valid value for course")
                                % (subject[0])
                            )
                            subjectsList.append(None)
                    else:
                        errorsList.append(
                            _("Line %s has no value for name") % (subject[0])
                        )
                        subjectsList.append(None)
                else:
                    subjectsList.append(None)

    return subjectsList, errorsList
