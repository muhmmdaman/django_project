from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('students', '0004_subject_is_lab'),
    ]
    operations = [
        migrations.CreateModel(
            name='SalaryPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, help_text='Amount paid in INR', max_digits=12)),
                ('payment_date', models.DateField(help_text='Date of payment')),
                ('payment_method', models.CharField(choices=[('bank_transfer', 'Bank Transfer'), ('check', 'Check'), ('cash', 'Cash'), ('other', 'Other')], default='bank_transfer', help_text='Method of payment', max_length=20)),
                ('reference_number', models.CharField(blank=True, help_text='Bank reference, check number, or transaction ID', max_length=100, unique=True)),
                ('notes', models.TextField(blank=True, help_text='Additional notes about this payment')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When this payment record was created')),
            ],
            options={
                'verbose_name': 'Salary Payment',
                'verbose_name_plural': 'Salary Payments',
                'ordering': ['-payment_date'],
            },
        ),
        migrations.AlterModelOptions(
            name='teacher',
            options={'ordering': ['department', 'user__first_name'], 'verbose_name_plural': 'Teachers'},
        ),
        migrations.AddField(
            model_name='teacher',
            name='last_paid_date',
            field=models.DateField(blank=True, help_text='Date of last salary payment', null=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='next_payment_date',
            field=models.DateField(blank=True, help_text='Scheduled next payment date', null=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='payment_notes',
            field=models.TextField(blank=True, help_text='Additional notes about salary/payments'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='salary_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Monthly salary in INR', max_digits=12),
        ),
        migrations.AddField(
            model_name='teacher',
            name='salary_status',
            field=models.CharField(choices=[('paid', 'Paid'), ('due', 'Due')], default='due', help_text='Payment status: paid or due', max_length=10),
        ),
        migrations.AddIndex(
            model_name='teacher',
            index=models.Index(fields=['salary_status'], name='students_te_salary__5a9392_idx'),
        ),
        migrations.AddIndex(
            model_name='teacher',
            index=models.Index(fields=['last_paid_date'], name='students_te_last_pa_3aa03d_idx'),
        ),
        migrations.AddField(
            model_name='salarypayment',
            name='processed_by',
            field=models.ForeignKey(blank=True, help_text='Admin who processed this payment', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='processed_salary_payments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='salarypayment',
            name='teacher',
            field=models.ForeignKey(help_text='Teacher receiving payment', on_delete=django.db.models.deletion.CASCADE, related_name='salary_payments', to='students.teacher'),
        ),
        migrations.AddIndex(
            model_name='salarypayment',
            index=models.Index(fields=['teacher', '-payment_date'], name='students_sa_teacher_d0f3ea_idx'),
        ),
        migrations.AddIndex(
            model_name='salarypayment',
            index=models.Index(fields=['payment_date'], name='students_sa_payment_6f0351_idx'),
        ),
    ]
