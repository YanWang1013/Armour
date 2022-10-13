import random
from django import template
from armour.general.models import Tip

register = template.Library()


@register.simple_tag()
def random_tip_id():
    ids_list = Tip.objects.values_list('pk', flat=True).order_by('pk')

    try:
        rand_id = random.sample(list(ids_list), 1)
        rand_id = str(rand_id).strip('[]')
    except ValueError:
        return False

    return rand_id


@register.simple_tag()
def total_tips_number():
    number = len(list(Tip.objects.values_list('pk',flat=True)))
    return number


@register.simple_tag()
def prev_next_tip(current_pk):
    ids_list = list(Tip.objects.values_list('pk', flat=True).order_by('pk'))
    current_index = ids_list.index(current_pk)

    previous_pk = ids_list[current_index - 1]
    if previous_pk > current_pk:
        previous_pk = current_pk

    try:
        next_pk = ids_list[current_index + 1]
    except IndexError:
        next_pk = current_pk

    return {
        'previous': previous_pk,
        'next': next_pk,
    }
