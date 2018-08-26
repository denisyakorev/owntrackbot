from django.shortcuts import render
import json
from core.models import Profile, Category
from django.http import Http404, HttpResponse

# Create your views here.
def get_profile_info(request, profile_id):
    """
    Возвращает информацию об общем затраченном времени и времени, затраченном на каждую из
    входящих в профиль категорий
    :param request: Объект запроса
    :param str profile_id: идентификатор профиля
    :return: json строка по объекту со следующими свойствами:
    @spent_time - общее время профиля в формате чч мм
    @categories - массив объектов со следующими свойствами:
        @name - название категории
        @spent_time - затраченное время
    """
    try:
        profile = Profile.objects.get(pk=int(profile_id))
    except Profile.DoesNotExist:
        raise Http404

    data = get_profile_data(profile)

    return HttpResponse(json.dumps(data), content_type="application/json")



def get_profile_data(profile):
    """
    Возвращает объект с данными по профилю
    :param profile: Профиль, для которого осуществляется поиск
    :return: объект с данными
    """
    data = {}
    data['spent_time'] = min_to_hours(profile.spent_time)
    data['categories'] = []

    categories = Category.objects.filter(profile=profile)
    for category in categories:
        cat_obj = {
            "name": category.name,
            "spent_time": min_to_hours(category.spent_time)
        }
        data['categories'].append(cat_obj)

    return data



def min_to_hours(value):
	"""
	Convert minutes to hours
	for example minutes: 62 out: 1h 2m
	"""
	minutes = int(value)
	hours = minutes//60
	minutes = minutes%60
	result = ''
	if hours > 0:
		result = '%dh %dm' % (hours, minutes)
	else:
		result = '%dm' % (minutes)

	return result