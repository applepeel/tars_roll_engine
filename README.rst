=====
Roll Engine
=====

Roll Engine is designed to implement rollout strategy in batch granularity.

Quick start
-----------

1. Add "polls" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'roll_engine',
    )

2. Run `python manage.py celery -A roll_engine worker -l info` to start worker service
