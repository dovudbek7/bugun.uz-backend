import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def generate_referral_codes(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    for user in User.objects.filter(referral_code=""):
        user.referral_code = uuid.uuid4().hex[:10]
        user.save(update_fields=["referral_code"])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_user_location"),
    ]

    operations = [
        # Add referral_code without unique first (blank default for existing rows)
        migrations.AddField(
            model_name="user",
            name="referral_code",
            field=models.CharField(max_length=10, default="", blank=True),
            preserve_default=False,
        ),
        # Add other fields
        migrations.AddField(
            model_name="user",
            name="referred_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="referrals",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="referral_count",
            field=models.PositiveIntegerField(default=0),
        ),
        # Populate unique codes for all existing rows
        migrations.RunPython(generate_referral_codes, migrations.RunPython.noop),
        # Now apply unique constraint
        migrations.AlterField(
            model_name="user",
            name="referral_code",
            field=models.CharField(max_length=10, unique=True, default=""),
        ),
    ]
