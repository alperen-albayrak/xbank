# Generated by Django 4.2.4 on 2023-09-04 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0005_alter_transaction_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.IntegerField(),
        ),
    ]
