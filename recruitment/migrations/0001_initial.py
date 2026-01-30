from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('phone', models.CharField(max_length=20)),
                ('area', models.CharField(max_length=120)),
                ('role', models.CharField(max_length=120)),
                ('availability', models.CharField(choices=[('MORNING', 'Morning'), ('EVENING', 'Evening')], max_length=20)),
                ('status', models.CharField(choices=[('NEW', '🟢 New'), ('INTERVIEW_SCHEDULED', '🟡 Interview Scheduled'), ('CONFIRMED', '🟡 Confirmed'), ('INTERVIEW_DONE', '🟡 Interview Done'), ('SELECTED', '🟢 Selected'), ('REJECTED', '🔴 Rejected'), ('HOLD', '🟡 Hold'), ('DOCUMENT_PENDING', '🟡 Document Pending'), ('DOCUMENT_COMPLETED', '🟢 Document Completed'), ('JOINED', '🟢 Joined'), ('DROPPED', '🔴 Dropped')], default='NEW', max_length=40)),
                ('interview_date', models.DateField(blank=True, null=True)),
                ('interview_time', models.TimeField(blank=True, null=True)),
                ('interview_done_at', models.DateTimeField(blank=True, null=True)),
                ('aadhaar_status', models.CharField(choices=[('PENDING', 'Pending'), ('RECEIVED', 'Received')], default='PENDING', max_length=20)),
                ('bank_status', models.CharField(choices=[('PENDING', 'Pending'), ('RECEIVED', 'Received')], default='PENDING', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='WhatsAppMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='whatsapp_messages', to='recruitment.candidate')),
            ],
        ),
    ]
