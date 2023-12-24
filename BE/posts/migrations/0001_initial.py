# Generated by Django 4.0.3 on 2023-12-24 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('category', models.CharField(choices=[('notice', '공지사항'), ('qna', '질의/응답'), ('creation-novel', '창작소설'), ('creation-poem', '창작시'), ('creation-essay', '창작수필'), ('comm-novel', '소설'), ('comm-poem', '시'), ('comm-essay', '수필')], max_length=14)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('view_count', models.IntegerField(default=0)),
                ('is_pinned', models.BooleanField(default=False)),
            ],
        ),
    ]
