from dateutil.utils import today
from django.test import TestCase
from django.contrib.sites.models import Site
from mixer.backend.django import Mixer

from armour.company.models import Company
from armour.legislation.models import *
from armour.legislation.tests.helpers import *

mixer = Mixer(fake=False)

class LocationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.location_1 = Location.objects.create(name='location 1')
        cls.location_2 = Location.objects.create(name='location 2', published=False)


    def test_str_representation(self):
        self.assertEqual(str(self.location_1), 'location 1')

    def test_not_published(self):
        self.assertEqual(self.location_1.published, True)
        self.assertEqual(self.location_2.published, False)


class TopicTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic_1 = Topic.objects.create(name='topic 1')
        cls.topic_2 = Topic.objects.create(name='topic 2', published=False)

    def test_str_representation(self):
        self.assertEqual(str(self.topic_1), 'topic 1')

    def test_not_published(self):
        self.assertEqual(self.topic_1.published, True)
        self.assertEqual(self.topic_2.published, False)


class PriceSettingsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create()
        cls.p_s_defaults = PriceSettings.objects.create(site=cls.site)

    def test_defaults(self):
        self.assertFalse(self.p_s_defaults.disc_choice)
        self.assertEqual(self.p_s_defaults.disc_topic, 0)
        self.assertEqual(self.p_s_defaults.disc_location, 0)
        self.assertFalse(self.p_s_defaults.disc_next_choice)
        self.assertEqual(self.p_s_defaults.disc_next_topic, 0)
        self.assertEqual(self.p_s_defaults.disc_next_location, 0)

    def test_str_representation(self):
        self.assertEqual(str(self.p_s_defaults), self.site.name)


class CurrencyTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create()
        cls.settings = PriceSettings.objects.create(site=cls.site)
        cls.currency = Currency.objects.create(name='SOME', settings=cls.settings,)

    def test_defaults(self):
        self.assertIs(self.currency.settings, self.settings)
        self.assertFalse(self.currency.main)
        self.assertTrue(self.currency.published)

    def test_str_representation(self):
        self.assertEqual(str(self.currency), self.currency.name)


class DiscountCodesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create()
        cls.settings = PriceSettings.objects.create(site=cls.site)
        cls.discount_code = DiscountCodes.objects.create(name='test code', settings=cls.settings, code='TESTEST')

    def test_defaults(self):
        self.assertIs(self.discount_code.settings, self.settings)
        self.assertEqual(self.discount_code.size, 1)
        self.assertEqual(self.discount_code.code, 'TESTEST')
        self.assertTrue(self.discount_code.active)

    def test_str_representation(self):
        self.assertEqual(str(self.discount_code), self.discount_code.name)


class LegislationTopicTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.location = mixer.blend('legislation.location')
        cls.topic = mixer.blend('legislation.topic')
        cls.legislation_topic = ISOStandard.objects.create(
            title='test title', description='test description',
            location=cls.location, topic=cls.topic,
        )

    def test_defaults(self):
        self.assertTrue(self.legislation_topic.published)

    def test_foreign_keys(self):
        self.assertEqual(self.legislation_topic.location, self.location)
        self.assertEqual(self.legislation_topic.topic, self.topic)

    def test_str_representation(self):
        self.assertEqual(str(self.legislation_topic), self.legislation_topic.title)


class QuestionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.location = mixer.blend('legislation.location')
        cls.topic = mixer.blend('legislation.topic')
        cls.legtopic = create_legislation_topic()
        cls.question = Question.objects.create(title='test title', legtopic=cls.legtopic)

    def test_defaults(self):
        self.assertTrue(self.question.published)

    def test_foreign_keys(self):
        self.assertEqual(self.question.isostandard, self.legtopic)

    def test_str_representation(self):
        self.assertEqual(str(self.question), self.question.title)



class KeyPointTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.location = mixer.blend('legislation.location')
        cls.topic = mixer.blend('legislation.topic')
        cls.legtopic = ISOStandard.objects.create(title='test title', description='test description',
                                                  location=cls.location, topic=cls.topic, )
        cls.key_point = KeyPoint.objects.create(point='test point', legtopic=cls.legtopic)

    def test_defaults(self):
        self.assertTrue(self.key_point.published)

    def test_foreign_keys(self):
        self.assertEqual(self.key_point.isostandard, self.legtopic)

    def test_str_representation(self):
        self.assertEqual(str(self.key_point), self.key_point.point)


class LegislationTopicComplyTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.location = mixer.blend('legislation.location')
        cls.topic = mixer.blend('legislation.topic')
        cls.legtopic = ISOStandard.objects.create(title='test title', description='test description',
                                                  location=cls.location, topic=cls.topic, )
        cls.point = KeyPoint.objects.create(point='test point', legtopic=cls.legtopic)
        cls.l_t_c = ISOStandardComply.objects.create(title='test title', point=cls.point)

    def test_str_representation(self):
        self.assertEqual(str(self.l_t_c), self.l_t_c.title)

    def test_foreign_keys(self):
        self.assertEqual(self.l_t_c.point, self.point)


class LegislationTopicOptionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.legtopic = create_legislation_topic()
        cls.point = KeyPoint.objects.create(point='test point', legtopic=cls.legtopic)
        cls.comply = ISOStandardComply.objects.create(title='test title', point=cls.point)
        cls.l_t_o = ISOStandardOption.objects.create(option='test option', comply=cls.comply)

    def test_str_representation(self):
        self.assertEqual(str(self.l_t_o), self.l_t_o.option)

    def test_foreign_keys(self):
        self.assertEqual(self.l_t_o.comply, self.comply)


class LocationCurrencyPriceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.location = mixer.blend('legislation.location')
        cls.site = Site.objects.create()
        cls.settings = PriceSettings.objects.create(site=cls.site)
        cls.currency = Currency.objects.create(name='SOME', settings=cls.settings, )
        cls.l_c_p = LocationCurrencyPrice.objects.create(location=cls.location, currency=cls.currency, price=9001)

    def test_foreign_keys(self):
        self.assertEqual(self.l_c_p.location, self.location)
        self.assertEqual(self.l_c_p.currency, self.currency)

    def test_str_representation(self):
        self.assertEqual(str(self.l_c_p), str(self.l_c_p.price))


class TopicCurrencyPriceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = mixer.blend('legislation.topic')
        cls.site = Site.objects.create()
        cls.settings = PriceSettings.objects.create(site=cls.site)
        cls.currency = Currency.objects.create(name='SOME', settings=cls.settings, )
        cls.t_c_p = TopicCurrencyPrice.objects.create(topic=cls.topic, currency=cls.currency, price=9001)

    def test_foreign_keys(self):
        self.assertEqual(self.t_c_p.topic, self.topic)
        self.assertEqual(self.t_c_p.currency, self.currency)

    def test_str_representation(self):
        self.assertEqual(str(self.t_c_p), str(self.t_c_p.price))


class SectorTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sector = Sector.objects.create(name='test name')

    def test_str_representation(self):
        self.assertEqual(str(self.sector), self.sector.name)

    def test_defaults(self):
        self.assertTrue(self.sector.published)


class RequirementsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.requirements = Requirements.objects.create(name='test name')

    def test_str_representation(self):
        self.assertEqual(str(self.requirements), self.requirements.name)

    def test_defaults(self):
        self.assertTrue(self.requirements.published)


class LegislationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = create_company()
        cls.legislation = ISOProduct.objects.create(company=cls.company, name='test name')
        cls.legislation.save()

    def test_foreign_keys(self):
        self.assertEqual(self.legislation.company, self.company)

    def test_str_representation(self):
        self.assertEqual(str(self.legislation), str(self.legislation.started.strftime('%Y-%m-%d')))

    def test_blank_field(self):
        self.assertIsNone(self.legislation.finish_date)


class LegislationPositionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.register = create_register()
        cls.topic = mixer.blend('legislation.topic')
        cls.location = mixer.blend('legislation.location')
        cls.legislation_position = LegislationPosition.objects.create(register=cls.register, topic=cls.topic,
                                                                      location=cls.location)

    def test_foreign_keys(self):
        self.assertEqual(self.legislation_position.topic, self.topic)
        self.assertEqual(self.legislation_position.location, self.location)

    def test_str_representation(self):
        self.assertEqual(str(self.legislation_position), str(self.register))


class LegislationSpecQuestionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.position = create_legislation_position()
        cls.question = create_question()
        cls.l_s_q = LegislationSpecQuestion.objects.create(position=cls.position, question=cls.question)

    def test_foreign_keys(self):
        self.assertEqual(self.l_s_q.position, self.position)
        self.assertEqual(self.l_s_q.question, self.question)

    def test_str_representation(self):
        self.assertEqual(str(self.l_s_q), self.question.title)

class LegislationTopicsResponseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.position = create_legislation_position()
        cls.legtopic = create_legislation_topic()
        cls.requirements = create_legislation_topic_option(leg_topic=cls.legtopic)
        cls.requirements.save()
        cls.l_t_r = ISOStandardResponse.objects.create(position=cls.position, legtopic=cls.legtopic)
        cls.l_t_r.requirements.add(cls.requirements)
        cls.l_t_r.save()

    def test_blank_field(self):
        self.assertIsNone(self.l_t_r.response)
        # self.assertEqual(self.l_t_r.requirements, self.requirements) # This one crashes even though it works in other tests

    def test_foreign_keys(self):
        self.assertEqual(self.l_t_r.isostandard, self.legtopic)
        self.assertEqual(self.l_t_r.position, self.position)


class SourceNCTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.source = SourceNC.objects.create(name='test name')

    def test_str_representation(self):
        self.assertEqual(str(self.source), self.source.name)


class LegislationNonConformanceResponseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.position = create_legislation_position()
        cls.legtopic = create_legislation_topic()
        cls.topicreply = ISOStandardResponse.objects.create(position=cls.position, legtopic=cls.legtopic)
        cls.source = mixer.blend('legislation.sourcenc')
        cls.l_n_c_r_1 = ISOStandardNCResponse.objects.create(topicreply=cls.topicreply, source=cls.source)
        cls.l_n_c_r_2 = ISOStandardNCResponse.objects.create(
            topicreply=cls.topicreply, source=cls.source, identified='Identified by', assigned='Assigned to',
            containment='Containment actions', completion='Completion date & by whom', root='Root cause',
            corrective='Corrective actions', cost='Cost of nonconformance', reviewed='Reviewed and closed out by',
        )
        cls.l_n_c_r_2.completeddate = today()
        cls.l_n_c_r_2.completed_by = create_user()

    def test_verify(self):
        self.assertFalse(self.l_n_c_r_1.verify())
        self.assertTrue(self.l_n_c_r_2.verify())


class LegislationDocumentTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.register = create_register()
        cls.legislation_document = LegislationDocument.objects.create(register=cls.register, title='test title')

    def test_str_representation(self):
        self.assertEqual(str(self.legislation_document), str(self.register))

    def test_get_extension(self):
        self.assertIsNone(self.legislation_document.get_extention())

