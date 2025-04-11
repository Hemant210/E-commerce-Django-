# Generated by Django 5.2 on 2025-04-10 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_wishlist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='product',
            name='main_category',
            field=models.CharField(choices=[('DA', 'Dairy'), ('EL', 'Electronics'), ('GR', 'Groceries'), ('WF', "Women's Fashion"), ('MF', "Men's Fashion"), ('FT', 'Footwear'), ('BK', 'Books')], default='DA', max_length=3),
        ),
        migrations.AddField(
            model_name='product',
            name='sub_category',
            field=models.CharField(choices=[('ML', 'Milk'), ('LS', 'Lassi'), ('GH', 'Ghee'), ('CR', 'Curd'), ('PN', 'Paneer'), ('CZ', 'Cheese'), ('IC', 'Ice-cream'), ('MS', 'Milkshake'), ('MB', 'Mobile'), ('TV', 'TV'), ('LP', 'Laptop'), ('FR', 'Fruits'), ('VG', 'Vegetables'), ('GRI', 'Grains'), ('SP', 'Spices'), ('WTP', 'Tops'), ('WSR', 'Sarees'), ('WDR', 'Dresses'), ('WJE', 'Jeans'), ('WST', 'Skirts'), ('MSH', 'Shirts'), ('MTS', 'T-Shirts'), ('MJE', 'Jeans'), ('MTR', 'Trousers'), ('MSL', "Men's Slippers"), ('MSH', "Men's Shoes"), ('WSH', "Women's Heels"), ('WSN', "Women's Sneakers"), ('FIC', 'Fiction'), ('NFC', 'Non-fiction'), ('EDU', 'Educational'), ('COM', 'Comics'), ('BIO', 'Biographies')], default='ML', max_length=3),
        ),
        migrations.AlterField(
            model_name='product',
            name='composition',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='product',
            name='prodapp',
            field=models.TextField(blank=True, default=''),
        ),
    ]
