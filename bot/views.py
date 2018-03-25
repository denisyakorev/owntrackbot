from django.shortcuts import render
from django.http import HttpResponse
import json

# Create your views here.
def hello_world(request):
    response = HttpResponse(json.dumps({'message': 'hello_world'}),
                             content_type='application/json')
    response.status_code = 200
    return response

def dispatcher(request):
    print ('POST: ')
    print (request.POST)
    print ('GET: ')
    print (request.GET)
    response = HttpResponse(json.dumps({'message': 'ок'}),
                             content_type='application/json')
    response.status_code = 200
    return response