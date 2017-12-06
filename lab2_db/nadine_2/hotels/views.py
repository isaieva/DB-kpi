from django.db import connection, IntegrityError
from django.http import Http404
from django.shortcuts import render, redirect
from django.views import generic

from .forms import FeatureForm, CommentForm, AddCountryForm, EditCountryForm
from .models import Feature, Country, Hotel, Comment, rating_to_star_str, Room


def hotel_search(request):
    # create FULLTEXT INDEX fts_index on hotels_hotel(description);
    countries = Country.objects.raw('SELECT * FROM hotels_country')
    features = Feature.objects.raw('SELECT *, 0 as active FROM hotels_feature')
    results = []
    if request.method == 'POST':
        fts = request.POST['fts']
        min_p = request.POST['min-price']
        max_p = request.POST['max-price']
        feature_req = request.POST.getlist('features')
        country = request.POST['country']
        phrase = request.POST['phrase']

        results = Hotel.objects.raw("""
SELECT h.*, (SELECT avg(c.rating) FROM hotels_comment c WHERE hotel_id=h.id) AS rating
FROM hotels_hotel h
WHERE
  match(h.description) against(%(q)s IN BOOLEAN MODE )  
  AND (SELECT min(r.daily_ratio)
       FROM hotels_room r
       WHERE r.hotel_id = h.id) >= %(min_price)s
  AND (SELECT max(r.daily_ratio)
       FROM hotels_room r
       WHERE r.hotel_id = h.id) <= %(max_price)s
  AND ((SELECT COUNT(1)
       FROM hotels_hotel_features hf
       WHERE hf.hotel_id = h.id AND hf.feature_id IN (%(features)s)) = %(features_len)s)
ORDER BY MATCH(h.description) against(%(q)s) DESC              
        """, {
            'q': '+{} "{}"'.format(fts, phrase),
            'phrase': phrase,
            'min_price': min_p,
            'max_price': max_p,
            'features': ','.join(feature_req),
            'features_len': len(feature_req)
        })

    return render(request, "hotels/hotel-search.html", {
        'results': results,
        'countries': countries,
        'features': features
    })


def hotel_delete(request, hotel_id):
    hotel = Hotel.objects.raw('SELECT * FROM hotels_hotel WHERE id = %s', [hotel_id])[0]

    with connection.cursor() as c:
        c.execute('DELETE FROM hotels_hotel_features WHERE hotel_id = %s', [hotel.id])
        c.execute('DELETE FROM hotels_comment WHERE hotel_id = %s', [hotel.id])
        c.execute('DELETE FROM hotels_hotel WHERE id = %s', [hotel.id])
        return redirect('hotels:country-details', hotel.country_id)


def hotel_add(request):
    get_countries = 'SELECT * FROM hotels_country'
    get_features = 'SELECT *, 0 AS active FROM hotels_feature'
    countries = Country.objects.raw(get_countries)
    features = Feature.objects.raw(get_features)

    if request.method == 'POST':
        n_name = request.POST['name']
        n_brief = request.POST['brief']
        n_descr = request.POST['description']
        n_country = request.POST['country']
        n_features = request.POST.getlist('features')
        with connection.cursor() as c:
            c.execute("""
INSERT INTO hotels_hotel(name, brief_description, description, country_id)
VALUES (%s, %s, %s, %s)""", [
                n_name, n_brief, n_descr, n_country
            ])
            id = c.lastrowid

            for f in n_features:
                c.execute('INSERT INTO hotels_hotel_features(hotel_id, feature_id) VALUES (%s, %s)',
                          [id, f])

            return redirect('hotels:hotel-details', id)

    return render(request, 'hotels/hotel-edit.html', {
        'title': 'Create hotel',
        'hotel': {},
        'countries': countries,
        'features': features
    })


def hotel_edit(request, hotel_id):
    get_hotel = 'SELECT * FROM hotels_hotel WHERE id = %s'
    get_countries = 'SELECT * FROM hotels_country'
    get_hotel_features = """
SELECT f.*, isat.feature_id IS NOT NULL AS active FROM hotels_feature f
LEFT JOIN (
    SELECT feature_id FROM hotels_feature
      JOIN hotels_hotel_features h ON hotels_feature.name = h.feature_id
    WHERE h.hotel_id = %s
) isat ON isat.feature_id = f.name
 """
    hotel = Hotel.objects.raw(get_hotel, [hotel_id])[0]
    countries = Country.objects.raw(get_countries)
    features = Feature.objects.raw(get_hotel_features, [hotel.id])

    if request.method == 'POST':
        n_name = request.POST['name']
        n_brief = request.POST['brief']
        n_descr = request.POST['description']
        n_country = request.POST['country']
        n_features = request.POST.getlist('features')
        with connection.cursor() as c:
            c.execute('DELETE FROM hotels_hotel_features WHERE hotel_id=%s', [hotel.id])
            for f in n_features:
                c.execute('INSERT INTO hotels_hotel_features(hotel_id, feature_id) VALUES (%s, %s)',
                          [hotel.id, f])
            c.execute("""
            UPDATE hotels_hotel SET 
            name=%s,
            brief_description=%s,
            description=%s,
            country_id = %s
             WHERE id = %s""", [n_name, n_brief, n_descr, n_country, hotel.id])

            return redirect('hotels:hotel-details', hotel.id)

    return render(request, 'hotels/hotel-edit.html', {
        'title': 'Edit {}'.format(hotel.name),
        'hotel': hotel,
        'countries': countries,
        'features': features
    })


def feature_delete(request, feature_name):
    with connection.cursor() as c:
        c.execute('DELETE FROM hotels_feature WHERE name = %s', [feature_name])
        return redirect('hotels:features')


def comment_delete(request, id):
    get_comment = "SELECT * FROM hotels_comment WHERE id = %s"
    delete_comment = "DELETE FROM hotels_comment WHERE id = %s"

    comment = Comment.objects.raw(get_comment, [id])[0]

    with connection.cursor() as c:
        c.execute(delete_comment, [comment.id])
        return redirect("hotels:hotel-details", comment.hotel_id)


def feature_list(request):
    features_all = "SELECT * FROM hotels_feature ORDER BY name"
    feature_add = "INSERT INTO hotels_feature(name) VALUES(%s)"

    error_message = None
    if request.method == 'POST':
        form = FeatureForm(request.POST)
        if form.is_valid():
            new_name = form.cleaned_data['new_feature']
            with connection.cursor() as c:
                try:
                    c.execute(feature_add, [new_name])
                    return redirect('hotels:features')
                except IntegrityError:
                    error_message = "Feature '{}' already exists".format(new_name)
    else:
        form = FeatureForm()

    return render(request, 'hotels/feature-list.html', {
        'features': Feature.objects.raw(features_all),
        'error_message': error_message,
        'form': form
    })


def country_add(request):
    create_country = "INSERT INTO hotels_country(name, description) VALUES (%s, %s)"
    if request.method == 'POST':
        form = AddCountryForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            descr = form.cleaned_data['description']
            with connection.cursor() as c:
                c.execute(create_country, [name, descr])
                return redirect('hotels:countries')
    else:
        form = AddCountryForm()

    return render(request, 'hotels/country-edit.html', {
        'form': form
    })


def country_edit(request, country_name):
    get_country = "SELECT * FROM hotels_country WHERE name=%s"
    update_country = "UPDATE hotels_country SET description =%s WHERE NAME=%s"

    country = Country.objects.raw(get_country, [country_name])[0]

    if request.method == 'POST':
        form = EditCountryForm(request.POST)
        if form.is_valid():
            with connection.cursor() as c:
                c.execute(update_country, [form.cleaned_data['description'], country.name])
                return redirect('hotels:country-details', country.name)
    else:
        form = EditCountryForm(initial={'name': country.name, 'description': country.description})

    return render(request, 'hotels/country-edit.html', {
        'form': form,
        'title': 'Edit'
    })


class CountryList(generic.ListView):
    template_name = 'hotels/country-list.html'
    context_object_name = 'countries'

    def get_queryset(self):
        return list(Country.objects.raw(
            "SELECT * FROM hotels_country c ORDER BY c.name"
        ))


class CountryDetails(generic.TemplateView):
    template_name = 'hotels/country-details.html'

    def get_context_data(self, country_name, **kwargs):
        get_country = "SELECT * FROM hotels_country WHERE name = %s"
        get_hotels = """
SELECT h.*, avg(c.rating) AS rating
FROM hotels_hotel h
LEFT JOIN hotels_comment c ON h.id = c.hotel_id
WHERE h.country_id = %s
GROUP BY h.id
                     """
        try:
            country = Country.objects.raw(get_country, [country_name])[0]
        except IndexError:
            raise Http404("Country not found")

        hotels = Hotel.objects.raw(get_hotels, [country.name])

        context = super(CountryDetails, self).get_context_data(**kwargs)
        context['country'] = country
        context['hotels'] = hotels
        return context


def hotel_details(request, hotel_id):
    get_hotel = "SELECT * FROM hotels_hotel WHERE id = %s"
    get_comments = "SELECT * FROM hotels_comment WHERE hotel_id = %s ORDER BY sent_at DESC"
    get_rating = "SELECT avg(rating) FROM hotels_comment WHERE hotel_id = %s"
    get_features = """SELECT feature_id AS name FROM hotels_hotel_features WHERE hotel_id = %s"""
    add_comment = """
    INSERT INTO hotels_comment(name, sent_at, message, rating, hotel_id)
    VALUES (%s, now(), %s, %s, %s)
    """

    try:
        hotel = Hotel.objects.raw(get_hotel, [hotel_id])[0]
    except IndexError:
        raise Http404("Hotel not found")

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            d = comment_form.cleaned_data
            with connection.cursor() as c:
                c.execute(add_comment, [
                    d['name'],
                    d['message'],
                    d['rating'],
                    hotel.id
                ])
                r = c.fetchone()
    else:
        comment_form = CommentForm()

    comments = Comment.objects.raw(get_comments, [hotel.id])

    features = Feature.objects.raw(get_features, [hotel.id])

    with connection.cursor() as cursor:
        cursor.execute(get_rating, [hotel.id])
        rating = rating_to_star_str(cursor.fetchone()[0])

    return render(request, 'hotels/hotel-details.html', {
        'hotel': hotel,
        'rating': rating,
        'comments': list(comments),
        'features': features,
        'comment_form': comment_form
    })


def room_list(request, hotel_id):
    get_hotel = "SELECT * FROM hotels_hotel WHERE id = %s"
    get_rooms = "SELECT * FROM hotels_room WHERE hotel_id = %s ORDER BY isnull(frees_at), id"

    try:
        hotel = Hotel.objects.raw(get_hotel, [hotel_id])[0]
    except IndexError:
        raise Http404("Hotel not found")

    rooms = Room.objects.raw(get_rooms, [hotel.id])

    return render(request, 'hotels/rooms-list.html', {
        'hotel': hotel,
        'rooms': rooms
    })
