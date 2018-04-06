from django.db import models
from core.models import Profile
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist


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
		command = self.analyze_command(message[0])

		

		return [command, message]


	def analyze_command(self, command):

		if command == '?':
			command = 'read'
		elif command == '+':
			command = 'create'
		elif command == '!':
			command = 'finish'
		else:
			command = False

		return command
	

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

	
