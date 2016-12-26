from django.contrib import admin
from .models import User
from .forms import UserForm

class UserAdmin(admin.ModelAdmin):
	list_display = ['username', 'social_name', 'email', 'is_staff', 'is_active']
	search_fields = ['username', 'social_name', 'email']
	form = UserForm

admin.site.register(User, UserAdmin)