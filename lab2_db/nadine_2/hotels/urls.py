from django.urls import path

from . import views 

app_name = 'hotels'

urlpatterns =  [
    path('', views.CountryList.as_view(), name='index'),
    path('features/', views.feature_list, name='features'),
    path('features/<feature_name>/delete/', views.feature_delete, name='feature-delete'),
    path('countries/', views.CountryList.as_view(), name='countries'),
    path('countries/<country_name>/', views.CountryDetails.as_view(), name='country-details'),
    path('hotels/<int:hotel_id>/', views.hotel_details, name='hotel-details'),
    path('hotels/<int:hotel_id>/rooms', views.room_list, name='hotel-rooms'),
    path('hotels/<int:hotel_id>/edit', views.hotel_edit, name='hotel-edit'),
    path('hotels/add', views.hotel_add, name='hotel-add'),
    path('hotels/<int:hotel_id>/delete', views.hotel_delete, name='hotel-delete'),
    path('countries/<country_name>/edit', views.country_edit, name='country-edit'),
    path('countries/add', views.country_add, name='country-add'),
    path('comments/<int:id>/delete', views.comment_delete, name='comment-delete'),
    path('search/', views.hotel_search, name='search')
]
