from .users import urlpatterns as users_urls
from .matches import urlpatterns as matches_urls
from .credentials import urlpatterns as credentials_urls

urlpatterns = [
    *users_urls, *matches_urls, *credentials_urls
]
