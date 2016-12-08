FROM praekeltfoundation/django-bootstrap:onbuild
ENV DJANGO_SETTINGS_MODULE "seed_service_rating.settings"
RUN ./manage.py collectstatic --noinput
ENV APP_MODULE "seed_service_rating.wsgi:application"
