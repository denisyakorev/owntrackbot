from django.db import models
from core.models import Profile
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
import re
from core.models import Task, Category, Group, Transaction
from core.models import TaskManager, GroupManager
import logging
import json
from django.db.utils import IntegrityError

logger = logging.getLogger(__name__)


class BotManager(models.Manager):

	def get_or_create_bot(self, messager):
		try:
			bot = super().get(messager=messager)
			if bot:
				return bot
		except ObjectDoesNotExist:
			if messager == 'telegram':
				bot = Bot(
					messager = 'telegram',
					url_prefix = 'https://api.telegram.org/bot'
					)
				bot.save()
				return bot



class Bot(models.Model):

	messager = models.CharField(max_length = 200)
	url_prefix = models.TextField()
	objects = BotManager()
	
	def get_response(self, update):	
		print("get response")	
		#Получим данные пользователя, или создадим нового
		user_data = update['message']['from']
		profile = Profile.objects.get_or_create_profile(
			client_type= self.messager,
			user_id= update['message']['from']['id'],
			username= update['message']['from']['first_name']
			)		
		#Проанализируем сообщение
		in_message = update['message']['text']
		out_message = self.make_command(in_message, profile, update)
		print("out message: "+out_message)
		return out_message

	def make_command(self, in_message, profile, update):
		try:
			command = Command(in_message, profile, self)
		except Exception:
			logger.info("Update: %s", json.dumps(update))
			logger.exception("Something wrong with your command")
			return _("Something wrong with your command")

		#Если действия понятные - выполним их
		if command.command == 0:
			message = self.create_objects(command)			
			
		elif command.command == 1:
			message= self.read_objects(command)
			
		elif command.command == 2:
			if command.is_time_valid and command.task_target:
				result = self.update_objects(command, profile)
				if result:
					message = self.read_objects(command)
				else:
					message = _("Something wrong with your command")				
			else:
				message = _("You should write right time and right task")
						

		elif command.command == 4:
			if command.task_target:
				result = self.finish_objects(command, profile)
				if result:
					message = self.read_objects(command)
				else:
					message = _("Something wrong with your command")
			else:
				message = _("You should write right task")
		
		#Возвратим сообщение по результату анализа
		return message


	def finish_objects(self, command, profile):
		try:
			Task.objects.finish_task(
				task_name= command.task_target.name,
				group_name= command.group_target.name,
				category_name= command.category_target.name,
				profile= profile
				)
		except Exception:
			return False
		
		return True

	
	def create_objects(self, command):
		"""
		Определяем, какой объект требуется создать
		и отправляем запрос на создание
		"""
		if command.task_target:
			#Если указана задача, значит создаём её
			try:
				Task.objects.create_new_task(
					task_name= command.task_target.name,
					group_name= command.group_target.name,
					category_name= command.category_target.name,
					profile= command.profile
					)
				return _("Task created successfully")
			except IntegrityError:
				return _("Task with the name already exists in the group")
			except Exception as err:
				return _("Something wrong with your command")
		else:
			#Если задача не указана
			if command.group_target.name != 'default':
				#Но указана какая-то группа
				try:
					Group.objects.create_new_group(
						group_name= command.group_target.name,
						category_name= command.category_target.name,
						profile= command.profile
						)
					return _("Group created successfully")
				except IntegrityError:
					return _("Group with the name already exists in the category")
				except Exception as err:
					return _("Something wrong with your command")
			
			elif command.category_target.name != 'default':
				#Если группа не указана, но указана категория
				try:
					Category.objects.create_new_category(
						category_name= command.category_target.name,
						profile= command.profile
						)
					return _("Category created successfully")
				except IntegrityError:
					return _("Category with the name already exists in the profile")
				except Exception as err:
					return _("Something wrong with your command")
			
			else:
				return False


	def read_objects(self, command):
		"""
		Выясняем по какому объекту нужно получить информацию
		и запрашиваем её
		"""
		if command.task_target:
			try:
				result= Task.objects.get_task_info(
					task_name= command.task_target.name,
					group_name= command.group_target.name,
					category_name= command.category_target.name,
					profile= command.profile
					)
			except ValueError as err:
				return err.args[0]

		else:
			#Если задача не указана
			
			if command.group_target.name != 'default' or not command.group_target.is_auto_default:
				#Но указана какая-то группа
				try:
					result= Group.objects.get_group_info(
						group_name= command.group_target.name,
						category_name= command.category_target.name,
						profile= command.profile
						)
				except ValueError as err:
					return err.args[0]
				
			elif command.category_target.name != 'default' or not command.category_target.is_auto_default:
				#Если группа не указана, но указана категория
				try:
					result= Category.objects.get_category_info(
						category_name= command.category_target.name,
						profile= command.profile
						)
				except ValueError as err:
					return err.args[0]
				
			else:				
				result = Profile.objects.get_profile_info(
					profile= command.profile
					)


		result_string = ''
		index = 0
		last_index = len(result)-1
		for elem in result:			
			result_string += str(elem['param_name'])+ ': '+str(elem['param_value'])
			if index != last_index:
				result_string += "\n"
			index += 1
		return result_string


	def update_objects(self, command, profile):
		try:
			Transaction.objects.add_transaction(
				task_name= command.task_target.name,
				group_name= command.group_target.name,
				category_name= command.category_target.name,
				profile= profile,
				minutes= command.minutes
				)
		except Exception as err:
			return False
		
		return True
		



	def get_send_message_url(self):
		return self.url_prefix + settings.TELEGRAM_TOKEN + '/sendMessage'


	def get_message(self, message_type='greeting'):
		"""Возвращает сообщение для ответа"""
		try:
			message = Message.objects.filter(message_type=message_type).order_by('?')[0]
		except IndexError:
			message = _("Hi. I am alive but it's all I can say now")
		
		return message


	def __unicode__(self):
		return self.messager

	def __str__(self):
		return self.messager


class CommandTarget(models.Model):
	TARGET_TYPES= (
		(0, 'task'),
		(1, 'group'),
		(2, 'category')
		)

	target_type = models.IntegerField(choices=TARGET_TYPES, default=0)
	name = models.CharField(max_length= 200, blank=True)
	errors = models.CharField(max_length= 200, blank=True)	

	def __init__(self, message, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.get_embedding_result(message=message)

	def get_embedding_result(self, message):
		""" 
		Функция, вычленяющая задачи, группы и категории из
		сообщения
		 """
		string = '\\' + self.symbol+'(\w+)'
		pattern = re.compile(string)
		entities = pattern.findall(message)
				
		if len(entities) > 1: 
			raise ValueError('Too many objects')

		elif len(entities) == 0:
			raise ValueError('There is no objects')
		
		else:
			self.name = entities[0]


	class Meta():
		abstract= True


class TaskTarget(CommandTarget):
	symbol = models.CharField(max_length=10, blank=True, default='#')
	task= models.ForeignKey(Task, on_delete=models.CASCADE, blank=True, null=True) 

		
class GroupTarget(CommandTarget):
	symbol = models.CharField(max_length=10, blank=True, default='@')
	group= models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
	is_auto_default = models.BooleanField(default=False)

	
	def get_embedding_result(self, message):
		""" 
		Функция, вычленяющая задачи, группы и категории из
		сообщения
		 """
		string = '\\' + self.symbol+'(\w+)'
		pattern = re.compile(string)
		entities = pattern.findall(message)
				
		if len(entities) > 1: 
			raise ValueError('Too many objects')

		elif len(entities) == 0:
			self.name = 'default'
			self.is_auto_default = True
		
		else:
			self.name = entities[0]



class CategoryTarget(CommandTarget):
	symbol = models.CharField(max_length=10, blank=True, default='*')
	category= models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
	is_auto_default = models.BooleanField(default=False)

	
	def get_embedding_result(self, message):
		""" 
		Функция, вычленяющая задачи, группы и категории из
		сообщения
		 """
		string = '\\' + self.symbol+'(\w+)'
		pattern = re.compile(string)
		entities = pattern.findall(message)
				
		if len(entities) > 1: 
			raise ValueError('Too many objects')			

		elif len(entities) == 0:
			self.name = 'default'
			self.is_auto_default = True
		
		else:
			self.name = entities[0]


class Command(models.Model):
	message = models.TextField(blank=True)
	COMMAND_TYPES = (
		(0, 'create'),
		(1, 'read'),
		(2, 'update'),
		(3, 'delete'),
		(4, 'finish')
		)
	command = models.IntegerField(choices=COMMAND_TYPES, default=1)
	is_valid = models.BooleanField(default=True)
	
	task_target = models.ForeignKey('TaskTarget', on_delete=models.SET_NULL, null=True, blank=True)
	group_target = models.ForeignKey('GroupTarget', on_delete=models.SET_NULL, null=True, blank=True)
	category_target = models.ForeignKey('CategoryTarget', on_delete=models.SET_NULL, null=True, blank=True)

	is_time_valid = models.BooleanField(default=False)
	time_errors = models.CharField(max_length= 200, blank=True)
	minutes = models.IntegerField(blank=True, null=True, default=0)

	created_at = models.DateField(auto_now_add=True)
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE)


	def __init__(self, message, profile, bot, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.message = message.lower().strip()
		self.profile = profile
		#Разбираем комманды
		self.analyze_command(message[0])
		#Разбираем цели и время, которые могут быть указаны в сообщении
		self.analyze_embeddings(message)
		

	
	def analyze_embeddings(self, message):				
		#Проверяем на наличие не больше одной задачи
		try:
			self.task_target = TaskTarget(message=self.message)
		except ValueError as err:
			e = err.args[0]
			if e != 'There is no objects':						
				raise ValueError(e)
			else:
				pass

		#Проверяем на наличие не больше одной группы
		self.group_target = GroupTarget(message=self.message)	
		#Проверяем на наличие не больше одной категории
		self.category_target = CategoryTarget(message=self.message)		
		
		#Проверяем на наличие времени
		#И преобразуем время, при необходимости
		is_time_valid = self.get_embedding_time(message)
		if not is_time_valid:
			self.minutes = 0	


	def get_embedding_time(self, message):
		"""
		Функция, вычленяющая время из сообщения
		"""
		hour_pattern = re.compile('(\d+)h')		
		min_pattern= re.compile('(\d+)m')

		hours = hour_pattern.findall(message)
		if len(hours) > 1: 
			self.is_time_valid = False
			self.time_errors = "Too many words like hours signature"
			return False
		elif len(hours) == 0:
			hours = 0
		else:
			hours = int(hours[0])

		minutes = min_pattern.findall(message)
		if len(minutes) > 1:
			self.is_time_valid = False
			self.time_errors = "Too many words like minutes signature" 
			return False
		elif len(minutes) == 0:
			minutes = 0
		else:
			minutes = int(minutes[0])

		self.minutes = hours*60 + minutes
		self.is_time_valid = True
		return self.is_time_valid		


	def analyze_command(self, command):
		"""
		Поиск комманд по ключевым словам
		"""
		if command == '?':
			self.command = 1
		elif command == '+':
			self.command = 0
		elif command == '!':
			self.command = 4
		else:
			self.command = 2
		

class Message(models.Model):
	text = models.TextField()
	lang = models.CharField(max_length=10, blank=True)
	MESSAGE_TYPES = (
		(0, 'greeting'),
		(1, 'approval'),
		(2, 'failure'),
		(3, 'chatter')
		)
	message_type = models.IntegerField(choices=MESSAGE_TYPES,
		default=3)

	def __unicode__(self):
		return self.text

	def __str__(self):
		return self.text

	
