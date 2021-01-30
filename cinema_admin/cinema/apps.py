from django.apps import AppConfig


class CinemaConfig(AppConfig):
    name = 'cinema'

    def ready(self):
        print ('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        import cinema.signals
