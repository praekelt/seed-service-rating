# TODO: Add production Dockerfile to
# https://github.com/praekeltfoundation/docker-seed
FROM praekeltfoundation/django-bootstrap:py2

COPY . /app
RUN pip install -e .

ENV DJANGO_SETTINGS_MODULE "seed_service_rating.settings"
RUN ./manage.py collectstatic --noinput
CMD ["seed_service_rating.wsgi:application"]
