from django.contrib import admin
from .models import User
from .forms import ProfileForm

class UserAdmin(admin.ModelAdmin):
	list_display = ['username', 'name', 'email', 'is_staff', 'is_active']
	search_fields = ['username', 'name', 'email']
	form = ProfileForm

admin.site.register(User, UserAdmin)