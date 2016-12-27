from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, DeleteView
from .models import Category
from django.core.urlresolvers import reverse_lazy
from rolepermissions.verifications import has_role

from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.mixins import LoginRequiredMixin

from rolepermissions.mixins import HasRoleMixin
from .forms import CategoryForm

from subjects.models import Subject

class IndexView(LoginRequiredMixin, ListView):

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    queryset = Category.objects.all()
    template_name = 'categories/list.html'
    context_object_name = 'categories'


    def get_queryset(self):
        result = super(IndexView, self).get_queryset()

       	
        return result

    def render_to_response(self, context, **response_kwargs):
        if self.request.user.is_staff:
            context['page_template'] = "categories/home_admin_content.html"
        else:
            context['page_template'] = "categories/home_teacher_student.html"

        context['title'] = _('Home')

        if self.request.is_ajax():
            if self.request.user.is_staff:
                self.template_name = "categories/home_admin_content.html"
            else:
                self.template_name = "categories/home_teacher_student_content.html"

        return self.response_class(request = self.request, template = self.template_name, context = context, using = self.template_engine, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        list_categories = None
        categories = self.get_queryset().order_by('name')
        if has_role(self.request.user,'system_admin'):
            categories = self.get_queryset().order_by('name')
            
        elif has_role(self.request.user,'professor'):
        	pass
            #list_categories = self.get_queryset().filter(professors__in = [self.request.user]).order_by('name')
            # categorys_categories = CourseCategory.objects.filter(course_category__professors__name = self.request.user.name).distinct()
        elif has_role(self.request.user, 'student'):
            pass

        
        context['title'] = _('Categories')
        context['categories'] = categories

        return context

class CreateCategory(HasRoleMixin, CreateView):

    allowed_rules = ['system_admin']
    login_url = reverse_lazy('users:login')
    form_class = CategoryForm
    template_name = 'categories/create.html'
    success_url = reverse_lazy('categories:index')

    def form_valid(self, form):
        self.object = form.save()
        #TODO: Implement log calls
        return super(CreateCategory, self).form_valid(form)


class DeleteCategory(HasRoleMixin, DeleteView):

    login_url = reverse_lazy("users:login")
    redirect_field_name = 'next'
    model = Category
    template_name = 'categories/delete.html'


    def delete(self, request, *args, **kwargs):
        category = get_object_or_404(Category, slug = self.kwargs.get('slug'))
        subjects = Subject.objects.filter(category = category)
        print("aqui 3")
        if len(subjects) > 0:
            return HttpResponse(_('There are subjects attched to this category'))
       
        return super(DeleteCategory, self).delete(self, request, *args, **kwargs)

    def get_success_url(self):
        
        return reverse_lazy('categories:index')

