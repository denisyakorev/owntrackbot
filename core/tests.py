from django.test import TransactionTestCase, TestCase
from core.models import Profile, Category
from core.views import get_profile_data

# Create your tests here.
class CoreTestCase(TransactionTestCase):

    def setUp(self):
        self.profile = Profile(username='denis', spent_time=133)
        self.profile.save()
        category1 = Category(name="Категория1", profile=self.profile, spent_time=63)
        category1.save()
        category2 = Category(name="Категория2", profile=self.profile, spent_time=70)
        category2.save()

    def test_get_info(self):
        result = get_profile_data(self.profile)
        self.assertEqual(result['spent_time'], '2h 13m')
        self.assertEqual(result['categories'][0]['name'], 'Категория1')
        self.assertEqual(result['categories'][0]['spent_time'], '1h 3m')
        self.assertEqual(result['categories'][1]['name'], 'Категория2')
        self.assertEqual(result['categories'][1]['spent_time'], '1h 10m')