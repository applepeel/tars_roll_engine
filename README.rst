=====
Roll Engine
=====

Roll Engine is designed to implement rollout strategy in batch granularity.

Quick start
-----------

1. Add "roll_engine" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'roll_engine',
    )

2. Run `python manage.py celery -A roll_engine worker -l info` to start worker service.
   Or export `DJANGO_SETTINGS_MODULE` environment before you run `celery -A roll_engine worker -i info`::

   # e.g. in tars django project
   export DJANGO_SETTINGS_MODULE='tars.settings'
