from django.http import JsonResponse
from django.views.generic.list import BaseListView

from cinema.models import FilmWork, FilmCrewRole
from cinema.apps import CinemaConfig


class Movies(BaseListView):
    model = FilmWork
    queryset =  model.objects.select_related('type')
    ordering = 'id'
    paginate_by = CinemaConfig.movies_per_page
    http_method_names = ['get']
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk:
            self.queryset = self.queryset.filter(id__exact=pk) 
        queryset = super().get_queryset()
        return queryset
   
    def get_context_data(self, *, object_list=None, **kwargs):
        paginator, currentpage, pageobjects, is_paginated = self.paginate_queryset(self.get_queryset(), self.paginate_by)
        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': None,
            'next': None,
            'results': []
        }
        if currentpage.has_previous():
            context['prev'] = currentpage.previous_page_number()
        if currentpage.has_next():
            context['next'] = currentpage.next_page_number()
        for film in pageobjects:
            film_dict = {
                'id':  film.id,
                'title': film.title,
                'description': film.description,
                'creation_date': film.creation_date,
                'rating': film.rating,
                'type': film.type.name,
                'genres': list(film.genres.values_list('name', flat=True)),
                'actors': list(film.crew.filter(filmworkperson__role=FilmCrewRole.ACTOR).values_list('full_name', flat=True)),
                'directors': list(film.crew.filter(filmworkperson__role=FilmCrewRole.DIRECTOR).values_list('full_name', flat=True)),
                'writers': list(film.crew.filter(filmworkperson__role=FilmCrewRole.WRITER).values_list('full_name', flat=True)),
            }
            if is_paginated:
                context['results'].append(film_dict)
            else:
                return film_dict
        return context

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)