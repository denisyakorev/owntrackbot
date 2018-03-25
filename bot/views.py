from django.shortcuts import render
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
import requests



# Create your views here.
def hello_world(request):
    response = HttpResponse(json.dumps({'message': 'hello_world'}),
                             content_type='application/json')
    response.status_code = 200
    return response

@csrf_exempt
def dispatcher(request):    
    update = json.loads(request.body.decode('utf-8'))
    chat_id = update.message.chat.id
    send_message(chat_id)
    response = HttpResponse(json.dumps({'message': 'ок'}),
                             content_type='application/json')
    response.status_code = 200
    return response


def send_message(chat_id):
    #url = 'https://api.telegram.org/bot565321270:AAGVaNTz5a2pscli1_VnG0vh2Fv0CarejLM/sendMessage'
    data = {
        'chat_id':chat_id,
        'text': 'hello world'
    }

    r = requests.post(url, data=data)
    print (r.status_code)

    if r.status_code == 200:
        return True
    else:
        return False