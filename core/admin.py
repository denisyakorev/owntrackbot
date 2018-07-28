from django.contrib import admin
from core.models import Profile, Category, Group, Task, Transaction

class TaskAdmin(admin.ModelAdmin):
	list_display=('name', 'profile', 'group', 'is_finished', 'finish_date')
	search_fields = ('name', 'profile', 'group')
	list_filter = ('is_finished',)
	date_hierarchy = 'finish_date'
	ordering = ('profile', 'group', 'name')

class GroupAdmin(admin.ModelAdmin):
	list_display=('name', 'profile', 'category', 'is_active')
	search_fields = ('name', 'profile', 'category')
	list_filter = ('is_active',)
	ordering = ('profile', 'category', 'name')

class CategoryAdmin(admin.ModelAdmin):
	list_display=('name', 'profile', 'is_active')
	search_fields = ('name', 'profile')
	list_filter = ('is_active',)
	ordering = ('profile', 'name')

class TransactionAdmin(admin.ModelAdmin):
	list_display=('task', 'spent_time', 'created_at')
	search_fields = ('task',)
	date_hierarchy = 'created_at'
	ordering = ('-created_at',)


# Register your models here.
admin.site.register(Profile)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Transaction, TransactionAdmin)



