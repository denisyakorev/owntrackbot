from django.test import TestCase
from bot.models import Bot

# Create your tests here.
class BotTestCase(TestCase):
	def setUp(self):
		self.bot = Bot.objects.get_or_create_bot('telegram')


	def check_out_message(self):
		
		"""Проверяет правильность анализа сообщений"""
		equals = [
			['?', 
				[
					['read', 'user_profile'],
				],
			],

			['? #unrealtask', 
				[
					['read', 'error_task_does_not_exist'],
				]
			],

			['? #realtask',
				[
					['read', 'task_id']
				]
			],

			['? #realtaskWithTwinInOtherGroup',
				[
					['read', 'error_too_more_objects']
				]
			],

			['?#realtask',
				[
					['read', 'task_id']
				]

			],

			['? @realgroup',
				[
					['read', 'group_id']
				]

			],

			['? @unrealgroup',
				[
					['read', 'error_group_does_not_exist']
				]

			],

			['? *realcategory',
				[
					['read', 'category_id']
				]

			],

			['? *unrealcategory',
				[
					['read', 'error_category_does_not_exist']
				]

			],

			['+ #newtask',
				[
					['create', 'task_newtask in group default in category default']
				]

			],

			['+ #existingtask',
				[
					['create', 'error_task_exists']
				]
			],

			['+ #newtask @existinggroup',
				[
					['create', 'task_newtask in group existinggroup in category default']
				]
			],

			['+ #newtask @existinggroup *existingcategory',
				[
					['create', 'task_newtask in group existinggroup in category existingcategory']
				]
			],

			['+ #newtask @newgroup *existingcategory',
				[
					['create', 'error_group_does_not_exists']
				]
			],

			['+ #newtask @existinggroup *newcategory',
				[
					['create', 'error_category_does_not_exists']
				]
			],

			['+ #newtask #newtask2 @existinggroup *existingcategory',
				[
					['create', 'error_too_many_tasks']
				]
			],

			['+ #newtask @existinggroup @existinggroup1 *existingcategory',
				[
					['create', 'error_too_many_groups']
				]
			],

			['+ #newtask @existinggroup *existingcategory *existingcategory1',
				[
					['create', 'error_too_many_categories']
				]
			],

			['+ @existinggroup *existingcategory',
				[
					['create', 'error_group_exists']
				]
			],

			['+ @newgroup *existingcategory',
				[
					['create', 'group_newgroup in category existingcategory']
				]
			],

			['+ @existinggroup #newtask *existingcategory',
				[
					['create', 'task_newtask in group existinggroup in category existingcategory']
				]
			],

			['+ @existinggroup *existingcategory  #newtask',
				[
					['create', 'task_newtask in group existinggroup in category existingcategory']
				]
			],

			['+ *existingcategory @existinggroup  #newtask',
				[
					['create', 'task_newtask in group existinggroup in category existingcategory']
				]
			],

			['+ *existingcategory @existinggroup',
				[
					['create', 'error_group_exists']
				]
			],

			['+ *newcategory @existinggroup',
				[
					['create', 'error_category_does_not_exists']
				]
			],

			['+ *newcategory',
				[
					['create', 'category_newcategory']
				]
			],

			['+ *existingcategory',
				[
					['create', 'error_category_exists']
				]
			],

			['1h23m #task1',
				[
					['update', 'add 83 min to task1']
				]
			],

			['1h23m #taskWithTwinInOtherGroup',
				[
					['update', 'error_too_many_tasks']
				]
			],

			['+1h23m #newtask',
				[
					['update', 'error_task_does_not_exists']
				]
			],

			['+1h23m #existingtask',
				[
					['update', 'error_task_does_not_exists']
				]
			],

			['?1h23m #existingtask',
				[
					['read', 'task_existingtask']
				]
			],

			['23m #existingtask',
				[
					['read', 'add 23 min to task1']
				]
			],

			['23 #existingtask',
				[
					['read', 'error_unknown_command']
				]
			],

			['m #existingtask',
				[
					['read', 'error_unknown_command']
				]
			],

			['! #existingtask',
				[
					['finish', 'task_existingtask']
				]
			]



		]

		for elem in equals:
			self.assertEqual(self.bot.analyze_message(equals[elem][0]), equals[elem][1])
		



