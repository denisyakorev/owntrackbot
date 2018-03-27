from django.shortcuts import render
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
import requests
from bot.models import TelegramBot



# Create your views here.
@csrf_exempt
def dispatcher(request):
    '''Принимает запрос, передаёт его в обработчик'''    
    #Преобразовываем запрос
    update = json.loads(request.body.decode('utf-8'))
    #Передаём в обработчик
    TelegramBot.dispatch_update(update)    

    #Возвращаем ответ
    response = HttpResponse(json.dumps({'message': 'ок'}),
                             content_type='application/json')
    response.status_code = 200
    return response


def send_message(chat_id, message='hello'):
    method = TelegramBot.get_send_message_url()
    
    data = {
        'chat_id':chat_id,
        'text': message
    }

    r = requests.post(method, data=data)
    print (r.status_code)

    return r.status_code == 200
        