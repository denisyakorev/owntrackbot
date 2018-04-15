from django.db import models
from core.models import Profile
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
import re
from core.models import Task, Category, Group, Transaction
from core.models import TaskManager, GroupManager
import logging
import json

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
		#Получим данные пользователя, или создадим нового
		user_data = update['message']['from']
		profile = Profile.objects.get_or_create_profile(
			client_type= self.messager,
			user_id= update['message']['from']['id'],
			username= update['message']['from']['first_name']
			)		
		#Проанализируем сообщение
		in_message = update['message']['text']
		out_message = self.make_command(in_message, profile)
		return out_message

	def make_command(self, in_message, profile):
		try:
			command = Command(in_message, profile)
		except Exception(e):
			logger.info("Update: %s", json.dumps(update))
			logger.exception(e)
			return _("Something wrong with your command")

		#Если действия понятные - выполним их
		if command.command == 0:
			self.create_objects(command)
			message = self.get_message(1)
			
		elif command.command == 1:
			message= self.read_objects(command)
			
		elif command.command == 2:
			if command.is_time_valid and command.task_target:
				self.update_objects(command)
				message = self.get_message(1)+"\n"
				message += self.read_objects(command)				
			else:
				message = _("You should write right time and right task")
						

		elif command.command == 4:
			if command.task_target:
				self.finish_objects(command)
				message = self.get_message(1)+"\n"
				message += self.read_objects(command)
			else:
				message = _("You should write right task")
		
		#Возвратим сообщение по результату анализа
		return message


	def finish_objects(self, command):
		command.task_target.task.finish_task()
		return True

	
	def create_objects(self, command):
		"""
		Определяем, какой объект требуется создать
		и отправляем запрос на создание
		"""
		if command.task_target:
			#Если указана задача, значит создаём её
			TaskManager.create_new_task(
				task_name= command.task_target.name,
				group_name= command.group_target.name,
				category_name= command.category_target.name,
				profile= command.profile
				)
			return True
		else:
			#Если задача не указана
			if command.group_target.name != 'default':
				#Но указана какая-то группа
				GroupManager.create_new_group(
					group_name= command.group_target.name,
					category_name= command.category_target.name,
					profile= command.profile
					)
				return True
			elif command.category_target.name != 'default':
				#Если группа не указана, но указана категория
				CategoryManager.create_new_category(
					category_name= command.category_target.name,
					profile= command.profile
					)
				return True
			else:
				return False


	def read_objects(self, command):
		"""
		Выясняем по какому объекту нужно получить информацию
		и запрашиваем её
		"""
		if command.task_target:
			#Если указана задача, значит создаём её
			result= TaskManager.get_task_info(
				task_name= command.task_target.name,
				group_name= command.group_target.name,
				category_name= command.category_target.name,
				profile= command.profile
				)

		else:
			#Если задача не указана
			if command.group_target.name != 'default':
				#Но указана какая-то группа
				result= GroupManager.get_group_info(
					group_name= command.group_target.name,
					category_name= command.category_target.name,
					profile= command.profile
					)
				
			elif command.category_target.name != 'default':
				#Если группа не указана, но указана категория
				result= CategoryManager.get_category_info(
					category_name= command.category_target.name,
					profile= command.profile
					)
				
			else:
				result = ProfileManager.get_profile_info(
					profile= command.profile
					)

		result_string = ''
		for elem in result:
			result_string += elem.param_name+ ': '+elem.param_value+'\n'

		return result_string


	def update_objects(self, command):
		Transaction.objects.add_transaction(
			task= command.task_target.task,
			spent_time= command.minutes
			)
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

	def __init__(choices, *args, **kwargs):
		super().__init__(choices, *args, **kwargs)
		get_embedding_result(kwargs['message'])

	def get_embedding_result(self, message):
		""" 
		Функция, вычленяющая задачи, группы и категории из
		сообщения
		 """
		string = self.symbol+'(\w+)'
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

	
	def get_embedding_result(self, symbol, message):
		""" 
		Функция, вычленяющая задачи, группы и категории из
		сообщения
		 """
		string = symbol+'(\w+)'
		pattern = re.compile(string)
		entities = pattern.findall(message)
				
		if len(entities) > 1: 
			raise ValueError('Too many objects')

		elif len(entities) == 0:
			self.name = 'default'
		
		else:
			self.name = entities[0]



class CategoryTarget(CommandTarget):
	symbol = models.CharField(max_length=10, blank=True, default='*')
	category= models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)

	
	def get_embedding_result(self, symbol, message):
		""" 
		Функция, вычленяющая задачи, группы и категории из
		сообщения
		 """
		string = symbol+'(\w+)'
		pattern = re.compile(string)
		entities = pattern.findall(message)
				
		if len(entities) > 1: 
			raise ValueError('Too many objects')			

		elif len(entities) == 0:
			self.name = 'default'
		
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
			self.task_target = TaskTarget(self.message)
		except ValueError(e):
			if e != 'There is no objects':						
				raise ValueError(e)
			else:
				pass

		#Проверяем на наличие не больше одной группы
		self.group_target = GroupTarget(self.message)	
		#Проверяем на наличие не больше одной категории
		self.category_target = CategoryTarget(self.message)		
		
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

	
