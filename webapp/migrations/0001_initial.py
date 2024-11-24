
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Custom_user',
            fields=[
                ('key', models.AutoField(primary_key=True, serialize=False)),
                ('id', models.CharField(max_length=10, unique=True)),
                ('pw', models.CharField(max_length=20)),
                ('user_email', models.EmailField(max_length=128)),
                ('pw_qust', models.IntegerField(default=0)),
                ('pw_ans', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=10)),
                ('join_date', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='School_Event',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField()),
                ('memo', models.TextField(blank=True, null=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.custom_user')),
            ],
        ),
    ]
