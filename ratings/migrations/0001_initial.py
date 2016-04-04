# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-04-04 16:10
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('identity', models.CharField(max_length=36)),
                ('version', models.IntegerField(default=1)),
                ('invited', models.BooleanField(default=False)),
                ('completed', models.BooleanField(default=False)),
                ('expired', models.BooleanField(default=False)),
                ('invite', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invites_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invites_updated', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('identity', models.CharField(max_length=36)),
                ('version', models.IntegerField(default=1)),
                ('question_id', models.IntegerField()),
                ('question_text', models.CharField(max_length=255)),
                ('answer_text', models.CharField(max_length=255)),
                ('answer_value', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ratings_created', to=settings.AUTH_USER_MODEL)),
                ('invite', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ratings_feedback', to='ratings.Invite')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ratings_updated', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]