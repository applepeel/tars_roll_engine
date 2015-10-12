from __future__ import absolute_import

from django.conf import settings

if "raven.contrib.django.raven_compat" in settings.INSTALLED_APPS:
    import celery
    import raven
    from raven.contrib.celery import register_signal, register_logger_signal

    class Celery(celery.Celery):

        def on_configure(self):
            client = raven.Client(settings.RAVEN_CONFIG['dsn'])

            # register a custom filter to filter out duplicate logs
            register_logger_signal(client)

            # hook into the Celery error handler
            register_signal(client)
else:
    from celery import Celery

app = Celery('roll_engine')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {!r}'.format(self.request))
