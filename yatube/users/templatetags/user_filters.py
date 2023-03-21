from django import template
from posts.models import Like

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={"class": css})


@register.simple_tag
def is_like(post, user):
    return Like.objects.filter(post=post, user=user).exists()

@register.simple_tag
def count_like(post):
    return Like.objects.filter(post=post).count()