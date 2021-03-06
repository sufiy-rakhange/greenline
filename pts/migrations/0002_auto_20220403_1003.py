# Generated by Django 3.1.7 on 2022-04-03 09:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='risks',
            name='illegal_immigration',
        ),
        migrations.RemoveField(
            model_name='risks',
            name='narcotics',
        ),
        migrations.RemoveField(
            model_name='risks',
            name='revenue',
        ),
        migrations.RemoveField(
            model_name='risks',
            name='smuggling',
        ),
        migrations.RemoveField(
            model_name='risks',
            name='terrorism',
        ),
        migrations.AddField(
            model_name='risks',
            name='name',
            field=models.CharField(default=12, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='airlines',
            name='two_letter_code',
            field=models.CharField(max_length=5),
        ),
        migrations.CreateModel(
            name='PassengerRisk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, max_digits=3)),
                ('p_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='pts.passengers')),
                ('r_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='pts.risks')),
            ],
        ),
        migrations.CreateModel(
            name='PassengerFlight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seat_number', models.CharField(max_length=20)),
                ('f_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='pts.flights')),
                ('p_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='pts.passengers')),
            ],
        ),
    ]
