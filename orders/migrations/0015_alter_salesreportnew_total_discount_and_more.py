# Generated by Django 4.2.6 on 2024-05-05 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0014_alter_salesreportnew_total_discount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesreportnew',
            name='total_discount',
            field=models.DecimalField(decimal_places=10, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='salesreportnew',
            name='total_sales_amount',
            field=models.DecimalField(decimal_places=10, default=0, max_digits=10),
        ),
    ]