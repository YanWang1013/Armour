from django.test import TestCase
from armour.general.models import Tip

class TestTipModel(TestCase):
    def setUp(self):
        Tip.objects.create(name='Test Name', content='Some content')
        Tip.objects.create(name='name 2', content='second content')

    def test_does_create_and_no_avatar(self):
        tip = Tip.objects.get(name='Test Name')
        tip_2 = Tip.objects.get(name='name 2')

        self.assertFalse(bool(tip.avatar))
        self.assertEqual(Tip.objects.all().count(), 2)
        self.assertEqual(tip_2.name, 'name 2')

    def test_does_return_str(self):
        tip = Tip.objects.get(name='Test Name')

        self.assertEqual(str(tip), 'Test Name')
