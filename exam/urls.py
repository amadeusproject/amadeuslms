from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^create/(?P<slug>[\w\-_]+)/$', views.CreateExam.as_view(), name='create_exam'), # exam slug
	url(r'^update/(?P<slug>[\w\-_]+)/$', views.UpdateExam.as_view(), name='update_exam'), # topic slug
	url(r'^view/(?P<slug>[\w\-_]+)/$', views.ViewExam.as_view(), name='view_exam'), # exam slug
	url(r'^delete/(?P<slug>[\w\-_]+)/$', views.DeleteExam.as_view(), name='delete_exam'), # exam
	url(r'^answer/$', views.AnswerExam.as_view(), name='answer_exam'), # exam
	url(r'^answer-exam/(?P<slug>[\w\-_]+)/$', views.AnswerStudentExam.as_view(), name='answer_student_exam'), # exam slug


	url(r'^discursive-question/$',views.DiscursiveQuestion.as_view(), name="discursive_question"),
	url(r'^gap-filling-question/$',views.GapFillingQuestion.as_view(), name="gap_filling_question"),
	url(r'^gap-filling-answer/$',views.GapFillingAnswer.as_view(), name="gap_filling_answer"),
	url(r'^multiple-choice-question/$',views.MultipleChoiceQuestion.as_view(), name="multiple_choice_question"),
	url(r'^multiple-choice-answer/$',views.MultipleChoiceAnswer.as_view(), name="multiple_choice_answer"),
	url(r'^true-or-false-question/$',views.TrueOrFalseQuestion.as_view(), name="true_or_false_question"),
	url(r'^true-or-false-answer/$',views.TrueOrFalseAnswer.as_view(), name="true_or_false_answer"),
]
