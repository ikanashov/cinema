from django.apps import AppConfig


class CinemaConfig(AppConfig):
    name = 'cinema'
    movies_per_page = 5
    def ready(self):
        print ('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        import cinema.signals
