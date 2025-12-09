# Generated manually to handle through model creation safely
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('labs', '0012_alter_equipment_id_alter_lab_id'),
        ('reservations', '0012_alter_reservation_id'),
    ]

    operations = [
        # 1. Create the new intermediate model
        migrations.CreateModel(
            name='ReservationEquipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='labs.equipment')),
                ('reservation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservations.reservation')),
            ],
            options={
                'unique_together': {('reservation', 'equipment')},
            },
        ),
        # 2. Remove the old M2M field
        migrations.RemoveField(
            model_name='reservation',
            name='equipment',
        ),
        # 3. Add the new M2M field pointing to the through model
        migrations.AddField(
            model_name='reservation',
            name='equipment',
            field=models.ManyToManyField(blank=True, related_name='reservations', through='reservations.ReservationEquipment', to='labs.equipment'),
        ),
    ]