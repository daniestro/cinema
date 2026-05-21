from django.apps import AppConfig


class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movies'

    def ready(self):
        _inject_custom_admin_entries()


# The admin index renders apps from admin.site.get_app_list(); Django has no public
# hook for non-model links, so we wrap the method to append synthetic entries under Movies.
def _inject_custom_admin_entries():
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
                app['models'].append({
                    'name': 'Featured Block',
                    'object_name': 'FeaturedBlock',
                    'admin_url': reverse('featured_dashboard'),
                    'view_only': True,
                    'add_url': None,
                })
                break
        return app_list

    admin.site.get_app_list = get_app_list
