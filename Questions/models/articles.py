from django.db import models


class Article(models.Model):
    created_on = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=500)
    date_published = models.CharField(max_length=500)
    source = models.CharField(max_length=500)
    original_text = models.TextField()
    DIFFICULTLY_CHOICES = [
        ("EASY", "Easy"),
        ("MEDIUM", "Medium"),
        ("HARD", "Hard"),
        ("ORIGINAL", "Original"),
    ]
    difficulty_level = models.CharField(max_length=50, choices=DIFFICULTLY_CHOICES, null=True)
    new_text = models.TextField(null=True)

