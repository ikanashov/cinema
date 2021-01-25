from django.contrib import admin
from django.contrib.admin.options import TabularInline

from .models import FilmGenre, FilmPerson, FilmType, FilmWork, FilmWorkGenre, FilmWorkPerson


@admin.register(FilmGenre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description'
    )


@admin.register(FilmPerson)
class PersonAdmin(admin.ModelAdmin):
    pass


@admin.register(FilmType)
class TypeAdmin(admin.ModelAdmin):
    pass


class FilmGenreInline(admin.TabularInline):
    model = FilmWorkGenre
    extra = 0
    fields = (
        'genre',
    )


class FilmWorkPersonInline(admin.TabularInline):
    model = FilmWorkPerson
    extra = 0


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'type',
        'creation_date'
    )
    list_filter = (
        'type',
        'genres',
    )
    fields = (
        'title',
        'type',
        'rating',
        'creation_date',
        'end_date',
        'imdb_tconst',
        #'genres',
        'certificate',
        'file_path',
        'description'
        #'crew'
    )
    inlines = [
        FilmGenreInline,
        FilmWorkPersonInline,
    ]
    #imdb_pconst = models.CharField(_('imdb parrent'), max_length=255, blank=True, null=True)
    #description = models.TextField(_('описание'), blank=True)
    #end_date = models.DateField(_('дата завершения'), blank=True, null=True)
    #season_number = models.PositiveSmallIntegerField(_('сезон'), blank=True, null=True)
    #episode_number = models.PositiveSmallIntegerField(_('эпизод'), blank=True, null=True)
