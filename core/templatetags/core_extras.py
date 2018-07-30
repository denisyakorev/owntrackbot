from django import template

register = template.Library()

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