from .users import urlpatterns as user_urls
from .credentials import urlpatterns as credentials_urls

urlpatterns = [
    *user_urls, *credentials_urls
]