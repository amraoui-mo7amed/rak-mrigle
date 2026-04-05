from django.core.management.base import BaseCommand
from django.db import transaction
from dashboard.models import Category


CATEGORIES_DATA = {
    "transport": {
        "icon": "fa-truck",
        "categories": [
            ("شاحنات صغيرة", "Petits camions", "Small trucks"),
            ("شاحنات متوسطة", "Camions moyens", "Medium trucks"),
            ("شاحنات كبيرة", "Grands camions", "Large trucks"),
            ("شاحنات ثقيلة", "Camions lourds", "Heavy trucks"),
            ("شاحنات مقطورة", "Camions remorqués", "Trailer trucks"),
            ("شاحنات برادية", "Camions frigorifiques", "Refrigerated trucks"),
            ("شاحنات صهاريج", "Camions citernes", "Tanker trucks"),
            ("شاحنات نقل السيارات", "Transporteurs de voitures", "Car carriers"),
            ("شاحنات قلابة", "Camions bennes", "Tipper trucks"),
            ("شاحنات نقل أثاث", "Camions de déménagement", "Moving trucks"),
            ("شاحنات توزيع", "Camions de distribution", "Delivery trucks"),
            ("شاحنات 3.5 طن", "Camions 3.5 tonnes", "3.5 ton trucks"),
            ("شاحنات 7.5 طن", "Camions 7.5 tonnes", "7.5 ton trucks"),
            ("شاحنات 12 طن", "Camions 12 tonnes", "12 ton trucks"),
            ("شاحنات 19 طن", "Camions 19 tonnes", "19 ton trucks"),
            ("شاحنات 26 طن", "Camions 26 tonnes", "26 ton trucks"),
            ("شاحنات نفطية", "Camions pétroliers", "Fuel trucks"),
            ("شاحنات مياه", "Camions d'eau", "Water trucks"),
            ("شاحنات قمامة", "Camions poubelles", "Garbage trucks"),
            ("شاحنات إسعاف", "Ambulances", "Ambulances"),
            ("حافلات صغيرة", "Petits bus", "Small buses"),
            ("حافلات متوسطة", "Bus moyens", "Medium buses"),
            ("حاحلات كبيرة", "Grands bus", "Large buses"),
            ("حافلات سياحية", "Bus touristiques", "Tourist buses"),
            ("حافلات مدرسية", "Bus scolaires", "School buses"),
            ("حافلات رحلات", "Bus excursions", "Excursion buses"),
            ("حافلات عمال", "Bus travailleurs", "Worker buses"),
            ("حافلات نقل موظفين", "Bus employés", "Employee transport"),
            ("فانات نقل", "Vans de transport", "Transport vans"),
            ("ميني فان", "Mini van", "Mini van"),
            ("فانات تجارية", "Vans commerciaux", "Commercial vans"),
            ("سيارات أجرة", "Taxis", "Taxis"),
            ("سيارات أجرة كبيرة", "Grands taxis", "Large taxis"),
            ("نقل مدرسي", "Transport scolaire", "School transport"),
            ("نقل عمال", "Transport de travailleurs", "Worker transport"),
            ("نقل حجاج", "Transport de pèlerins", "Pilgrim transport"),
            ("نقل سياحي", "Transport touristique", "Tourist transport"),
            ("نقل قطاع خاص", "Transport privé", "Private transport"),
            ("نقل قطاع عام", "Transport public", "Public transport"),
            ("شاحنات متنوعة", "Camions divers", "Miscellaneous trucks"),
        ],
    },
    "machinery": {
        "icon": "fa-truck-loading",
        "categories": [
            ("حفارات صغيرة", "Mini pelles", "Mini excavators"),
            ("حفارات متوسطة", "Pelles moyennes", "Medium excavators"),
            ("حفارات كبيرة", "Grandes pelles", "Large excavators"),
            ("حفارات هيدروليكية", "Pelles hydrauliques", "Hydraulic excavators"),
            ("حفارات بعجلات", "Pelles sur pneus", "Wheel excavators"),
            ("حفارات زحافة", "Pelles sur chenilles", "Track excavators"),
            ("لودر", "Chargeur", "Loader"),
            ("لودر بعجل", "Chargeur sur pneus", "Wheel loader"),
            ("لودر زحافة", "Chargeur sur chenilles", "Track loader"),
            ("لودر خلفي", "Chargeur rétropelle", "Backhoe loader"),
            ("رافعات برجية", "Grues à tour", "Tower cranes"),
            ("رافعات متنقلة", "Grues mobiles", "Mobile cranes"),
            ("رافعات شاحنة", "Grues sur camion", "Truck cranes"),
            ("رافعات علوية", "Grues aériennes", "Overhead cranes"),
            ("رافعات تفريغ", "Grues de déchargement", "Unloading cranes"),
            ("رافعات بناء", "Grues de construction", "Construction cranes"),
            ("رافعات ميناء", "Grues portuaires", "Port cranes"),
            ("رافعات صغيرة", "Petites grues", "Small cranes"),
            ("رافعات ثقيلة", "Grues lourdes", "Heavy cranes"),
            ("بلدوزر", "Bulldozer", "Bulldozer"),
            ("بلدوزر زحافة", "Bulldozer sur chenilles", "Track bulldozer"),
            ("بلدوزر بعجل", "Bulldozer sur pneus", "Wheel bulldozer"),
            ("دحاجات", "Compacteurs", "Compactors"),
            ("دحاجة طرق", "Compacteur de routes", "Road roller"),
            ("دحاجة تربة", "Compacteur de sol", "Soil compactor"),
            ("دحاجة أسفلت", "Compacteur d'asphalte", "Asphalt compactor"),
            ("خلاطات خرسانة", "Bétonnières", "Concrete mixers"),
            ("خلاطات أسفلت", "Malaxeurs d'asphalte", "Asphalt mixers"),
            ("رصف طرق", "Finisseur", "Paver"),
            ("فرش أسفلت", "Finisseur d'asphalte", "Asphalt paver"),
            ("جرارات", "Tracteurs", "Tractors"),
            ("جرارات زراعية", "Tracteurs agricoles", "Agricultural tractors"),
            ("جرارات بناء", "Tracteurs de construction", "Construction tractors"),
            ("مقالع", "Carrières", "Quarries"),
            ("كسارات", "Concasseurs", "Crushers"),
            ("غربلة", "Cribleurs", "Screeners"),
            ("مناشر حجر", "Scies de pierre", "Stone saws"),
            ("مضخات خرسانة", "Pompes à béton", "Concrete pumps"),
            ("أوناش رافعة", "Grues télescopiques", "Telescopic cranes"),
            ("معدات متنوعة", "Équipements divers", "Miscellaneous machinery"),
        ],
    },
    "logistics": {
        "icon": "fa-warehouse",
        "categories": [
            ("تخزين بضائع", "Stockage de marchandises", "Goods storage"),
            ("مستودعات مبردة", "Entrepôts frigorifiques", "Cold storage"),
            ("مستودعات عامة", "Entrepôts généraux", "General warehouses"),
            ("مستودعات مؤتمتة", "Entrepôts automatisés", "Automated warehouses"),
            ("مستودعات مفتوحة", "Entrepôts ouverts", "Open warehouses"),
            ("مستودعات مغلقة", "Entrepôts fermés", "Closed warehouses"),
            ("شحن بحري", "Fret maritime", "Sea freight"),
            ("شحن جوي", "Fret aérien", "Air freight"),
            ("شحن بري", "Fret routier", "Land freight"),
            ("شحن سككي", "Fret ferroviaire", "Rail freight"),
            ("شحن دولي", "Fret international", "International freight"),
            ("شحن محلي", "Fret local", "Local freight"),
            ("تخليص جمركي", "Dédouanement", "Customs clearance"),
            ("استيراد", "Importation", "Import"),
            ("تصدير", "Exportation", "Export"),
            ("ترانزيت", "Transit", "Transit"),
            ("توزيع محلي", "Distribution locale", "Local distribution"),
            ("توزيع جهوي", "Distribution régionale", "Regional distribution"),
            ("توزيع وطني", "Distribution nationale", "National distribution"),
            ("توزيع دولي", "Distribution internationale", "International distribution"),
            ("مناولة", "Manutention", "Handling"),
            ("تغليف", "Emballage", "Packaging"),
            ("تفريغ", "Déchargement", "Unloading"),
            ("تحميل", "Chargement", "Loading"),
            ("تخزين مؤقت", "Stockage temporaire", "Temporary storage"),
            ("خدمات لوجستية", "Services logistiques", "Logistics services"),
            ("سلسلة توريد", "Chaîne d'approvisionnement", "Supply chain"),
            ("إدارة مخزون", "Gestion des stocks", "Inventory management"),
            ("تتبع شحنات", "Suivi des expéditions", "Shipment tracking"),
            ("خدمات متنوعة", "Services divers", "Miscellaneous services"),
        ],
    },
}


class Command(BaseCommand):
    help = "Seeds the database with transport, machinery, and logistics categories"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing categories before seeding",
        )

    def handle(self, *args, **kwargs):
        clear = kwargs.get("clear", False)

        if clear:
            self.stdout.write("Clearing existing categories...")
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING("All categories deleted."))

        total_created = 0
        total_skipped = 0

        with transaction.atomic():
            for category_type, data in CATEGORIES_DATA.items():
                icon = data["icon"]
                categories = data["categories"]

                self.stdout.write(f"\nProcessing {category_type} categories...")

                for name_ar, name_fr, name_en in categories:
                    exists = Category.objects.filter(
                        name_ar=name_ar,
                        category_type=category_type,
                    ).exists()

                    if exists:
                        total_skipped += 1
                        continue

                    Category.objects.create(
                        name_ar=name_ar,
                        name_fr=name_fr,
                        name_en=name_en,
                        category_type=category_type,
                        icon=icon,
                        is_active=True,
                    )
                    total_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSeeding complete!\n"
                f"  Created: {total_created} categories\n"
                f"  Skipped: {total_skipped} categories (already exist)\n"
                f"  Total:   {total_created + total_skipped} categories"
            )
        )
