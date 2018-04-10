from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
import datetime

# Create your models here.

class ProfileManager(models.Manager):

	def get_or_create_profile(self, client_type, user_id, **kwargs):
		"""Находит подходящий профиль или создаёт новый и возвращает его"""
		
		query_set = super().filter(register_from=client_type, register_id=user_id)                   
		if len(query_set) > 0:
			profile = query_set[0]
		else:
			#Собираем данные для создания нового профиля
			params = {}
			for k,v in kwargs.items():
				params[k] = v

			params['register_from'] = client_type
			params['register_id'] = user_id
			#Передаём их в функцию - фабрику
			profile = self.create_new_pool(params)

		return profile


	def create_new_pool(self, **kwargs):
		"""Создаёт новый набор объектов, необходимый для 
		формирования профиля. А именно:
		- категорию по умолчанию
		- группу задач по умолчанию
		- сам профиль
		"""
		profile = super().create(**kwargs)
		
		default_category = Category.objects.create(
			name= 'default',
			profile= profile,
			is_default= True,
			is_active= True,
			completed_tasks= 0,
			spent_time= 0,
			last_activity= datetime.datetime.now()
			)

		default_group = Group.objects.create(
			name= 'default',
			category= default_category,
			is_default= True,
			is_active= True,
			completed_tasks= 0,
			spent_time= 0,
			last_activity= datetime.datetime.now()
			)

		return profile



class Profile(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	username = models.CharField(max_length=200, verbose_name=_("username"))
	register_from = models.CharField(max_length=200, verbose_name=_("register from"), default='telegram')
	register_id = models.IntegerField(null=True, blank=True, unique=True)
	completed_tasks = models.IntegerField(null=True, blank=True)
	spent_time = models.IntegerField(null=True, blank=True)
	last_activity = models.DateField()
	created_at = models.DateField(auto_now_add=True)

	def __unicode__(self):
		return self.username

	def __str__(self):
		return self.username

	class Meta:
		verbose_name = _("profile")
		verbose_name_plural = _("profiles")
		ordering = ["-created_at"]

	
class CategoryManager(models.Manager):
	def create_new_category(self, category_name, profile):
		category = super().create(
			name= category_name,
			profile= profile,
			completed_tasks= 0,
			spent_time= 0,
			last_activity= datetime.datetime.now()						
			)
		return group


class Category(models.Model):
	name = models.CharField(max_length=200, unique=True, verbose_name=_("category name"))
	profile = models.ForeignKey('Profile', on_delete=models.CASCADE, blank=True, null=True)
	parent = models.ForeignKey("Category", on_delete=models.CASCADE, blank=True)
	is_default = models.BinaryField(default=False)
	is_active = models.BinaryField(default=True)
	aim = models.TextField(verbose_name=_("what person want to get"), blank=True)
	completed_tasks = models.IntegerField(null=True, blank=True)
	spent_time = models.IntegerField(null=True, blank=True)
	last_activity = models.DateField(default=datetime.datetime.now())
	created_at = models.DateField(auto_now_add=True)

	def __unicode__(self):
		return self.name

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = _("category")
		verbose_name_plural = _("categories")
		ordering = ["-last_activity"]


class GroupManager(models.Manager):
	def create_new_group(self, group_name, category_name, profile):
		category = Category.objects.get(name=category_name, profile=profile)
		group = super().create(
			name= group_name,
			category= category,
			completed_tasks= 0,
			spent_time= 0,
			last_activity= datetime.datetime.now()						
			)
		return group


class Group(models.Model):
	name = models.CharField(max_length=200, verbose_name=_("programm name"))
	category = models.ForeignKey(Category, on_delete=models.CASCADE)
	is_default = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	description = models.TextField(verbose_name=_("what is this programm for"), blank=True)
	completed_tasks = models.IntegerField(null=True, blank=True)
	spent_time = models.IntegerField(null=True, blank=True)
	last_activity = models.DateField()
	created_at = models.DateField(auto_now_add=True)
	

	def __unicode__(self):
		return self.name

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = _("programm")
		verbose_name_plural = _("programms")
		ordering = ["-last_activity"]


class TaskManager(models.Manager):

	def create_new_task(self, task_name, group_name, category_name, profile):
		category = Category.objects.get(name=category_name, profile=profile)
		group = Group.objects.get(name=group_name, category=category)
		task = super().create(
			name= task_name,
			profile= profile,
			group= group,
			spent_time= 0,
			last_activity= datetime.datetime.now()			
			)
		return task


class Task(models.Model):
	name = models.CharField(max_length=200, verbose_name=_("task"))
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
	group = models.ForeignKey(Group, on_delete=models.CASCADE)
	is_finished = models.BooleanField(default=False)
	created_at = models.DateField(auto_now_add=True)
	plan_date = models.DateField(null=True, blank=True)
	finish_date = models.DateField(null=True, blank=True)
	spent_time = models.IntegerField(null=True, blank=True)
	last_activity = models.DateField()
	description = models.TextField(verbose_name=_("what is this task about"), blank=True)
	objects = TaskManager()


	def __unicode__(self):
		return self.name

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = _("task")
		verbose_name_plural = _("tasks")
		ordering = ["-finish_date"]


def user_directory_path(instance, filename):
		# file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
		return 'user_{0}/{1}'.format(instance.profile.id, filename)


class Achievment(models.Model):
	task = models.ForeignKey(Task, on_delete=models.CASCADE)
	upload = models.FileField(upload_to=user_directory_path)
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
	description = models.TextField(blank=True)    


	class Meta:
		verbose_name = _("achievment")
		verbose_name_plural = _("achievments")


class Transaction(models.Model):
	task = models.ForeignKey(Task, on_delete=models.CASCADE)
	spent_time = models.IntegerField()
	created_at = models.DateField(auto_now_add=True)

	class Meta:
		verbose_name = _("transaction")
		verbose_name_plural = _("transactions")
		ordering = ["-created_at"]
		


# Create your models here.
