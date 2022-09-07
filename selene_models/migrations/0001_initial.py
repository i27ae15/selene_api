# Generated by Django 4.0.6 on 2022-09-07 02:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SeleneModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('model', models.FileField(upload_to='models')),
                ('name', models.CharField(max_length=255)),
                ('updated_at', models.DateTimeField()),
                ('data_trained_with', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='SeleneNode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('head_id', models.IntegerField(default=None, null=True)),
                ('parent_id', models.IntegerField(default=None, null=True)),
                ('next_id', models.IntegerField(default=None, null=True)),
                ('block_step', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField()),
                ('do_after', models.JSONField()),
                ('do_before', models.JSONField()),
                ('name', models.CharField(max_length=255)),
                ('updated_at', models.DateTimeField()),
                ('random_response', models.BooleanField(default=True)),
                ('responses_raw_text', models.TextField()),
                ('patterns_raw_text', models.TextField()),
                ('model', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='selene_models.selenemodel')),
            ],
        ),
        migrations.CreateModel(
            name='SeleneBot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField()),
                ('token', models.CharField(max_length=255)),
                ('updated_at', models.DateTimeField()),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='selene_models.selenemodel')),
            ],
        ),
    ]
