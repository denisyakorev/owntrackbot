from django.db import models
from core.models import Profile
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
import re
from core.models import Task, Category, Group


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
		intent, target = self.analyze_message(in_message)
		#Если действия понятные - выполним их
		if intent and target:
			result = self.make_actions(intent, target)
			#И сформируем отчёт о действиях
			if result:
				return self.get_message(1)
		
		#Иначе - получаем сообщение об ошибке
		out_message = self.get_message(2)
		#Возвратим сообщение по результату анализа
		return out_message


	def analyze_message(self, message):
		message = message.lower().strip()
		#Разбираем комманды
		command = self.analyze_command(message[0])
		#Разбираем цели и время, которые могут быть указаны в сообщении
		targets = self.analyze_embeddings(message)
		if not targets.is_valid:

		result = self.make_actions(command, targets)		

		return [command, targets]


	

	def make_actions(self, intent, target):
		
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

	is_valid = models.BooleanField(default=True)
	symbol = models.CharField(max_length=10, blank=True)
	target_type = models.IntegerField(choises=COMMAND_TYPES, default=0)
	name = models.CharField(max_length= 200, blank=True)
	errors = models.CharField(max_length= 200, blank=True)

	def __init__(self, message):
		self.get_embedding_result('\\'+self.symbol, message)
		if not self.is_valid:
			raise ValueError(self.errors)
			


	def get_embedding_result(self, symbol, message):
		""" 
		Функция, вычленяющая задачи, группы и категории из
		сообщения
		 """
		string = symbol+'(\w+)'
		pattern = re.compile(string)
		entities = pattern.findall(message)
				
		if len(entities) > 1: 
			self.is_valid = False
			self.errors = 'Too many objects'

		elif len(entities) == 0:
			self.is_valid = False
			self.errors = 'Too many objects'
		
		else:
			self.is_valid = True
			self.name = entities[0]


class TaskTarget(models.Model, CommandTarget):
	symbol= "#"
	task= models.ForeignKey('Task', on_delete=models.CASCADE, blank=True, null=True) 


class GroupTarget(models.Model, CommandTarget):
	symbol= "@"
	group= models.ForeignKey('Group', on_delete=models.CASCADE, blank=True, null=True)


class CategoryTarget(models.Model, CommandTarget):
	symbol= "*"
	category= models.ForeignKey('Category', on_delete=models.CASCADE, blank=True, null=True)


class Command(models.Model):
	message = models.TextField(blank=True)
	COMMAND_TYPES = (
		(0, 'create'),
		(1, 'read'),
		(2, 'update'),
		(3, 'delete'),
		(4, 'finish')
		)
	command = models.IntegerField(choises=COMMAND_TYPES, default=1)
	is_command_valid = models.BooleanField(default=True)
	
	task_target = models.ForeignKey('TaskTarget', on_delete=models.SET_NULL)
	group_target = models.ForeignKey('GroupTarget', on_delete=models.SET_NULL)
	category_target = models.ForeignKey('CategoryTarget', on_delete=models.SET_NULL)

	is_time_valid = models.BooleanField(default=True)
	time_errors = models.CharField(max_length= 200, blank=True)
	minutes = models.IntegerField(blank=True, null=True, default=0)

	created_at = models.DateField(auto_now_add=True)
	created_by = models.ForeignKey(Profile, on_delete=models.CASCADE)


	def __init__(self, message, profile):
		self.message = message.lower().strip()
		self.profile = profile
		#Разбираем комманды
		self.analyze_command(message[0])
		#Разбираем цели и время, которые могут быть указаны в сообщении
		self.analyze_embeddings(message)
		#Пробуем получить все объекты, указанные в комманде
		self.get_command_objects()
	
	
	def analyze_embeddings(self, message):
				
		#Проверяем на наличие не больше одной задачи
		try:
			self.task_target = TaskTarget(self.message)
		except ValueError(e):
			self.task_target = null

		#Проверяем на наличие не больше одной группы
		try:
			self.group_target = GroupTarget(self.message)
		except ValueError(e):
			self.group_target = null

		#Проверяем на наличие не больше одной категории
		try:
			self.category_target = CategoryTarget(self.message)
		except ValueError(e):
			self.category_target = null
		
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
		return True		


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

	
