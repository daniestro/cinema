import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from psqlextra.indexes import UniqueIndex


CONTENT_CATALOG = 'content\".\"'


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class CreatedMixin(models.Model):
    # Колонка в dump.sql (sprint_3) называется created_at, а не created
    created_at = models.DateTimeField(_('created'), auto_now_add=True)

    class Meta:
        abstract = True


class ModeifiedMixin(models.Model):
    # Колонка в dump.sql (sprint_3) называется updated_at, а не modified
    updated_at = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        abstract = True


class DatesMixin(CreatedMixin, ModeifiedMixin):
    class Meta:
        abstract = True


class Genre(UUIDMixin, DatesMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        db_table = CONTENT_CATALOG + 'genre'
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

    def __str__(self):
        return self.name


class Person(UUIDMixin, DatesMixin):
    full_name = models.CharField(_('full_name'), max_length=255)

    class Meta:
        db_table = CONTENT_CATALOG + 'person'
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')
        indexes = [
            models.Index(fields=['full_name'])
        ]

    def __str__(self):
        return self.full_name


def poster_upload_path(instance, filename):
    ext = filename.rsplit('.', 1)[-1].lower()
    return f'{instance.id}.{ext}'


class Filmwork(UUIDMixin, DatesMixin):

    class TypeOfContent(models.TextChoices):
        MOVIE = 'movie', _('Movie')
        TV_SHOW = 'tv_show', _('TV Show')

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), null=True, blank=True)
    creation_date = models.DateTimeField(_('creation date'))
    rating = models.FloatField(_('rating'), blank=True,
                               validators=[MinValueValidator(0),
                                           MaxValueValidator(100)],
                               default=0)
    type = models.CharField(_('type'), max_length=7,
                            choices=TypeOfContent.choices,
                            default=TypeOfContent.MOVIE)
    file_path = models.TextField(_('file path'), null=True, blank=True)
    poster = models.ImageField(_('poster'), upload_to=poster_upload_path, null=True, blank=True)
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')

    class Meta:
        db_table = CONTENT_CATALOG + 'film_work'
        verbose_name = _('Movie')
        verbose_name_plural = _('Movies')
        indexes = [
            UniqueIndex(fields=['title', 'description']),
        ]


class GenreFilmwork(UUIDMixin, CreatedMixin):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)

    class Meta:
        db_table = CONTENT_CATALOG + 'genre_film_work'
        constraints = [
            models.UniqueConstraint(fields=['genre', 'film_work'], name='soooome_name'),
        ]


class PersonFilmwork(UUIDMixin, CreatedMixin):

    class RoleChoises(models.TextChoices):
        DIRECTOR = 'DR', _('Director')
        SCREENWRITER = 'SW', _('Screenwriter')
        ACTOR = 'AC', _('Actor')

    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    role = models.CharField(_('role'), max_length=2, choices=RoleChoises.choices,
                            default=RoleChoises.ACTOR)

    class Meta:
        db_table = CONTENT_CATALOG + 'person_film_work'
        constraints = [
            models.UniqueConstraint(fields=['person_id', 'film_work_id'], name='CRINGE')
        ]


