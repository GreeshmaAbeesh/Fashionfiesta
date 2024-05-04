# Generated by Django 4.2.6 on 2024-05-02 16:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_wallet'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReturnRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('return_reason', models.CharField(choices=[('Damage', 'Item is damaged'), ('Wrong Size', 'Wrong size ordered'), ('Wrong Item', 'Wrong item received'), ('Other', 'Other reason')], max_length=100)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='return_requests', to='orders.order')),
            ],
        ),
    ]