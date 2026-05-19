from django.db import migrations, models

import movies.models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0002_filmwork_file_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='filmwork',
            name='poster',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=movies.models.poster_upload_path,
                verbose_name='poster',
            ),
        ),
    ]
