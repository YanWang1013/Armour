from mixer.backend.django import mixer

from armour.company.models import Company
from armour.legislation.models import *
from armour.user.models import User


def create_company():
    site = Site.objects.get_or_create(domain='dev.armour.ai', name='dev')[0]
    company_settings = PriceSettings.objects.get_or_create(site=site)[0]
    locations = mixer.blend('legislation.location')
    topics = mixer.blend('legislation.topic')
    currency = Currency.objects.get_or_create(name='SOME', settings=company_settings, )[0]
    currency.save()
    sector = mixer.blend('legislation.sector')
    req = mixer.blend('legislation.Requirements')
    company = Company.objects.create(
        name='test name', street='street', zipcode='zip', city='city', email='test@example.com',
        website='www.website.com', country='PL', vat='vat', currency=currency,
        scope='scope',
    )
    company.locations.add(locations)
    company.topics.add(topics)
    company.sector.add(sector)
    company.req.add(req)
    company.active = True
    company.specqgenerated = True
    company.save()

    return company


def create_user():
    company = create_company()
    user = User.objects.create(email='user@example.com', company=company)

    return user


def create_register():
    company = create_company()
    register = ISOProduct.objects.create(company=company, name='test name')
    register.save()

    return register


def create_legislation_topic():
    location = mixer.blend('legislation.location')
    topic = mixer.blend('legislation.topic')
    legislation_topic = ISOStandard.objects.create(
        title='test title', description='test description',
        location=location, topic=topic,
    )
    legislation_topic.save()
    return legislation_topic


def create_legislation_position():
    register = create_register()
    topic = mixer.blend('legislation.topic')
    location = mixer.blend('legislation.location')
    legislation_position = LegislationPosition.objects.create(register=register, topic=topic,
                                                              location=location)
    legislation_position.save()
    return legislation_position


def create_legislation_non_conformance_response(pk=''):
    position = create_legislation_position()
    legtopic = create_legislation_topic()
    topicreply = ISOStandardResponse.objects.create(position=position, legtopic=legtopic)
    source = mixer.blend('legislation.sourcenc')
    if pk == '' or None:
        l_n_c_r_1 = ISOStandardNCResponse.objects.create(topicreply=topicreply, source=source)
    else:
        l_n_c_r_1 = ISOStandardNCResponse.objects.create(topicreply=topicreply, source=source, id=pk)
    return l_n_c_r_1


def create_question():
    legtopic = create_legislation_topic()
    legtopic.save()
    question = Question.objects.create(title='test title', legtopic=legtopic)
    question.save()
    return question


def create_legislation_topic_option(leg_topic=''):
    if leg_topic == '' or None:
        legtopic = create_legislation_topic()
    else:
        legtopic = leg_topic

    # legtopic = create_legislation_topic()
    point = KeyPoint.objects.create(point='test point', legtopic=legtopic)
    comply = ISOStandardComply.objects.create(title='test title', point=point)
    l_t_o = ISOStandardOption.objects.create(option='test option', comply=comply)

    return l_t_o
