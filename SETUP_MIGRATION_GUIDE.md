# Setup & Migration Guide - Smart Multi-Tenant SaaS Platform

## ✅ WHAT HAS BEEN COMPLETED

### New Models Created:
1. ✅ **Tenants App** - Enhanced with branding, privacy policies, operating hours, bank accounts
2. ✅ **Users App** - CustomUser, CustomerProfile, BusinessOwnerProfile, LoginHistory, NotificationPreferences
3. ✅ **Drivers App** - DriverProfile (with verification), DriverDocument, DriverAssignment (enhanced), DriverEarnings
4. ✅ **Incidents App** - Incident, IncidentComment, IncidentFeedback, IncidentReport, IncidentCategory

### Admin Interfaces Created:
1. ✅ **Tenants Admin** - Master admin can view/manage all businesses with global search
2. ✅ **Users Admin** - Global user management with registration ID search
3. ✅ **Drivers Admin** - Driver verification workflow with document management
4. ✅ **Incidents Admin** - Incident tracking with resolution workflow
5. ✅ **Custom User Admin** - Extended Django user with tenant support

### Features Implemented:
- ✅ **Global Search** - By Registration ID or Mobile Number
- ✅ **Master Visibility** - Platform admin sees all data
- ✅ **Business Owner Control** - Approve drivers, manage staff
- ✅ **Multi-Tenant Isolation** - Proper queryset filtering
- ✅ **Verification Workflows** - Driver document approval
- ✅ **Incident Management** - Full resolution tracking
- ✅ **Performance Metrics** - Analytics & reporting

---

## 🚀 SETUP STEPS

### Step 1: Update Django Settings

Edit `backend/school_saas/settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # REST Framework
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    
    # Local Apps
    'tenants',
    'users',          # ← UPDATED
    'drivers',        # ← UPDATED
    'incidents',      # ← NEW
    'crm',
    'delivery',
    'inventory',
    'pos',
    'payments',
    'notifications',
    'finance',
    'accounts',
    'students',
    'receipts',
    'school_saas',
]

# ← ADD THIS
AUTH_USER_MODEL = 'users.CustomUser'

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
}
```

### Step 2: Create Migrations

```bash
cd backend

# Create migration files for updated models
python manage.py makemigrations tenants users drivers incidents

# Check migrations
python manage.py showmigrations
```

### Step 3: Backup Existing Data (IMPORTANT!)

```bash
# Dump current database (if data exists)
python manage.py dumpdata > backup_before_models.json
```

### Step 4: Apply Migrations

```bash
# Apply all migrations
python manage.py migrate

# Verify migration status
python manage.py showmigrations
```

### Step 5: Create Master Admin User

```bash
python manage.py createsuperuser

# When prompted:
# - Username: admin (or your choice)
# - Email: admin@example.com
# - Password: (secure password)
# - Password (again): (confirm)

# After creation, set user_type to master_admin:
python manage.py shell

>>> from users.models import CustomUser
>>> admin = CustomUser.objects.get(username='admin')
>>> admin.user_type = 'master_admin'
>>> admin.save()
>>> exit()
```

### Step 6: Create Test Tenant (Optional)

```bash
python manage.py shell

>>> from tenants.models import Tenant
>>> from users.models import CustomUser
>>> 
>>> # Create a tenant
>>> tenant = Tenant.objects.create(
...     name='Sample Agriculture Store',
...     category='agriculture',
...     owner_name='John Farmer',
...     owner_email='john@agrifarm.com',
...     owner_phone='+1234567890',
...     is_active=True,
...     is_approved=True
... )
>>> tenant.save()
>>> print(f"Tenant created: {tenant.name} ({tenant.registration_id})")
>>> exit()
```

---

## 🔧 VERIFY INSTALLATION

### Test 1: Check Models

```bash
python manage.py shell

>>> from django.apps import apps
>>> models = apps.get_models()
>>> for model in models:
...     print(f"{model.__module__}.{model.__name__}")

# Should see models like:
# users.CustomUser
# users.CustomerProfile
# users.BusinessOwnerProfile
# drivers.DriverProfile
# drivers.DriverDocument
# incidents.Incident
# ... and many more
```

### Test 2: Check Admin Registration

```bash
python manage.py shell

>>> from django.contrib import admin
>>> from tenants.models import Tenant
>>> from users.models import CustomUser
>>> from drivers.models import DriverProfile
>>> from incidents.models import Incident
>>> 
>>> # Check if registered
>>> print(Tenant in admin.site._registry)  # Should be True
>>> print(CustomUser in admin.site._registry)  # Should be True
>>> print(DriverProfile in admin.site._registry)  # Should be True
>>> print(Incident in admin.site._registry)  # Should be True
```

### Test 3: Access Django Admin

```bash
python manage.py runserver

# Open browser: http://localhost:8000/admin
# Login with master admin credentials
# You should see:
# - Tenants
# - Users (CustomUser)
# - Drivers
# - Incidents
# - Customer Profiles
# - Business Owner Profiles
# - And more...
```

---

## ⚠️ IMPORTANT NOTES

### 1. **CustomUser Migration**
If existing users were created with default Django User model:
```bash
# Create a data migration to handle existing users
python manage.py makemigrations --empty users --name migrate_auth_user
```

### 2. **MultiTenant Support**
Each object belongs to a Tenant (business). Set `tenant_id` when creating:
```python
from tenants.models import Tenant
from users.models import CustomerProfile

tenant = Tenant.objects.first()
profile = CustomerProfile.objects.create(
    user=user,
    tenant=tenant,
    ...
)
```

### 3. **UUID Primary Keys**
Some models use UUID instead of auto-increment IDs:
- Tenant
- CustomUser
- DriverProfile
- Incident
- DriverDocument
- DriverAssignment
- DriverEarnings

This is intentional for security and multi-database support.

### 4. **Global Search Fields**
Always use these indexed fields for searching:
- **Customers:** `registration_id`, `phone_number`
- **Drivers:** `registration_id`, `phone`
- **Businesses:** `registration_id`, `owner_phone`, `business_phone`

---

## 📊 DATABASE SCHEMA OVERVIEW

### New Tables (17 total):
```
tenants_tenant
tenants_tenantoperatinghours
tenants_tenantbankaccount
users_customuser
users_customerprofile
users_businessownerprofile
users_userloginhistory
users_usernotificationpreferences
drivers_driverprofile
drivers_driverdocument
drivers_driverassignment
drivers_driverearnings
incidents_incidentcategory
incidents_incident
incidents_incidentcomment
incidents_incidentfeedback
incidents_incidentreport
```

### Key Relationships:
```
Tenant (1) ──── (N) CustomUser
Tenant (1) ──── (N) DriverProfile
Tenant (1) ──── (N) Incident
CustomUser (1) ──── (1) CustomerProfile
CustomUser (1) ──── (1) BusinessOwnerProfile
DriverProfile (1) ──── (N) DriverDocument
DriverProfile (1) ──── (N) DriverAssignment
Incident (1) ──── (N) IncidentComment
```

---

## 🎯 NEXT STEPS

### 1. Create REST API Endpoints
Follow `API_STRUCTURE_GUIDE.md` for serializers and views

### 2. Setup Frontend
- Install & configure Next.js PWA
- Add service worker
- Create pages for each feature

### 3. Mobile App Development
- Android/iOS apps using API endpoints
- Real-time location tracking
- Push notifications

### 4. Testing
- Unit tests for models
- Integration tests for API
- E2E tests for workflows

### 5. Deployment
- Configure Docker compose
- Setup production database
- Configure CDN for media

---

## 🐛 TROUBLESHOOTING

### Migration Conflicts
```bash
# If migrations conflict, remove and recreate:
rm backend/*/migrations/00*.py
python manage.py makemigrations
python manage.py migrate --fake-initial
```

### CustomUser Error
If error "AUTH_USER_MODEL refers to model that has not been installed":
```python
# Ensure in settings.py:
AUTH_USER_MODEL = 'users.CustomUser'
```

### Admin Not Showing Models
```bash
# Rebuild admin:
python manage.py shell
>>> from django.contrib import admin
>>> admin.site.site_header = "My Admin"
>>> exit()
```

### Permission Errors
```bash
# Reset permissions:
python manage.py migrate auth --fake-initial
python manage.py migrate --run-syncdb
```

---

## 📋 CHECKLIST

- [ ] Updated Django settings with new INSTALLED_APPS
- [ ] Set AUTH_USER_MODEL = 'users.CustomUser'
- [ ] Backed up existing database
- [ ] Created and applied migrations
- [ ] Created master admin user
- [ ] Set admin user_type to 'master_admin'
- [ ] Verified admin interface loads
- [ ] Tested global search in admin
- [ ] Created test business (tenant)
- [ ] Confirmed all models visible in admin
- [ ] Tested filtering & search in admin
- [ ] Reviewed documentation files

---

## 📁 FILES MODIFIED/CREATED

### Modified:
- `backend/tenants/models.py` - Enhanced with full features
- `backend/tenants/admin.py` - Complete admin interface
- `backend/users/models.py` - CustomUser with profiles
- `backend/users/admin.py` - User management admin
- `backend/drivers/models.py` - Driver verification system
- `backend/drivers/admin.py` - Driver admin interface

### Created:
- `backend/incidents/models.py` - Incident system (new app)
- `backend/incidents/admin.py` - Incident admin
- `backend/incidents/__init__.py` - App config
- `backend/incidents/apps.py` - Django app config
- `COMPLETE_MODELS_DOCUMENTATION.md` - Full documentation
- `API_STRUCTURE_GUIDE.md` - API endpoints guide
- `SETUP_MIGRATION_GUIDE.md` - This file

---

## 🎉 SUCCESS INDICATORS

You'll know setup is successful when:
1. ✅ `python manage.py migrate` completes without errors
2. ✅ Admin panel loads at `http://localhost:8000/admin`
3. ✅ Can search for drivers by registration ID/phone
4. ✅ Can view all businesses with global filters
5. ✅ Can approve/reject drivers in admin
6. ✅ Can manage incidents with resolution workflow
7. ✅ Can view login history and user preferences
8. ✅ Business owners only see their data
9. ✅ Master admin sees all data

---

**Status:** ✅ Complete & Ready for Setup!

Run the setup steps above to activate the system.
