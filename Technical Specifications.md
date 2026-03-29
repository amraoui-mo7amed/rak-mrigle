# Technical Specifications: Rak-Mrigle Marketplace

## 1. Project Identification

- **Project Name:** Rak-Mrigle
- **Client:** Oussama
- **Lead Developer:** Amraoui Mohamed
- **Project Duration:** 6 Weeks (Maximum)
-
## 2. Tech Stack & Environment
- **Backend:** Python / Django (Modern web framework for scalability)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla), Bootstrap 5, HTMX
- **Icons:** FontAwesome 6 (Free)
- **Localization:** Django i18n (Arabic RTL support)
- **Mobile Strategy:** Responsive Web (Mobile-First / PWA potential)

## 3. Core Functional Requirements
### 3.1 User Roles & Authentication
- **Admin:** Full platform oversight, user verification, and transaction monitoring.
- **Customer:** Request-based flow for transport or heavy machinery.
- **Provider:** Profile and fleet management, request handling, and commission settlement.
- **Auth Logic:** **Social Login** or **E-mail Login** with **Manual Account Approval** 
### 3.2 Service Catalog
- **Transport:** Small/Large trucks, Utility vehicles (e.g., Renault Master).
- **Machinery:** Backhoe loaders, Cranes, Lifting equipment, Construction machinery.
- **Logistics:** Car towing (Dépannage), On-demand logistics.

### 3.3 Pricing & Commission Engine
- **Distance Logic:** Price = Distance (km) × Rate/Km
- **Base Fare:** Minimum charge depending on vehicle type
- **Hourly Logic:** Hourly Rate+ Optional Fuel/Operator costs.
- **Extra Costs:** Wait Time/Access difficulties
- **Commission Structure:** 1% (Promotional - Month 1), 10% (Growth - Month 2 onwards).
- **Settlement:** Weekly commission payments (Every Sunday) via CCP or Cash.

### 3.4 Matchmaking & Communication
- **Provider Workflow:**
    - Customized User Profile
    - Create/Delete/Update an offer 
    - Accept/Reject Customer requests
    
- **Customer Workflow:** 
    - Offers Browsing 
    - Request Submission with Price Estimation
    - Provider acceptence with Price offer
    - Customer acceptence/rejection
    - Order Completion.
- **Admin Workflow:**
    - Users Management 
    - Offers/Orders History 
    - General Statistics
    
- **Privacy:** Phone number is locked until mutual confirmation.
## 4. Technical Architecture (Developer Ready)
### 4.1 Database Entities (Django Models)
- **Users:** Extended `AbstractUser` for Role-Based Access Control (RBAC).
- **Providers:** Linked to Users; includes Driving License verification status.
- **Categories:** Hierarchical structure for Transport, Machinery
- **Vehicles:** Linked to Providers; stores category, capacity, and imagery.
- **Orders:** Tracks Pickup/Destination, Status (Pending/Active/Done), and Pricing.
- **Payments:** Ledger for weekly commission debts and provider payouts.
- **Ratings:** 1-5 star system with optional feedback for trust building.
- **Notifications:** Real-time Notifications for tracking users actions.

### 4.2 Localization (i18n)
- **Languages:** 
    - Arabic 
    - French
    - English (🇬🇧)

## 5. UI/UX Guidelines
- **Primary Colors:** 
    - Gold Yellow (#FFD700) for energy/vibrance
    - Dark Blue (#1A2B3C) for trust.
    - Light Grey (#F5F5F5) for borders and backgrounds
- **Style:** 
    - Minimalist
    - High-speed performance
    - Intuitive for non-tech users.

## 6. Legal & Security
- **Liability:** Strict "Intermediary Only" clause in Terms of Service (ToS).
- **Validation:** Admin-side verification of provider documentation (ID, License, Insurance).

## 7. Development Timeline (6x 1-Week Sprints)
- **Week 1:** Environment Setup, Core Models (User, Categories), and Phone-based Auth.
- **Week 2:** Provider Profiles, Vehicle Management, and KYC Documentation logic.
- **Week 3:** Pricing Engine (Distance/Hourly) and Matching Workflow (Request/Estimation).
- **Week 4:** Real-time Notification System, Contact Privacy Logic, and Order Flow Logic.
- **Week 5:** Multi-language (i18n) implementation, RTL UI Polish, and Admin Dashboard.
- **Week 6:** Commission Ledger, Final UAT (Algiers Stress Test), and Production Deployment.

