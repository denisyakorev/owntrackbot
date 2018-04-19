from django.test import TransactionTestCase, TestCase
from bot.models import Bot
from core.models import Profile

# Create your tests here.
class BotTestCase(TransactionTestCase):
	
	def setUp(self):
		self.bot = Bot.objects.get_or_create_bot('telegram')
		self.profile = Profile.objects.get_or_create_profile(
			user_id= 1,
			client_type= 'telegram'
			)
		self.last_activity = self.profile.last_activity.strftime("%Y-%m-%d")



	def test_message_out(self):
		
		equals = [
			['?', 'spent time: 0\ncompleted tasks: 0\nlast activity: '+self.last_activity+'\ninfo about categories in profile: default: 0\n'],

			['? #unrealtask', 'Task does not exist'],

			['+ #newtask',"Task created successfully"],

			['+ #newtask',"Task with the name already exists in the group"],

			['? #newtask',	"name: newtask\ngroup: default\ncreated at: "+self.last_activity+"\nspent time: 0\nlast activity: "+self.last_activity],

			['+ @newgroup',"Group created successfully"],

			['+ #newtask @newgroup',"Task created successfully"],

			['? #newtask', "name: newtask\ngroup: default\ncreated at: "+self.last_activity+"\nspent time: 0\nlast activity: "+self.last_activity],

			['?#newtask', "name: newtask\ngroup: default\ncreated at: "+self.last_activity+"\nspent time: 0\nlast activity: "+self.last_activity],

			['? @newgroup',"name: newgroup\ncreated at: "+self.last_activity+"\ncategory: default\nspent time: 0\ncompleted tasks: 0\nlast activity: "+self.last_activity+"\ninfo about active tasks: newtask: 0\n"],

			['? @unrealgroup',"Group does not exist"],

			['+ *newcategory',"Category created successfully"],

			['+ @newgroup *newcategory',"Group created successfully"],

			['+ #newtask @newgroup *newcategory',"Task created successfully"],

			['? *newcategory',"spent time: 0\ncompleted tasks: 0\nlast activity: "+self.last_activity+"\ninfo about groups in category: newgroup: 0\n"],

			['? *unrealcategory',"Category does not exist"],

			['+ #newtask @newgroup2 *newcategory',"Something wrong with your command"],

			['+ #newtask #newtask2 @existinggroup *existingcategory',"Something wrong with your command"],

			['+ #newtask @newgroup @existinggroup1 *newcategory',"Something wrong with your command"],

			['+ #newtask @newgroup *newcategory *newcategory1',"Something wrong with your command"],

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
			print(elem)
			out_message = self.bot.make_command(elem[0], self.profile, elem)
			print(out_message+"\n\n")
			self.assertEqual(out_message, elem[1]) 


	def _test_embeddings(self):
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
			print (result)
			self.assertEqual(result, elem[1])
			 


