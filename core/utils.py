from core.models import Profile, Category, Group, Task, Transaction
from django.db.models import Sum

def update_all_profile_objects(profile):
	"""
	Update spent_time counter and completed_tasks counter 
	for all profile objects
	"""
	tasks = Task.objects.filter(profile=profile)
	transactions = Transaction.objects.all()
	groups = Group.objects.filter(profile=profile)
	categories = Category.objects.filter(profile=profile)
	
	for task in tasks:
		task.spent_time = Transaction.objects.filter(task=task).aggregate(Sum('spent_time'))['spent_time__sum']
		task.save()

	for group in groups:
		group.spent_time = Task.objects.filter(group=group).aggregate(Sum('spent_time'))['spent_time__sum']
		group.completed_tasks = Task.objects.filter(is_finished=True, group=group).count()
		group.save()

	for cat in categories:
		cat.spent_time = Group.objects.filter(category=cat).aggregate(Sum('spent_time'))['spent_time__sum']
		cat.completed_tasks = Group.objects.filter(category=cat).aggregate(Sum('completed_tasks'))['completed_tasks__sum']
		cat.save()

	profile.spent_time = Category.objects.filter(profile=profile).aggregate(Sum('spent_time'))['spent_time__sum']
	profile.completed_tasks = Category.objects.filter(profile=profile).aggregate(Sum('completed_tasks'))['completed_tasks__sum']
	profile.save()