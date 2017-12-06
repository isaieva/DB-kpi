from django.db import models

COMMENT_RATINGS = (
    (1, 'Very bad'),
    (2, 'Bad'),
    (3, 'Mediocre'),
    (4, 'Good'),
    (5, 'Awesome')
)


def rating_to_star_str(rating):
    if not rating:
        return ""
    rating = round(rating)
    return "★" * rating + "☆" * (len(COMMENT_RATINGS) - rating)


class Country(models.Model):
    name = models.CharField(max_length=150, primary_key=True)
    description = models.CharField(max_length=2000)

    def __str__(self):
        return self.name


class Feature(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class Hotel(models.Model):
    name = models.CharField(max_length=200)
    brief_description = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    features = models.ManyToManyField(Feature, blank=True)

    def __str__(self):
        return self.name


class Comment(models.Model):
    name = models.CharField(max_length=100)
    sent_at = models.DateTimeField()
    message = models.CharField(max_length=1000)
    rating = models.IntegerField(choices=COMMENT_RATINGS, blank=True, null=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.PROTECT)

    def get_stars(self):
        return rating_to_star_str(self.rating)

    def __str__(self):
        if self.rating:
            rating = self.get_rating_display()
        else:
            rating = "no rating"
        return "Comment by {} at {}, {}".format(self.name, self.sent_at, rating)


class Room(models.Model):
    frees_at = models.DateTimeField(blank=True,null=True)
    description = models.CharField(max_length=100)
    daily_ratio = models.FloatField()
    hotel = models.ForeignKey(Hotel, on_delete=models.PROTECT)

    def is_free(self):
        return not bool(self.frees_at)

    def __str__(self):
        if self.frees_at:
            free_str = "frees at {}".format(self.frees_at)
        else:
            free_str = "free"
        return "#{}, {} for {}$ per day, {}".format(self.id, self.description, self.daily_ratio, free_str)