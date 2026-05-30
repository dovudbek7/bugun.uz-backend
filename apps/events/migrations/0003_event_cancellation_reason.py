from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_event_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='cancellation_reason',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
