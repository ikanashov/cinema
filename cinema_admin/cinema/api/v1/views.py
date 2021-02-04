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

from cinema.models import FilmWork


class Movies(BaseListView):
    model = FilmWork
    #Не забыть избавиьтся от магических ЦИФР!!!
    paginate_by = 5
    http_method_names = ['get']  # Список методов, которые реализует обработчик
    queryset =  model.objects.prefetch_related('genres', 'crew').select_related('type')[:1]
    #queryset = model.objects.prefetch_related('genres', 'crew').select_related('type').filter(imdb_tconst__exact='tt0049793')
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
        paginator = self.get_paginator(self.queryset, self.paginate_by)
        currentpage = paginator.get_page(page)
        #queryset = self.get_queryset()
        #genres = [list(film.genres.values()) for film in queryset]
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
        context['result'] = list(currentpage.object_list.values('id', 'title', 'description', 'creation_date', 'rating', 'type__name'))
        print(paginator.page(page).object_list)
        #context['results'] = list(queryset.values('id', 'title', 'description', 'creation_date', 'rating', 'type__name'))
        return context

    def render_to_response(self, context, **response_kwargs):
        #print(type(context))
        return JsonResponse(context)