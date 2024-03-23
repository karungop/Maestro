from django.urls import path
from .views import read_article

urlpatterns = [
    # The '<int:article_id>' part captures an integer from the URL and passes it as an argument to the view
    path('read_article/<int:article_id>/', read_article, name='read_article'),
]
