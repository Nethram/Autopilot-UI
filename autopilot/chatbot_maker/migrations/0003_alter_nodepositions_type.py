# Generated by Django 3.2.6 on 2021-12-28 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot_maker', '0002_nodepositions_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nodepositions',
            name='type',
            field=models.CharField(default='say-item', max_length=24),
        ),
    ]
