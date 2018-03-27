from django.db import models
from core.models import Profile
from django.conf import settings

class TelegramBot(models.Model):

	available_messages = models.ManyToManyField('Message', blank=True, null=True)
	url_prefix = 'https://api.telegram.org/bot'

	def dispatch_update(self, update):
		if not update['message']['from']['is_bot']:
			Profile.objects.get_profile(update['message']['from'])
		
		chat_id = update['message']['chat']['id']
		send_message(chat_id)

	def get_send_message_url(self):
		return self.url_prefix + settings.TELEGRAM_TOKEN + 'sendMessage'



def Message(models.Model):
	text = models.TextField()

	def __unicode__(self):
        return self.text

    def __str__(self):
        return self.text

    
