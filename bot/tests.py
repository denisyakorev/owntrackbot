from django.test import TestCase
from bot.models.py import Bot

# Create your tests here.
class MessageAnalysysTest(TestCase):
	def setUp(self):
		self.bot = Bot.objects.get(messager='telegram')

	def check_out_message(self):
		"""Проверяет правильность анализа сообщений"""
		equals = [
			['?', 
				[
					['get_info', 'user_profile'],
				],
			],

			['? #unrealtask', 
				[
					['get_info', 'error_task_does_not_exist'],
				]
			],

			['? #realtask',
				[
					['get_info', 'task_id']
				]
			],

			['?#realtask',
				[
					['get_info', 'task_id']
				]

			],

			['? @realgroup',
				[
					['get_info', 'group_id']
				]

			],

			['? @unrealgroup',
				[
					['get_info', 'error_group_does_not_exist']
				]

			],

			['? *realcategory',
				[
					['get_info', 'category_id']
				]

			],

			['? *unrealcategory',
				[
					['get_info', 'error_category_does_not_exist']
				]

			],

			['+ #newtask',
				[
					['create', 'task_newtask']
				]

			],

			['+ #existingtask',
				[
					['create', 'error_task_exists']
				]
			],

			['+ #newtask @existinggroup',
				[
					['get', 'error_task_exists']
				]
			]


		]

		self.assertEqual(bot.analyze_message())
		pass

