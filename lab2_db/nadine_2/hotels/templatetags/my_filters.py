from django.template.defaulttags import register
from ..models import rating_to_star_str

@register.filter
def to_stars(rating):
    return rating_to_star_str(rating)


