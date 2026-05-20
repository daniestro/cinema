from django.contrib import admin
from django.urls import path

from movies.etl_views import etl_dashboard, etl_reset, etl_trigger


urlpatterns = [
    path('etl/', etl_dashboard, name='etl_dashboard'),
    path('etl/trigger/', etl_trigger, name='etl_trigger'),
    path('etl/reset/', etl_reset, name='etl_reset'),
    path('', admin.site.urls),
]
