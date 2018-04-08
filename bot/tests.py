from django.test import TestCase
from bot.models import Bot

# Create your tests here.
class BotTestCase(TestCase):
	
	def setUp(self):
		self.bot = Bot.objects.get_or_create_bot('telegram')

	def test_message_out(self):
		
		equals = [
			['?', ['read', 'user_profile'] ],

			['? #unrealtask', ['read', 'error_task_does_not_exist']],

			['? #realtask',	['read', 'task_id']],

			['? #realtaskWithTwinInOtherGroup',['read', 'error_too_more_objects']],

			['?#realtask',['read', 'task_id']],

			['? @realgroup',['read', 'group_id']],

			['? @unrealgroup',['read', 'error_group_does_not_exist']],

			['? *realcategory',['read', 'category_id']],

			['? *unrealcategory',['read', 'error_category_does_not_exist']],

			['+ #newtask',['create', 'task_newtask in group default in category default']],

			['+ #existingtask',['create', 'error_task_exists']],

			['+ #newtask @existinggroup',['create', 'task_newtask in group existinggroup in category default']],

			['+ #newtask @existinggroup *existingcategory',['create', 'task_newtask in group existinggroup in category existingcategory']],

			['+ #newtask @newgroup *existingcategory',['create', 'error_group_does_not_exists']],

			['+ #newtask @existinggroup *newcategory',['create', 'error_category_does_not_exists']],

			['+ #newtask #newtask2 @existinggroup *existingcategory',['create', 'error_too_many_tasks']],

			['+ #newtask @existinggroup @existinggroup1 *existingcategory',['create', 'error_too_many_groups']],

			['+ #newtask @existinggroup *existingcategory *existingcategory1',['create', 'error_too_many_categories']],

			['+ @existinggroup *existingcategory',['create', 'error_group_exists']],

			['+ @newgroup *existingcategory',['create', 'group_newgroup in category existingcategory']],

			['+ @existinggroup #newtask *existingcategory',['create', 'task_newtask in group existinggroup in category existingcategory']],

			['+ @existinggroup *existingcategory  #newtask',['create', 'task_newtask in group existinggroup in category existingcategory']],

			['+ *existingcategory @existinggroup  #newtask',['create', 'task_newtask in group existinggroup in category existingcategory']],

			['+ *existingcategory @existinggroup',['create', 'error_group_exists']],

			['+ *newcategory @existinggroup',['create', 'error_category_does_not_exists']],

			['+ *newcategory',['create', 'category_newcategory']],

			['+ *existingcategory',['create', 'error_category_exists']],

			['1h23m #task1',['update', 'add 83 min to task1']],

			['1h23m #taskWithTwinInOtherGroup',['update', 'error_too_many_tasks']],

			['+1h23m #newtask',['create', 'task_new_task']],

			['+1h23m #existingtask',['create', 'error_task_exists']],

			['?1h23m #existingtask',['read', 'task_existingtask']],

			['23m #existingtask',['update', 'add 23 min to task1']],

			['23 #existingtask',['update', 'error_unknown_value']],

			['m #existingtask',['update', 'error_unknown_value']],

			['! #existingtask',['finish', 'task_existingtask']],

			['! #existingtaskWithTwinInOtherGroup',['finish', 'error_too_many_tasks']],

			['! @existinggroup',['finish', 'error_unknown_task']],

			['! *existingcategory',['finish', 'error_unknown_task']]

		]
		
		for elem in equals:
			command, message = self.bot.analyze_message(elem[0])
			self.assertEqual(command, elem[1][0])
			self.assertEqual(message, elem[1][1]) 


	def test_embeddings(self):
		equals = [
			['?', {
					'task_name':'',
					'group_name':'',
					'category_name':'',
					'is_valid': True,
					'error':'',
					'minutes':0
					} 
			],
			['? #unrealtask', {
					'task_name':'unrealtask',
					'group_name':'',
					'category_name':'',
					'is_valid': True,
					'error':'',
					'minutes':0
					} 
			],
			['? #unrealtask #realtask', {
					'task_name':'error_too_many_tasks',
					'group_name':'',
					'category_name':'',
					'is_valid': False,
					'error':'error_too_many_tasks',
					'minutes':0
					} 
			],
			['? @realgroup', {
					'task_name':'',
					'group_name':'realgroup',
					'category_name':'',
					'is_valid': True,
					'error':'',
					'minutes':0
					} 
			],
			['+ #newtask @existinggroup *existingcategory', {
					'task_name':'newtask',
					'group_name':'existinggroup',
					'category_name':'existingcategory',
					'is_valid': True,
					'error':'',
					'minutes':0
					} 
			],
			['+ #newtask @existinggroup *existingcategory *existingcategory1', {
					'task_name':'newtask',
					'group_name':'existinggroup',
					'category_name':'error_too_many_categories',
					'is_valid': False,
					'error':'error_too_many_tasks',
					'minutes':0
					} 
			],
			['1h45m #newtask', {
					'task_name':'newtask',
					'group_name':'',
					'category_name':'',
					'is_valid': True,
					'error':'',
					'minutes':105
					} 
			],			
			['10h #newtask', {
					'task_name':'newtask',
					'group_name':'',
					'category_name':'',
					'is_valid': True,
					'error':'',
					'minutes':600
					} 
			],
			['68m #newtask', {
					'task_name':'newtask',
					'group_name':'',
					'category_name':'',
					'is_valid': True,
					'error':'',
					'minutes':68
					} 
			],

			

		]

		for elem in equals:
			result = self.bot.analyze_embeddings(elem[0])
			self.assertEqual(result, elem[1])
			 


