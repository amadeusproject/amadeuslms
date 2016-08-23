from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
	return render(request, "app/index.html")

@login_required
def test(request):
	return render(request, "admin_index.html")

@login_required
def participantes_curso(request):
	return render(request, "admin_participantes_curso.html")

@login_required
def avaliacao_curso(request):
	return render(request, "admin_avaliacao_curso.html")

@login_required
def email(request):
	return render(request, "admin_send_email.html")

@login_required
def profile(request):
	return render(request, "admin_profile.html")

@login_required
def edit_profile(request):
	return render(request, "admin_editar_perfil.html")

@login_required
def reset_pass(request):
	return render(request, "admin_reset_pass.html")

@login_required
def colegas(request):
	return render(request, "admin_colegas_curso.html")

@login_required
def configuracoes(request):
	return render(request, "admin_config.html")

@login_required
def mobile(request):
	return render(request, "mobile.html")

@login_required
def tarefas(request):
	return render(request, "admin_tarefas.html")

@login_required
def users_online(request):
	return render(request, "admin_online.html")

@login_required
def search(request):
	return render(request, "admin_search.html")