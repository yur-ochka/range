from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='contact_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='order',
            name='contact_name',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='order',
            name='contact_phone',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
