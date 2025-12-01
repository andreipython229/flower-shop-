import os
import warnings

from django.core.asgi import get_asgi_application

# Подавление предупреждений об устаревших пакетах
warnings.filterwarnings("ignore", category=UserWarning, module="coreapi")
warnings.filterwarnings("ignore", message=".*pkg_resources.*")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
application = get_asgi_application()
