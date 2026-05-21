from django.contrib import admin
from django.urls import path

from movies.etl_views import etl_dashboard, etl_reset, etl_trigger
from movies.featured_views import featured_dashboard, featured_save


urlpatterns = [
    path('etl/', etl_dashboard, name='etl_dashboard'),
    path('etl/trigger/', etl_trigger, name='etl_trigger'),
    path('etl/reset/', etl_reset, name='etl_reset'),
    path('featured/', featured_dashboard, name='featured_dashboard'),
    path('featured/save/', featured_save, name='featured_save'),
    path('', admin.site.urls),
]
