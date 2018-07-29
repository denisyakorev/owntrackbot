from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from django.template.loader import get_template

# Create your models here.


class ProgrammComponent(models.Model):
	spent_time = models.IntegerField(null=True, blank=True)
	last_activity = models.DateField(default=timezone.now())
	created_at = models.DateField(auto_now_add=True)
	
	def get_info(self):
		spent_time = self.get_spent_time()
		
		info = [
			{
				'param_name':_('spent time'),
				'param_value': spent_time 
			},
			{
				'param_name':_('last activity'),
				'param_value': self.last_activity.strftime("%d.%m.%Y")  
			}
		]

		return info

	
	def get_spent_time(self):
		spent_time = "0"
		if self.spent_time:
			if self.spent_time > 60:
				spent_time = str(self.spent_time // 60)+"h "+str(self.spent_time % 60)+"m"
			else:
				spent_time = str(self.spent_time)+"m"
		
		return spent_time


	class Meta:
		abstract= True


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
		print('get profile info')
		context = {}
		context['categories'] = Category.objects.filter(profile=profile)		
		context['groups'] = Group.objects.filter(profile=profile).select_related()
		#Отдельно получаем все задачи пользователя
		context['tasks'] = Task.objects.filter(profile=profile, is_finished=False).select_related()
		template = get_template('responses/profile.txt')
		info = template.render(context)
		print (info)
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



class Profile(ProgrammComponent):
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	username = models.CharField(max_length=200, verbose_name=_("username"))
	register_from = models.CharField(max_length=200, verbose_name=_("register from"), default='telegram')
	register_id = models.IntegerField(null=True, blank=True, unique=True)
	completed_tasks = models.IntegerField(null=True, blank=True)	
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
			self.spent_time += category.spent_time
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
		return category


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
		try:
			category = Category.objects.get(name=category_name, profile=profile)
		except Category.DoesNotExist:
			raise ValueError(_("Category does not exist"))
		groups = Group.objects.filter(category=category)
		
		groups_info = ""
		for group in groups:
			groups_info += group.name+": "+ group.get_spent_time() + "\n"
		
		info = category.get_info()
		info.append(
		{
			'param_name':_('info about groups in category'),
			'param_value': groups_info 
		}
		)

		return info


class Category(ProgrammComponent):
	name = models.CharField(max_length=200, unique=True, verbose_name=_("category name"))
	profile = models.ForeignKey('Profile', on_delete=models.CASCADE, blank=True, null=True)
	parent = models.ForeignKey("Category", on_delete=models.CASCADE, blank=True, null=True)
	is_default = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	completed_tasks = models.IntegerField(null=True, blank=True)
	aim = models.TextField(verbose_name=_("what person want to get"), blank=True)
	objects = CategoryManager()

	def __unicode__(self):
		return self.name

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = _("category")
		verbose_name_plural = _("categories")
		ordering = ["-last_activity"]
		unique_together = ("name", "profile")

	def update_category(self):
		self.last_activity = datetime.datetime.now()
		self.spent_time = 0
		self.completed_tasks = 0
		groups = Group.objects.filter(category=self)
		for group in groups:
			self.spent_time += group.spent_time
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
			profile=profile,
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
		try:
			group = super().get(name=group_name, category=category)
		except Group.DoesNotExist:
			raise ValueError(_('Group does not exist'))

		tasks = Task.objects.filter(group= group, is_finished= False)
		tasks_info = ""
		for task in tasks:
			tasks_info += task.name+": "+ task.get_spent_time() + "\n"
		info = group.get_info()
		info.append({
				'param_name':_('category'),
				'param_value': group.category.name 
			})			
		info.append({
				'param_name':_('info about active tasks'),
				'param_value': tasks_info 
			})
		

		return info


class Group(ProgrammComponent):
	name = models.CharField(max_length=200, verbose_name=_("programm name"))
	category = models.ForeignKey(Category, on_delete=models.CASCADE)
	profile = models.ForeignKey('Profile', on_delete=models.CASCADE, blank=True, null=True)
	is_default = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	description = models.TextField(verbose_name=_("what is this programm for"), blank=True)
	completed_tasks = models.IntegerField(null=True, blank=True)
	objects = GroupManager()
	

	def __unicode__(self):
		return self.name

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = _("programm")
		verbose_name_plural = _("programms")
		ordering = ["-last_activity"]
		unique_together = ("name", "category")


	def update_group(self):
		self.last_activity = datetime.datetime.now()
		self.spent_time = 0
		self.completed_tasks = 0
		tasks = Task.objects.filter(group=self)
		for task in tasks:
			if self.spent_time:
				self.spent_time += task.spent_time
			else:
				self.spent_time = task.spent_time

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
		category= Category.objects.get(name=category_name, profile=profile)
		group= Group.objects.get(name=group_name, category=category)
		try:
			task = super().get(
				name= task_name,
				profile= profile,
				group= group			
				)
		except Task.DoesNotExist:
			raise ValueError(_('Task does not exist'))

		info = task.get_info()
		info.append(
		{
			'param_name':_('group'),
			'param_value': task.group.name 
		}
		)

		return info


	def finish_task(self, task_name, group_name, category_name, profile):
		
		category = Category.objects.get(name=category_name, profile=profile)
		group = Group.objects.get(name=group_name, category=category)
		task = Task.objects.get(
			name= task_name,
			profile= profile,
			group= group,					
			)

		task.finish_date = datetime.datetime.now()
		task.is_finished = True
		task.save()
		task.group.update_group()
		
		return True
		


class Task(ProgrammComponent):
	name = models.CharField(max_length=200, verbose_name=_("task"))
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
	group = models.ForeignKey(Group, on_delete=models.CASCADE)
	is_finished = models.BooleanField(default=False)
	plan_date = models.DateField(null=True, blank=True)
	finish_date = models.DateField(null=True, blank=True)
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
		unique_together = ("name", "group")


	def update_task(self, transaction):
		self.last_activity = datetime.datetime.now()
		print("%s + %s" % (str(self.spent_time), str(transaction.spent_time)))
		if self.spent_time:
			self.spent_time += transaction.spent_time
		else:
			self.spent_time = transaction.spent_time
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

	def add_transaction(self, task_name, group_name, category_name, profile, minutes):
		category = Category.objects.get(name=category_name, profile=profile)
		group = Group.objects.get(name=group_name, category=category)
		task = Task.objects.get(
			name= task_name,
			profile= profile,
			group= group,					
			)

		transaction = super().create(
			task= task,
			spent_time= minutes
			)

		task.update_task(transaction)

		return True



class Transaction(models.Model):
	task = models.ForeignKey(Task, on_delete=models.CASCADE)
	spent_time = models.IntegerField()
	created_at = models.DateField(auto_now_add=True)
	objects = TransactionManager()

	class Meta:
		verbose_name = _("transaction")
		verbose_name_plural = _("transactions")
		ordering = ["-created_at"]
		



# Create your models here.
