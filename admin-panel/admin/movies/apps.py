from django.apps import AppConfig


class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movies'

    def ready(self):
        _inject_etl_dashboard_entry()


# The admin index renders apps from admin.site.get_app_list(); Django has no public
# hook for non-model links, so we wrap the method to append a synthetic entry under Movies.
def _inject_etl_dashboard_entry():
    from django.contrib import admin
    from django.urls import reverse

    original_get_app_list = admin.site.get_app_list

    def get_app_list(request, *args, **kwargs):
        app_list = original_get_app_list(request, *args, **kwargs)
        for app in app_list:
            if app['app_label'] == 'movies':
                app['models'].append({
                    'name': 'ETL Dashboard',
                    'object_name': 'ETLDashboard',
                    'admin_url': reverse('etl_dashboard'),
                    'view_only': True,
                    'add_url': None,
                })
                break
        return app_list

    admin.site.get_app_list = get_app_list
