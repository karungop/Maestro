from django.shortcuts import render
from Study.models.articles import Article

def student_articles(request):
    articles = Article.objects.all()  # Retrieve all student articles
    context = {'articles': articles}
    return render(request, 'Study/student_view.html', context)
