# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-27 20:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.contrib.taggit
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('culturecase_wagtail', '0008_auto_20180227_0054'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResearchTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('taggit.tag',),
        ),
        migrations.AlterField(
            model_name='articlesummarypage',
            name='article_authors',
            field=models.CharField(blank=True, default=None, help_text='The names of one or more authors separated by commas', max_length=255, null=True, verbose_name='Article authors'),
        ),
        migrations.AlterField(
            model_name='articlesummarypage',
            name='article_email',
            field=models.EmailField(blank=True, default=None, help_text='Contact email address for the lead author', max_length=254, null=True, verbose_name='Author email'),
        ),
        migrations.AlterField(
            model_name='articlesummarypage',
            name='article_oaurl',
            field=models.URLField(blank=True, default=None, help_text='Open access URL (including the http:// part)', null=True, verbose_name='Article open access link'),
        ),
        migrations.AlterField(
            model_name='articlesummarypage',
            name='article_source',
            field=models.CharField(blank=True, default=None, help_text='Source reference', max_length=255, null=True, verbose_name='Article source'),
        ),
        migrations.AlterField(
            model_name='articlesummarypage',
            name='article_title',
            field=models.CharField(blank=True, default=None, help_text='The title of the research paper', max_length=255, null=True, verbose_name='Article title'),
        ),
        migrations.AlterField(
            model_name='articlesummarypage',
            name='article_url',
            field=models.URLField(blank=True, default=None, help_text='Reference URL (including the http:// part)', null=True, verbose_name='Article link'),
        ),
        migrations.AlterField(
            model_name='articlesummarypage',
            name='article_year',
            field=models.IntegerField(blank=True, default=None, help_text='Year of publication', null=True, verbose_name='Article year'),
        ),
        migrations.AddField(
            model_name='researchtag',
            name='content_object',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='research_tags', to='culturecase_wagtail.ArticleSummaryPage'),
        ),
        migrations.AddField(
            model_name='researchtag',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='culturecase_wagtail_researchtag_items', to='taggit.Tag'),
        ),
        migrations.AddField(
            model_name='articlesummarypage',
            name='tags',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='culturecase_wagtail.ResearchTag', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
