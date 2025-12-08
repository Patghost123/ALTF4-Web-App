from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0004_reservation_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='purpose',
            field=models.TextField(default='General Lab Usage', help_text='Reason for booking (e.g., Thesis Research, Class Project)'),
            preserve_default=False,
        ),
    ]