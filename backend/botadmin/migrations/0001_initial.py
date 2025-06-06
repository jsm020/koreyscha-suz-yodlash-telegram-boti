# Generated by Django 5.2.1 on 2025-05-17 13:28

import botadmin.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('korean', models.TextField()),
                ('uzbek', models.TextField()),
                ('romanized', models.TextField(blank=True, null=True)),
                ('audio_file', models.FileField(blank=True, null=True, upload_to=botadmin.models.audio_upload_path)),
                ('created_at', models.DateField(auto_now_add=True)),
            ],
            options={
                'db_table': 'words',
            },
        ),
        migrations.CreateModel(
            name='RepeatSession',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('repeat_key', models.TextField(unique=True)),
                ('date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('words', models.ManyToManyField(related_name='repeat_sessions', to='botadmin.word')),
            ],
            options={
                'db_table': 'repeat_sessions',
            },
        ),
        migrations.CreateModel(
            name='RepeatResult',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.BigIntegerField()),
                ('is_correct', models.BooleanField(blank=True, null=True)),
                ('attempt_count', models.IntegerField(blank=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('repeat_session', models.ForeignKey(db_column='repeat_key', on_delete=django.db.models.deletion.CASCADE, to='botadmin.repeatsession')),
                ('word', models.ForeignKey(db_column='word_id', on_delete=django.db.models.deletion.CASCADE, to='botadmin.word')),
            ],
            options={
                'db_table': 'repeat_results',
            },
        ),
        migrations.CreateModel(
            name='Attempt',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.BigIntegerField()),
                ('attempt_count', models.IntegerField()),
                ('is_correct', models.BooleanField()),
                ('attempted_at', models.DateTimeField(auto_now_add=True)),
                ('word', models.ForeignKey(db_column='word_id', on_delete=django.db.models.deletion.CASCADE, to='botadmin.word')),
            ],
            options={
                'db_table': 'attempts',
            },
        ),
        migrations.CreateModel(
            name='KnownWord',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.BigIntegerField()),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('word', models.ForeignKey(db_column='word_id', on_delete=django.db.models.deletion.CASCADE, to='botadmin.word')),
            ],
            options={
                'db_table': 'known_words',
                'unique_together': {('user_id', 'word')},
            },
        ),
    ]
