# Generated by Django 5.0.2 on 2024-02-17 21:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('TeacherWorm', '0002_remove_article_difficulty_level_easy_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='original_text_id',
        ),
    ]