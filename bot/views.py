from django.shortcuts import render
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
import requests
from bot.models import Bot
from threading import Thread



# Create your views here.
@csrf_exempt
def dispatcher(request):
    '''Принимает запрос, передаёт его в обработчик''' 
    print ('Hello world')
    update = json.loads(request.body.decode('utf-8')) 
    #Заупскаем второй поток, 
    #который начинает работу над ответным сообщением
    t2= Thread(target=make_response, args=(), kwargs={'update': update})

    t2.start()

    response = HttpResponse(json.dumps({'message': 'ок'}),
                             content_type='application/json')
    response.status_code = 200
    return response


def send_message(chat_id, message='hello', url=''):
        
    data = {
        'chat_id':chat_id,
        'text': message
    }
    r = requests.post(url, data=data)
    
    return r.status_code == 200
        

def make_response(*args, **kwargs):
    """
    Запрос:
    {'message': {'text': 'Hi', 'from': {'language_code': 'ru-RU', 'is_bot': False, 'first_name': 'Denis', 'id': 347385183}, 'chat': {'type': 'private', 'first_name': 'Denis', 'id': 347385183}, 'date': 1522167580, 'message_id': 52}, 'update_id': 890164791}
    """    
    #Передаём запрос боту, и получаем его ответ   
    update = kwargs['update']
    bot = Bot.objects.get_or_create_bot('telegram')
    message = bot.get_response(update)
    send_message(
        chat_id= update['message']['chat']['id'], 
        message= message,
        url= bot.get_send_message_url()
        )
