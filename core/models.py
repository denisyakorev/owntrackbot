from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
import datetime
from django.utils import timezone

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
			profile = self.create_new_pool(**params)

		return profile


	def get_profile_info(self, profile):
		"""
		Возвращает информацию о категории:
		- название категории
		- суммарное время, затраченное на задачи категории
		- количество выполненных задач
		- дата последней активности		
		- перечень входящих в категорию групп 
		с временем, затраченным на них				
		
		"""
		categories = Category.objects.filter(profile=profile)
		
		categories_info = ""
		for category in categories:
			categories_info += category.name+": "+ category.spent_time + "\n"
		
		info = [
			
		{
			'param_name':_('spent time'),
			'param_value': profile.spent_time 
		},
		{
			'param_name':_('completed tasks'),
			'param_value': profile.completed_tasks 
		},
		{
			'param_name':_('last activity'),
			'param_value': profile.last_activity 
		},
		{
			'param_name':_('info about categories in profile'),
			'param_value': categories_info 
		}

		]

		return info



	def create_new_pool(self, **kwargs):
		"""Создаёт новый набор объектов, необходимый для 
		формирования профиля. А именно:
		- категорию по умолчанию
		- группу задач по умолчанию
		- сам профиль
		"""
		profile = super().create(**kwargs)
		cur_time = timezone.now()
		
		default_category = Category(
			name= 'default',
			profile= profile,
			is_default= True,
			is_active= True,
			completed_tasks= 0,
			spent_time= 0
			)
		default_category.save()

		default_group = Group(
			name= 'default',
			category= default_category,
			is_default= True,
			is_active= True,
			completed_tasks= 0,
			spent_time= 0
			)
		default_group.save()

		return profile



class Profile(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	username = models.CharField(max_length=200, verbose_name=_("username"))
	register_from = models.CharField(max_length=200, verbose_name=_("register from"), default='telegram')
	register_id = models.IntegerField(null=True, blank=True, unique=True)
	completed_tasks = models.IntegerField(null=True, blank=True)
	spent_time = models.IntegerField(null=True, blank=True)
	last_activity = models.DateField(default=timezone.now())
	created_at = models.DateField(auto_now_add=True)
	objects = ProfileManager()

	def __unicode__(self):
		return self.username

	def __str__(self):
		return self.username

	class Meta:
		verbose_name = _("profile")
		verbose_name_plural = _("profiles")
		ordering = ["-created_at"]


	def update_profile(self):
		self.last_activity = datetime.datetime.now()
		self.spent_time = 0
		self.completed_tasks = 0
		categories = Category.objects.filter(profile=self)
		for category in categories:
			self.spent_time += category.minutes
			self.completed_tasks += category.completed_tasks

		self.save()		
		return True

	
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


	def get_category_info(self, category_name, profile):
		"""
		Возвращает информацию о категории:
		- название категории
		- суммарное время, затраченное на задачи категории
		- количество выполненных задач
		- дата последней активности		
		- перечень входящих в категорию групп 
		с временем, затраченным на них				
		
		"""
		category = Category.objects.get(name=category_name, profile=profile)
		groups = Group.objects.filter(category=category)
		
		groups_info = ""
		for group in groups:
			groups_info += group.name+": "+ group.spent_time + "\n"
		
		info = [
			
		{
			'param_name':_('spent time'),
			'param_value': category.spent_time 
		},
		{
			'param_name':_('completed tasks'),
			'param_value': category.completed_tasks 
		},
		{
			'param_name':_('last activity'),
			'param_value': category.last_activity 
		},
		{
			'param_name':_('info about groups in category'),
			'param_value': groups_info 
		}

		]

		return info


class Category(models.Model):
	name = models.CharField(max_length=200, unique=True, verbose_name=_("category name"))
	profile = models.ForeignKey('Profile', on_delete=models.CASCADE, blank=True, null=True)
	parent = models.ForeignKey("Category", on_delete=models.CASCADE, blank=True)
	is_default = models.BinaryField(default=False)
	is_active = models.BinaryField(default=True)
	aim = models.TextField(verbose_name=_("what person want to get"), blank=True)
	completed_tasks = models.IntegerField(null=True, blank=True)
	spent_time = models.IntegerField(null=True, blank=True)
	last_activity = models.DateField(default=timezone.now())
	created_at = models.DateField(auto_now_add=True)

	def __unicode__(self):
		return self.name

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = _("category")
		verbose_name_plural = _("categories")
		ordering = ["-last_activity"]


	def update_category(self):
		self.last_activity = datetime.datetime.now()
		self.spent_time = 0
		self.completed_tasks = 0
		groups = Group.objects.filter(category=self)
		for group in groups:
			self.spent_time += group.minutes
			self.completed_tasks += group.completed_tasks

		self.save()
		self.profile.update_profile()
		return True


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


	def get_group_info(self, group_name, category_name, profile):
		"""
		Возвращает информацию о группе задач:
		- название группы
		- дата создания
		- название категории
		- суммарное время, затраченное на задачи группы
		- количество выполненных задач
		- дата последней активности		
		- перечень входящих в группу активных задач 
		с временем, затраченным на них				
		
		"""
		category = Category.objects.get(name=category_name, profile=profile)
		group = super().get(name=group_name, category=category)
		tasks = Task.objects.filter(group= group, is_finished= False)
		tasks_info = ""
		for task in tasks:
			tasks_info += task.name+": "+ task.spent_time + "\n"
		
		info = [
		{
			'param_name':_('name'),
			'param_value': group.name 
		},
		{
			'param_name':_('created at'),
			'param_value': group.created_at 
		},
		{
			'param_name':_('category'),
			'param_value': group.category.name 
		},		
		{
			'param_name':_('spent time'),
			'param_value': group.spent_time 
		},
		{
			'param_name':_('completed tasks'),
			'param_value': group.completed_tasks 
		},
		{
			'param_name':_('last activity'),
			'param_value': group.last_activity 
		},
		{
			'param_name':_('info about active tasks'),
			'param_value': tasks_info 
		}

		]

		return info


class Group(models.Model):
	name = models.CharField(max_length=200, verbose_name=_("programm name"))
	category = models.ForeignKey(Category, on_delete=models.CASCADE)
	is_default = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	description = models.TextField(verbose_name=_("what is this programm for"), blank=True)
	completed_tasks = models.IntegerField(null=True, blank=True)
	spent_time = models.IntegerField(null=True, blank=True)
	last_activity = models.DateField(default=timezone.now())	
	created_at = models.DateField(auto_now_add=True)
	

	def __unicode__(self):
		return self.name

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = _("programm")
		verbose_name_plural = _("programms")
		ordering = ["-last_activity"]


	def update_group(self):
		self.last_activity = datetime.datetime.now()
		self.spent_time = 0
		self.completed_tasks = 0
		tasks = Task.objects.filter(group=self)
		for task in tasks:
			self.spent_time += task.minutes
			if task.is_finished:
				self.completed_tasks += 1

		self.save()
		self.category.update_category()
		return True
		
		

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


	def get_task_info(self, task_name, group_name, category_name, profile):
		"""
		Возвращает информацию о задаче:
		- название задачи
		- название группы
		- дата создания
		- потраченное на задачу время
		- последняя активность 
		
		"""
		category = Category.objects.get(name=category_name, profile=profile)
		group = Group.objects.get(name=group_name, category=category)
		task = super().get(
			name= task_name,
			profile= profile,
			group= group			
			)
		info = [
		{
			'param_name':_('name'),
			'param_value': task.name 
		},
		{
			'param_name':_('group'),
			'param_value': task.group.name 
		},
		{
			'param_name':_('created at'),
			'param_value': task.created_at 
		},
		{
			'param_name':_('created at'),
			'param_value': task.created_at 
		},
		{
			'param_name':_('spent time'),
			'param_value': task.spent_time 
		},
		{
			'param_name':_('last activity'),
			'param_value': task.last_activity 
		}

		]

		return info
		


class Task(models.Model):
	name = models.CharField(max_length=200, verbose_name=_("task"))
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
	group = models.ForeignKey(Group, on_delete=models.CASCADE)
	is_finished = models.BooleanField(default=False)
	created_at = models.DateField(auto_now_add=True)
	plan_date = models.DateField(null=True, blank=True)
	finish_date = models.DateField(null=True, blank=True)
	spent_time = models.IntegerField(null=True, blank=True)
	last_activity = models.DateField(default=timezone.now())
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


	def update_task(self, transaction):
		self.last_activity = datetime.datetime.now()
		self.spent_time += transaction.minutes
		self.save()
		self.group.update_group()
		return True

	def finish_task(self):
		self.finish_date = datetime.datetime.now()
		self.is_finished = True
		self.save()
		self.group.update_group()
		return True



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


class TransactionManager(models.Manager):

	def add_transaction(self, task, minutes):
		transaction = super().create(
			task= task,
			spent_time= minutes
			)
		task.update_task()

		return True



class Transaction(models.Model):
	task = models.ForeignKey(Task, on_delete=models.CASCADE)
	spent_time = models.IntegerField()
	created_at = models.DateField(auto_now_add=True)

	class Meta:
		verbose_name = _("transaction")
		verbose_name_plural = _("transactions")
		ordering = ["-created_at"]
		



# Create your models here.
