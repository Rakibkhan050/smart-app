# API Structure Guide - Next Steps

## Overview
This document outlines the API endpoints and serializers needed for the complete system to support mobile apps (Android/iOS) and web frontend.

---

## 1. AUTHENTICATION & USER ENDPOINTS

### Path: `users/api.py`

#### Endpoints:
```
POST   /api/auth/register/               - Register new user
POST   /api/auth/login/                  - Login user
POST   /api/auth/refresh/                - Refresh JWT token
POST   /api/auth/logout/                 - Logout user
POST   /api/auth/password-reset/         - Request password reset
POST   /api/auth/password-reset/confirm/ - Confirm password reset
GET    /api/profile/                     - Get user profile
PATCH  /api/profile/                     - Update user profile
GET    /api/profile/login-history/       - Get login history
PATCH  /api/notification-preferences/    - Update notification settings
```

#### Serializers Needed:
- `UserRegistrationSerializer`
- `UserLoginSerializer`
- `CustomUserSerializer`
- `CustomerProfileSerializer`
- `BusinessOwnerProfileSerializer`
- `UserLoginHistorySerializer`
- `UserNotificationPreferencesSerializer`

---

## 2. BUSINESS/TENANT ENDPOINTS

### Path: `tenants/api.py`

#### Endpoints:
```
# Public (No auth required)
GET    /api/businesses/                   - List all approved businesses
GET    /api/businesses/{slug}/            - Get business details
GET    /api/businesses/{slug}/products/   - Get business products
GET    /api/businesses/{slug}/reviews/    - Get business reviews

# Business Owner Only
GET    /api/my-business/                  - Get own business details
PATCH  /api/my-business/                  - Update business info
PATCH  /api/my-business/branding/         - Update logo, colors, etc.
PATCH  /api/my-business/policies/         - Update privacy/terms
GET    /api/my-business/analytics/        - Get business analytics
GET    /api/my-business/staff/            - List staff members
GET    /api/my-business/operating-hours/  - Get/set operating hours
GET    /api/my-business/bank-account/     - Get/update bank details
GET    /api/my-business/payouts/          - Get payout history
```

#### Serializers Needed:
- `TenantListSerializer` (public list view)
- `TenantDetailSerializer` (includes policies, branding)
- `TenantOperatingHoursSerializer`
- `TenantBankAccountSerializer`

---

## 3. CUSTOMER ENDPOINTS

### Path: `crm/api.py` (extend)

#### Endpoints:
```
# Customer Only
GET    /api/orders/                       - Get order history
GET    /api/orders/{id}/                  - Get order details
GET    /api/favorite-stores/              - Get favorite businesses
POST   /api/favorite-stores/              - Add favorite
DELETE /api/favorite-stores/{id}/         - Remove favorite
GET    /api/loyalty-points/               - Get loyalty info
POST   /api/write-review/                 - Submit review
GET    /api/my-reviews/                   - Get my reviews
```

#### Serializers Needed:
- `OrderSerializer`
- `OrderDetailSerializer`
- `CustomerProfileSerializer` (already defined)
- `LoyaltyPointsSerializer`
- `ReviewSerializer`

---

## 4. DRIVER ENDPOINTS

### Path: `drivers/api.py`

#### Endpoints:
```
# Driver Only
GET    /api/driver/profile/               - Get driver profile
PATCH  /api/driver/profile/               - Update profile
POST   /api/driver/upload-document/       - Upload ID document
GET    /api/driver/documents/             - Get document status
GET    /api/driver/assignments/           - Get delivery assignments
GET    /api/driver/assignments/{id}/      - Get assignment details
PATCH  /api/driver/assignments/{id}/accept/ - Accept delivery
PATCH  /api/driver/assignments/{id}/start/  - Start delivery
PATCH  /api/driver/assignments/{id}/complete/ - Complete delivery
GET    /api/driver/earnings/              - Get earnings history
GET    /api/driver/location/              - Get current location
POST   /api/driver/location/              - Update location (real-time)
GET    /api/driver/stats/                 - Get performance stats
```

#### Serializers Needed:
- `DriverProfileSerializer`
- `DriverDocumentSerializer`
- `DriverAssignmentSerializer`
- `DriverAssignmentDetailSerializer`
- `DriverEarningsSerializer`
- `DriverLocationSerializer`
- `DriverStatsSerializer`

---

## 5. DELIVERY ENDPOINTS

### Path: `delivery/api.py`

#### Endpoints:
```
# Public
GET    /api/delivery/estimate/            - Estimate delivery fee
GET    /api/delivery/zones/               - Get delivery zones

# Customer
POST   /api/orders/{id}/request-delivery/ - Request delivery
GET    /api/orders/{id}/tracking/         - Real-time delivery tracking
PATCH  /api/orders/{id}/cancel/           - Cancel delivery

# Business Owner
GET    /api/my-business/deliveries/       - Get all deliveries
GET    /api/my-business/drivers/          - Get assigned drivers
POST   /api/my-business/drivers/          - Add driver
PATCH  /api/my-business/drivers/{id}/     - Update driver

# Driver
GET    /api/driver/deliveries/pending/    - Get pending deliveries
GET    /api/driver/deliveries/history/    - Get delivery history
```

#### Serializers Needed:
- `DeliverySerializer`
- `DeliveryDetailSerializer`
- `DeliveryTrackingSerializer`
- `ShippingFeeRuleSerializer`

---

## 6. INCIDENT REPORTING ENDPOINTS

### Path: `incidents/api.py`

#### Endpoints:
```
# Customer
POST   /api/incidents/create/             - Report new incident
GET    /api/incidents/                    - Get my incidents
GET    /api/incidents/{id}/               - Get incident details
PATCH  /api/incidents/{id}/               - Update incident
POST   /api/incidents/{id}/comments/      - Add comment
GET    /api/incidents/{id}/comments/      - Get comments
POST   /api/incidents/{id}/feedback/      - Submit feedback

# Business Owner
GET    /api/my-business/incidents/        - Get all incidents
GET    /api/my-business/incidents/pending/ - Get pending incidents
PATCH  /api/my-business/incidents/{id}/acknowledge/ - Acknowledge
PATCH  /api/my-business/incidents/{id}/resolve/     - Resolve
GET    /api/my-business/incidents/report/ - Get incident report
```

#### Serializers Needed:
- `IncidentCreateSerializer`
- `IncidentListSerializer`
- `IncidentDetailSerializer`
- `IncidentCommentSerializer`
- `IncidentFeedbackSerializer`
- `IncidentReportSerializer`
- `IncidentCategorySerializer`

---

## 7. GLOBAL SEARCH & ADMIN ENDPOINTS

### Path: `core/api.py` (new)

#### Endpoints:
```
# Master Admin Only
GET    /api/admin/search/drivers/         - Search drivers by ID/phone
GET    /api/admin/search/customers/       - Search customers by ID/phone
GET    /api/admin/search/businesses/      - Search businesses by ID
GET    /api/admin/global-analytics/       - Platform-wide analytics
GET    /api/admin/incidents/all/          - All platform incidents
GET    /api/admin/payouts/                - All payout transactions
```

#### Serializers Needed:
- `GlobalSearchResultSerializer`
- `PlatformAnalyticsSerializer`
- `PayoutTransactionSerializer`

---

## 8. STOREFRONT (PWA) ENDPOINTS

### Path: `storefront/api.py` (new)

#### Endpoints:
```
# Public
GET    /{business-slug}/api/products/     - Get products
GET    /{business-slug}/api/products/{id}/ - Get product details
GET    /{business-slug}/api/categories/   - Get categories
GET    /{business-slug}/api/business/     - Get business info
GET    /{business-slug}/api/policies/     - Get policies
POST   /{business-slug}/api/cart/         - Manage cart
POST   /{business-slug}/api/checkout/     - Checkout

# Authenticated
POST   /{business-slug}/api/orders/       - Create order
GET    /api/orders/                       - Get my orders
```

---

## API AUTHENTICATION

### JWT Token Flow:
```python
# LOGIN
POST /api/auth/login/
{
    "username": "user@example.com",
    "password": "password"
}
Response:
{
    "access": "eyJ...",
    "refresh": "eyJ..."
}

# USE IN HEADERS
Authorization: Bearer eyJ...

# REFRESH
POST /api/auth/refresh/
{
    "refresh": "eyJ..."
}
```

---

## ERROR RESPONSES

### Standard Error Format:
```json
{
    "error": "Error message",
    "code": "ERROR_CODE",
    "details": {
        "field": ["error message"]
    }
}
```

### Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not found
- `422` - Unprocessable entity
- `500` - Server error

---

## PAGINATION

### Query Parameters:
```
GET /api/orders/?page=1&page_size=20
```

### Response:
```json
{
    "count": 100,
    "next": "http://api.example.com/orders/?page=2",
    "previous": null,
    "results": [...]
}
```

---

## FILTERING & SEARCH

### Examples:
```
GET /api/incidents/?status=open&priority=high
GET /api/drivers/?status=available&assigned_businesses=tenant-id
GET /api/orders/?created_at__gte=2024-01-01&created_at__lte=2024-12-31
```

---

## REAL-TIME FEATURES (WebSocket)

### For location tracking:
```
ws://api.example.com/ws/driver/{driver-id}/location/
```

### For incident updates:
```
ws://api.example.com/ws/incidents/{incident-id}/updates/
```

---

## IMPLEMENTATION ROADMAP

1. **Phase 1** - Authentication & User APIs
2. **Phase 2** - Business & Tenant APIs
3. **Phase 3** - Customer APIs
4. **Phase 4** - Driver APIs
5. **Phase 5** - Delivery & Tracking APIs
6. **Phase 6** - Incident Reporting APIs
7. **Phase 7** - Admin/Global Search APIs
8. **Phase 8** - Storefront APIs
9. **Phase 9** - WebSocket Real-time Features
10. **Phase 10** - Mobile App Integration

---

## MOBILE APP REQUIREMENTS

### Android/iOS Need:
- ✅ User authentication
- ✅ Profile management
- ✅ Order management (customers)
- ✅ Delivery tracking (drivers)
- ✅ Incident reporting
- ✅ Push notifications
- ✅ Real-time location (drivers)
- ✅ Payment integration
- ✅ Loyalty points
- ✅ Reviews & ratings

### PWA Requirements:
- ✅ Service worker support
- ✅ Offline functionality
- ✅ Install to home screen
- ✅ Responsive design
- ✅ Push notifications

---

**Next:** Create serializers and views in each app's `api.py` and `serializers.py` files following this structure.
