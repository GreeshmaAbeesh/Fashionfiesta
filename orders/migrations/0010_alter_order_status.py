# Generated by Django 4.2.6 on 2024-05-04 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_salesreport'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Cash_on_delivery', 'Cash_on_delivery'), ('Accepted', 'Accepted'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled'), ('Returned', 'Returned'), ('Not_Completed', 'Not_Completed')], default='New', max_length=50),
        ),
    ]