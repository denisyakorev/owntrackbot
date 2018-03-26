from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
import requests


url = 'https://api.telegram.org/bot%s/' % (settings.TELEGRAM_TOKEN)


@csrf_exempt
def dispatcher(request):    
    update = json.loads(request.body.decode('utf-8'))
    print(update)
    chat_id = update['message']['chat']['id']
    send_message(chat_id)
    response = HttpResponse(json.dumps({'message': 'ок'}),
                             content_type='application/json')
    response.status_code = 200
    return response


def send_message(chat_id):
    method = url+ 'sendMessage'
    data = {
        'chat_id':chat_id,
        'text': 'hello world'
    }

    r = requests.get(method, data=data)
    print(r.url)
    print (r.status_code)

    if r.status_code == 200:
        return True
    else:
        return False
