import csv
from django.core.management.base import BaseCommand
from catalog.models import Product

class Command(BaseCommand):
    help = 'Imports products from a CIF file into the Product model'

    def add_arguments(self, parser):
        parser.add_argument('cif_file', type=str, help='Path to the CIF file')

    def handle(self, *args, **options):
        cif_file = options['cif_file']
        with open(cif_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            data_section = False
            for line in lines:
                line = line.strip()
                if line == 'DATA':
                    data_section = True
                    continue
                if line == 'ENDOFDATA':
                    break
                if data_section and line:
                    row = next(csv.reader([line], delimiter=','))
                    supplier_id, supplier_part_id, manufacturer_part_id, item_description, spsc_code, unit_price, unit_of_measure, lead_time, manufacturer_name, supplier_url, manufacturer_url, market_price, punchout_enabled = row
                    Product.objects.update_or_create(
                        item_code=supplier_part_id,
                        defaults={
                            'main_category': 'Punchout Products',
                            'product_title': item_description,
                            'product_description': item_description,
                            'price': float(unit_price) if unit_price else 0.0,
                            'image_url': supplier_url if supplier_url else None,
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f'Imported product: {item_description}'))