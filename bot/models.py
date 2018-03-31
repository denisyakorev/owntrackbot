from django.db import models
from core.models import Profile
from django.conf import settings
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
		#Ответим что-нибудь. Пока просто приветствие		
		return self.get_message(0)
			

	def get_send_message_url(self):
		return self.url_prefix + settings.TELEGRAM_TOKEN + 'sendMessage'


	def get_message(self, message_type='greeting'):
		"""Возвращает сообщение для ответа"""
		try:
			message = Message.objects.filter(message_type=message_type).order_by('?')[0]
		except IndexError:
			message = 'Привет дружище. У меня всё в порядке, но это пока всё, что я могу пока сказать'
		
		return message


	def __unicode__(self):
		return self.messager

	def __str__(self):
		return self.messager



class Message(models.Model):
	text = models.TextField()
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

	
