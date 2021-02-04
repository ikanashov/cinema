from django.core.paginator import EmptyPage
from django.http import JsonResponse
from django.views import View

class MoviesListApi(View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        # Получение и обработка данных
        return JsonResponse({'test':1})


from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView

from cinema.models import FilmWork, FilmCrewRole


class Movies(BaseListView):
    model = FilmWork
    #Не забыть избавиьтся от магических ЦИФР!!!
    paginate_by = 5
    http_method_names = ['get']  # Список методов, которые реализует обработчик
    queryset =  model.objects.prefetch_related('genres', 'crew').select_related('type')
    #queryset =  model.objects.select_related('type')
    #queryset =  model.objects.prefetch_related('genres', 'crew')
    #queryset =  model.objects.all()
    #queryset = model.objects.prefetch_related('genres', 'crew').select_related('type').filter(imdb_tconst__exact='tt0175245')
    #queryset = model.objects.prefetch_related('genres', 'crew').select_related('type').filter(title__icontains='Star')

    #def get_queryset(self):
        #queryset =  self.model.objects.all().values()
        #z = self.model.objects.aggregate(ArrayAgg('title'))
        #print(z)
        #z = {'q', 'tosi bosi'}
        #return queryset # Сформированный QuerySet
   
    def get_context_data(self, *, object_list=None, **kwargs):
        page = self.request.GET.get('page', 1)
        context = {}
        paginator = self.get_paginator(self.get_queryset(), self.paginate_by)
        currentpage = paginator.get_page(page)
        context['count'] = paginator.count
        context['total_pages'] = paginator.num_pages
        if currentpage.has_previous():
            context['prev'] = currentpage.previous_page_number()
        else:
            context['prev'] = None
        if currentpage.has_next():
            context['next'] = currentpage.next_page_number()
        else:
            context['next'] = None
        context['result'] = []
        for film in currentpage.object_list:
            film_dict = {
                'id':  film.id,
                'title': film.title,
                'description': film.description,
                'creation_date': film.creation_date,
                'rating': film.rating,
                'type': film.type.name,
                'genres': list(film.genres.values_list('name', flat=True)),
                #такой код сделает меньше запросов, но надо будет вручную отбирать профессии
                #'persons': list(film.crew.values_list('full_name', flat=True)), 
                'actors': list(film.crew.filter(filmworkperson__role=FilmCrewRole.ACTOR).values_list('full_name', flat=True)),
                'directors': list(film.crew.filter(filmworkperson__role=FilmCrewRole.DIRECTOR).values_list('full_name', flat=True)),
                'writers': list(film.crew.filter(filmworkperson__role=FilmCrewRole.WRITER).values_list('full_name', flat=True)),
            }
            context['result'].append(film_dict)
        return context

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)