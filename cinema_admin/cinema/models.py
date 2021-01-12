import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.fields import AutoCreatedField

from model_utils.models import TimeStampedModel


class TimeStampedWithId(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class FilmGenre(TimeStampedWithId):
    name = models.CharField(_('название'), max_length=255, null=False, unique=True)
    description = models.TextField(_('описание'), blank=True) #description TEXT, ??? not null ?
    migrated_from = models.CharField(_('мигрировано'), max_length=255, blank=True) # migrated_from TEXT,??? not null ?

    class Meta:
        verbose_name = (_('жанр'))
        verbose_name_plural = (_('жанры'))
        db_table = 'film_genre'

    def __str__(self) -> str:
        return self.name


class FilmType(TimeStampedWithId):
    name = models.CharField(_('название'), max_length=255, null=False, unique=True)
    description = models.TextField(_('описание'), blank=True) #description TEXT, ??? not null ?

    class Meta:
        verbose_name = (_('тип'))
        verbose_name_plural = (_('типы'))
        db_table = 'film_type'

    def __str__(self) -> str:
        return self.name


class FilmPerson(TimeStampedWithId):
    full_name = models.CharField(_('полное имя'), max_length=255) #full_name TEXT NOT NULL,
    imdb_nconst = models.CharField(_('imdb id'), max_length=255, blank=True) #imdb_nconst TEXT,??? not null ?
    birth_date = models.DateField(_('дата рождения'), blank=True, null=True) #birth_date DATE,
    death_date = models.DateField(_('дата смерти'), blank=True, null=True) #death_date DATE,
    migrated_from = models.CharField(_('мигрировано'), max_length=255, blank=True) # migrated_from TEXT,??? not null ?

    class Meta:
        verbose_name = (_('участник съемочной группы'))
        verbose_name_plural = (_('участники съемочоной группы'))
        db_table = 'film_person'

    def __str__(self) -> str:
        return self.full_name


class FilmWork(TimeStampedWithId):
    imdb_tconst = models.CharField(_('imbd id'), max_length=255) #imdb_tconst TEXT NOT NULL,
    imdb_pconst = models.CharField(_('imdb parent id'), max_length=255, blank=True, null=True) #imdb_pconst TEXT, -- Для произведений с сериями (родительское произведение)
    title = models.CharField(_('название'), max_length=255) #title TEXT NOT NULL,
    description = models.TextField(_('описание'), blank=True) #description TEXT, ??? not null ?
    creation_date = models.DateField(_('дата создания')) #creation_date DATE,
    end_date = models.DateField(_('дата завершения'), blank=True, null=True) #end_date DATE, -- Для произведений с сериями дата выхода последней серии 
    certificate = models.TextField(_('возрастные ограничения'), blank=True) #certificate TEXT, ??? not null ?
    file_path = models.CharField(_('имя файла'), max_length=255, blank=True) #file_path TEXT, ??? not null ?
    rating = models.FloatField(_('рейтинг'), validators=[MinValueValidator(0)], default=0.0, blank=True) #rating FLOAT, -- Рейтинг imdb
    season_number = models.PositiveSmallIntegerField(_('сезон'), blank=True, null=True) #season_number INTEGER, -- Для произведений с сериями номер сезона 
    episode_number = models.PositiveSmallIntegerField(_('эпизод'), blank=True, null=True) #episode_number INTEGER, -- Для произведений с сериями номер серии 
    genres = models.ManyToManyField(FilmGenre, through='FilmWorkGenre')

    class Meta:
        verbose_name = (_('кинопроизведение'))
        verbose_name_plural = (_('кинопроизведения'))
        db_table = 'film_work'

    def __str__(self) -> str:
        return self.title


class FilmWorkGenre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    migrated_from = models.CharField(_('мигрировано'), max_length=255, blank=True) # migrated_from TEXT,??? not null ?
    created = AutoCreatedField(_('создано'))
    film_work = models.ForeignKey(
        FilmWork,
        on_delete=models.CASCADE,
    )
    genre = models.ForeignKey(
        FilmGenre,
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['genre', 'film_work'], name='uniquie_film_genre')
        ]
        db_table = 'film_work_genre'
        verbose_name = _('жанр кинопроизведения')
        verbose_name_plural = _('жанры кинопроизведения')

    def __str__(self):
        return f'{self.film_work_id.title}  {self.genre_id.name}'
