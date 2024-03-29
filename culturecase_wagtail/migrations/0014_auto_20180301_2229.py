# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-03-01 22:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('culturecase_wagtail', '0013_auto_20180301_1835'),
    ]

    operations = [
        migrations.CreateModel(
            name='FAQsPage',
            fields=[
                ('richpage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='culturecase_wagtail.RichPage')),
            ],
            options={
                'abstract': False,
            },
            bases=('culturecase_wagtail.richpage',),
        ),
        migrations.CreateModel(
            name='QuestionAndAnswer',
            fields=[
                ('richpage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='culturecase_wagtail.RichPage')),
            ],
            options={
                'abstract': False,
            },
            bases=('culturecase_wagtail.richpage',),
        ),
        migrations.AlterModelOptions(
            name='researchsummary',
            options={'ordering': ['-go_live_at']},
        ),
        migrations.AlterField(
            model_name='researchsummary',
            name='categories',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, related_name='research_summaries', to='culturecase_wagtail.ResearchCategory'),
        ),
    ]
