# Generated by Django 4.2.6 on 2024-03-16 07:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_rename_variations_orderproduct_variation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderproduct',
            old_name='variation',
            new_name='variations',
        ),
    ]
