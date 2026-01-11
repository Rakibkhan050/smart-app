"""
Management command to create sample businesses for Multi-Business SaaS platform
"""
from django.core.management.base import BaseCommand
from tenants.models import Tenant


class Command(BaseCommand):
    help = 'Create sample businesses for multi-business storefront'

    def handle(self, *args, **kwargs):
        businesses = [
            {
                'name': 'Fresh Mart Grocery',
                'slug': 'fresh-mart-grocery',
                'category': 'grocery',
                'owner_name': 'Sarah Johnson',
                'owner_email': 'sarah@freshmart.com',
                'owner_phone': '+1234567891',
                'business_address': '456 Oak Street, Downtown',
                'description': 'Organic produce and fresh groceries delivered daily',
                'commission_rate': 10,
                'is_active': True,
                'is_approved': True
            },
            {
                'name': 'Pizza Palace',
                'slug': 'pizza-palace',
                'category': 'restaurant',
                'owner_name': 'Mike Romano',
                'owner_email': 'mike@pizzapalace.com',
                'owner_phone': '+1234567892',
                'business_address': '789 Food Street, City Center',
                'description': 'Authentic Italian pizza and pasta since 1985',
                'commission_rate': 12,
                'is_active': True,
                'is_approved': True
            },
            {
                'name': 'HealthCare Pharmacy',
                'slug': 'healthcare-pharmacy',
                'category': 'pharmacy',
                'owner_name': 'Dr. Emily Chen',
                'owner_email': 'emily@healthcarepharmacy.com',
                'owner_phone': '+1234567893',
                'business_address': '321 Medical Plaza, North District',
                'description': '24/7 pharmacy with home delivery and prescription services',
                'commission_rate': 8,
                'is_active': True,
                'is_approved': True
            },
            {
                'name': 'Urban Fashion Hub',
                'slug': 'urban-fashion-hub',
                'category': 'fashion',
                'owner_name': 'Alex Martinez',
                'owner_email': 'alex@urbanfashion.com',
                'owner_phone': '+1234567894',
                'business_address': '555 Fashion Avenue, Shopping District',
                'description': 'Trendy clothing and accessories for all ages',
                'commission_rate': 15,
                'is_active': True,
                'is_approved': True
            },
            {
                'name': 'TechZone Electronics',
                'slug': 'techzone-electronics',
                'category': 'electronics',
                'owner_name': 'David Kim',
                'owner_email': 'david@techzone.com',
                'owner_phone': '+1234567895',
                'business_address': '888 Tech Boulevard, Innovation Park',
                'description': 'Latest gadgets, smartphones, and computer accessories',
                'commission_rate': 12,
                'is_active': True,
                'is_approved': True
            },
            {
                'name': 'Sushi Express',
                'slug': 'sushi-express',
                'category': 'restaurant',
                'owner_name': 'Yuki Tanaka',
                'owner_email': 'yuki@sushiexpress.com',
                'owner_phone': '+1234567896',
                'business_address': '222 Asian Street, East Side',
                'description': 'Fresh sushi and Japanese cuisine delivered fast',
                'commission_rate': 12,
                'is_active': True,
                'is_approved': True
            },
            {
                'name': 'QuickMeds Pharmacy',
                'slug': 'quickmeds-pharmacy',
                'category': 'pharmacy',
                'owner_name': 'Dr. Robert Lee',
                'owner_email': 'robert@quickmeds.com',
                'owner_phone': '+1234567897',
                'business_address': '999 Health Drive, West Side',
                'description': 'Quick prescription refills and over-the-counter medicines',
                'commission_rate': 8,
                'is_active': True,
                'is_approved': False  # Pending approval
            },
        ]

        created = 0
        updated = 0

        for business_data in businesses:
            slug = business_data['slug']
            try:
                tenant, created_flag = Tenant.objects.update_or_create(
                    slug=slug,
                    defaults=business_data
                )
                if created_flag:
                    created += 1
                    self.stdout.write(self.style.SUCCESS(f'✓ Created: {tenant.name} ({tenant.category})'))
                else:
                    updated += 1
                    self.stdout.write(self.style.WARNING(f'↻ Updated: {tenant.name} ({tenant.category})'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error creating {business_data["name"]}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Done! Created {created} new businesses, updated {updated} existing ones.'))
        self.stdout.write(self.style.SUCCESS(f'Total approved businesses: {Tenant.objects.filter(is_approved=True).count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total pending businesses: {Tenant.objects.filter(is_approved=False).count()}'))
