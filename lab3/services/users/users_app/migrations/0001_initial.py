from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.TextField(verbose_name="ФИО")),
                ("address", models.TextField(verbose_name="Адрес")),
                ("phone_number", models.TextField(verbose_name="Номер телефона")),
                ("email", models.TextField(verbose_name="Электронная почта")),
                ("picture", models.ImageField(blank=True, null=True, upload_to="customers", verbose_name="Изображение")),
                ("user", models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name="Пользователь")),
            ],
            options={"verbose_name": "Клиент", "verbose_name_plural": "Клиенты"},
        ),
    ]
