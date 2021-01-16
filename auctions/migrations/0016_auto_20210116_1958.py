# Generated by Django 3.1.4 on 2021-01-16 18:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0015_auto_20210114_0924'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='current_bid',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='highest_bidder',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='highest_bid', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='watchlist',
            field=models.ManyToManyField(blank=True, default=None, to='auctions.Listing'),
        ),
    ]
