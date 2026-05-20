from django.contrib import admin
from django.utils.html import format_html
from .models import Genre, Filmwork, GenreFilmwork, Person, PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description', 'id')


class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmwork
    autocomplete_fields = ('genre',)


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmwork
    autocomplete_fields = ('person',)


@admin.register(Filmwork)
class FilmWorkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmWorkInline, PersonFilmWorkInline)
    list_display = ('poster_thumb', 'title', 'type', 'creation_date',
                    'rating', 'created_at', 'updated_at', 'get_genres')
    list_display_links = ('title',)
    list_filter = ('type',)
    search_fields = ('title', 'description', 'id')

    def poster_thumb(self, obj):
        if obj.poster:
            return format_html('<img src="{}" style="height:40px;" />', obj.poster.url)
        return '—'
    poster_thumb.short_description = 'Poster'

    def get_genres(self, obj):
        return ', '.join([genre.name for genre in obj.genres.all()])

    get_genres.short_description = 'Жанры фильма'


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'created_at')
    search_fields = ('full_name', 'id')
