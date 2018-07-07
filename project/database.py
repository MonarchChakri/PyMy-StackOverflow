import os

from django.conf import settings


engines = {
    'sqlite': 'django.db.backends.sqlite3',
    'postgresql': 'django.db.backends.postgresql_psycopg2',
    'mysql': 'django.db.backends.mysql',
}


def config():
    service_name = os.getenv('DATABASE_SERVICE_NAME', 'mysql').upper().replace('-', '_')
    if service_name:
        engine = engines.get(os.getenv('DATABASE_ENGINE', 'mysql'), engines['sqlite'])
    else:
        engine = engines['sqlite']
    name = os.getenv('DATABASE_NAME', 'sodb')
    if not name and engine == engines['sqlite']:
        name = os.path.join(settings.BASE_DIR, 'db.sqlite3')
    return {
        'ENGINE': engine,
        'NAME': name,
        'USER': os.getenv('DATABASE_USER', 'mc'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'pword'),
        'HOST': os.getenv('{}_SERVICE_HOST'.format(service_name), '127.0.0.1'),
        'PORT': os.getenv('{}_SERVICE_PORT'.format(service_name), '15432'),
    }
