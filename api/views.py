from django.shortcuts import render
from django.http import HttpResponse, JsonResponse


import django.views.generic as generic
from mural.models import SubjectPost, Comment, MuralVisualizations
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, date
from subjects.models import Subject

class ReportView(LoginRequiredMixin, generic.TemplateView):
    template_name = "api/report.html"

    def get_context_data(self, **kwargs):
        context = {}
        params = self.request.GET
       
        if params['subject_id'] and params['init_date'] and params['end_date']:
            subject_id = params['subject_id']
            subject = Subject.objects.get(id=subject_id)
            data = {}
            students = subject.students.all()
            formats = ["%d/%m/%Y", "%m/%d/%Y"] #so it accepts english and portuguese date formats
            for fmt in formats:
                try:
                    init_date = datetime.strptime(params['init_date'], fmt)
                    end_date = datetime.strptime(params['end_date'], fmt)
                except ValueError:
                    pass

            for student in students:
                interactions = {}
                #first columns
                interactions['subject_name'] = subject.name
                interactions['username'] = student.social_name
                interactions['init_date'] = init_date
                interactions['end_date'] = end_date
                print(datetime.now())
                #number of help posts created by the student
                interactions['doubts_count'] = SubjectPost.objects.filter(action="help", create_date__range=(init_date, end_date), 
                space__id=subject_id, user=student).count()

                help_posts = SubjectPost.objects.filter(action="help", create_date__range=(init_date, end_date), 
                space__id=subject_id)

                #comments count on help posts created by the student
                interactions['comments_count'] = Comment.objects.filter(post__in = help_posts.filter(user=student), 
                    create_date__range=(init_date, end_date)).count()
                

                #count the amount of comments made by the student on posts made by one of the professors
                interactions['comments_professor_count'] = Comment.objects.filter(post__in = help_posts.filter(user__in= subject.professor.all()), create_date__range=(init_date, end_date),
                 user=student).count()

                 #comments made by the user on other users posts
                interactions['comments_on_others_count'] = Comment.objects.filter(post__in = help_posts.exclude(user=student), 
                    create_date__range=(init_date, end_date),
                    user= student).count()
               
                
               
                comments_by_teacher = Comment.objects.filter(user__in=subject.professor.all())
                help_posts_ids = []
                for comment in  comments_by_teacher:
                    help_posts_ids.append(comment.post.id)
                 #number of help posts created by the user that the teacher commented on
                interactions['help_posts_commented_by_teacher'] = help_posts.filter(user=student, id__in = help_posts_ids)

               
                comments_by_others = Comment.objects.filter(user__in=subject.students.exclude(id = student.id))
                help_posts_ids = []
                for comment in  comments_by_teacher:
                    help_posts_ids.append(comment.post.id)
                #number of help posts created by the user others students commented on
                interactions['help_posts_commented_by_others'] = help_posts.filter(user=student, id__in = help_posts_ids).count()


                #Number of student visualizations on the mural of the subject
                interactions['mural_visualizations_count'] = MuralVisualizations.objects.filter(post__in = SubjectPost.objects.filter(space__id=subject.id),
                    user = student).count()
                print(datetime.now())

                data[student] = interactions
              
            print(data)


        return context
