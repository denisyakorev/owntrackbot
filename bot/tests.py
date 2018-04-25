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
		self.last_activity = self.profile.last_activity.strftime("%d.%m.%Y")



	def test_message_out(self):
		
		equals = [
			['?', 'spent time: 0\nlast activity: '+self.last_activity+'\ninfo about categories in profile: default: 0\n'],

			['? #unrealtask', 'Task does not exist'],

			['+ #newtask',"Task created successfully"],

			['+ #newtask',"Task with the name already exists in the group"],

			['? #newtask',	"spent time: 0\nlast activity: "+self.last_activity+"\ngroup: default"],

			['+ @newgroup',"Group created successfully"],

			['+ #newtask @newgroup',"Task created successfully"],

			['? #newtask', "spent time: 0\nlast activity: "+self.last_activity+"\ngroup: default"],

			['?#newtask', "spent time: 0\nlast activity: "+self.last_activity+"\ngroup: default"],

			['? @newgroup',"spent time: 0\nlast activity: "+self.last_activity+"\ncategory: default\ninfo about active tasks: newtask: 0\n"],

			['? @default',"spent time: 0\nlast activity: "+self.last_activity+"\ncategory: default\ninfo about active tasks: newtask: 0\n"],

			['? *default',"spent time: 0\nlast activity: "+self.last_activity+"\ninfo about groups in category: default: 0\nnewgroup: 0\n"],

			['? @unrealgroup',"Group does not exist"],

			['+ *newcategory',"Category created successfully"],

			['+ @newgroup *newcategory',"Group created successfully"],

			['+ #newtask @newgroup *newcategory',"Task created successfully"],

			['? *newcategory',"spent time: 0\nlast activity: "+self.last_activity+"\ninfo about groups in category: newgroup: 0\n"],

			['? *unrealcategory',"Category does not exist"],

			['+ #newtask @newgroup2 *newcategory',"Something wrong with your command"],

			['+ #newtask #newtask2 @existinggroup *existingcategory',"Something wrong with your command"],

			['+ #newtask @newgroup @existinggroup1 *newcategory',"Something wrong with your command"],

			['+ #newtask @newgroup *newcategory *newcategory1',"Something wrong with your command"],

			['+ @newgroup *newcategory',"Group with the name already exists in the category"],

			['+ @newgroup #newtask3 *newcategory',"Task created successfully"],

			['+ @newgroup *newcategory  #newtask4',"Task created successfully"],

			['+ *newcategory @newgroup  #newtask5',"Task created successfully"],

			['+ *newcategory @existinggroup',"Group created successfully"],

			['+ *newcategory2',"Category created successfully"],

			['+ *newcategory2',"Category with the name already exists in the profile"],

			['1h23m #newtask',"spent time: 1h 23m\nlast activity: "+self.last_activity+"\ngroup: default"],

			['1h23m #newtask @newgroup *newcategory',"spent time: 1h 23m\nlast activity: "+self.last_activity+"\ngroup: newgroup"],

			['? @newgroup *newcategory',"spent time: 1h 23m\nlast activity: "+self.last_activity+"\ncategory: newcategory\ninfo about active tasks: newtask: 1h 23m\nnewtask3: 0\nnewtask4: 0\nnewtask5: 0\n"],

			['? *newcategory',"spent time: 1h 23m\nlast activity: "+self.last_activity+"\ninfo about groups in category: newgroup: 1h 23m\nexistinggroup: 0\n"],

			['+1h23m #newtask6',"Task created successfully"],

			['+1h23m #newtask',"Task with the name already exists in the group"],

			['?1h23m #newtask',"spent time: 1h 23m\nlast activity: "+self.last_activity+"\ngroup: default"],

			['23m #newtask',"spent time: 1h 46m\nlast activity: "+self.last_activity+"\ngroup: default"],

			['23 #existingtask',"Something wrong with your command"],

			['m #existingtask',"Something wrong with your command"],

			['! #existingtask',"Something wrong with your command"],

			['! #newtask',"spent time: 1h 46m\nlast activity: "+self.last_activity+"\ngroup: default"],

			['! @existinggroup',"You should write right task"],

			['! *existingcategory',"You should write right task"]

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
			 


