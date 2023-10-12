# Generated by Django 4.2 on 2023-06-15 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('truck_app', '0012_chosenshiftingvehicle_vehicle_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='houseshiftingdetails',
            name='booking_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='orderbooking',
            name='booking_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='vehicleshiftingdetails',
            name='booking_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='warehousestoragedetails',
            name='booking_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]