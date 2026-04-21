# Inventory Management System - Specification

## 1. Project Overview

**Project Name:** InvenTrack Pro
**Project Type:** Full-stack Web Application (Django + HTMX + Tailwind CSS)
**Core Functionality:** A professional inventory management system with real-time stock tracking, SKU management, transaction auditing, and data visualization.
**Target Users:** Warehouse managers, inventory clerks, small-to-medium business owners

---

## 2. UI/UX Specification

### Layout Structure

- **Sidebar-Driven Layout:** Fixed left sidebar (280px) with collapsible menu
- **Main Content Area:** Fluid width with max-width 1600px, centered
- **Header Bar:** Sticky top bar with search, notifications, and user profile
- **Content Sections:** Card-based modular design

### Responsive Breakpoints
- Desktop: 1280px+ (full sidebar)
- Tablet: 768px-1279px (collapsed sidebar, hamburger menu)
- Mobile: <768px (drawer sidebar)

### Visual Design

**Color Palette:**
- Primary: `#0F172A` (Slate 900 - sidebar background)
- Secondary: `#1E293B` (Slate 800 - cards)
- Accent: `#10B981` (Emerald 500 - success/add actions)
- Warning: `#F59E0B` (Amber 500 - low stock alerts)
- Danger: `#EF4444` (Red 500 - critical/out of stock)
- Surface: `#F8FAFC` (Slate 50 - main background)
- Text Primary: `#1E293B` (Slate 800)
- Text Muted: `#64748B` (Slate 500)
- Border: `#E2E8F0` (Slate 200)

**Typography:**
- Font Family: `'DM Sans', sans-serif` (headings), `'IBM Plex Sans', sans-serif` (body)
- Headings: 24px (h1), 20px (h2), 16px (h3)
- Body: 14px regular, 14px medium
- Small: 12px

**Spacing System:**
- Base unit: 4px
- Padding: 16px (cards), 24px (sections)
- Gap: 16px (grid items)

**Visual Effects:**
- Card shadows: `0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)`
- Hover elevation: `0 4px 6px rgba(0,0,0,0.1)`
- Border radius: 8px (cards), 6px (buttons), 4px (inputs)
- Transitions: 200ms ease-out

### Components

**Sidebar:**
- Logo/brand area at top
- Navigation menu with icons
- Active state: emerald left border + emerald text
- Hover: slate-700 background

**Data Tables:**
- Striped rows (alternate slate-50/white)
- Sortable column headers
- Live search filter input
- Pagination controls
- Row hover state

**Modals:**
- Centered overlay with backdrop blur
- Slide-in animation
- Close button (X) top-right
- Form inputs with labels

**Cards/Widgets:**
- Stat cards with icon, value, label
- Chart cards with title and canvas
- Alert cards for low stock warnings

**Buttons:**
- Primary: Emerald background, white text
- Secondary: Slate-200 background, slate-700 text
- Danger: Red background, white text
- States: hover (darken 10%), active (scale 0.98), disabled (opacity 50%)

**Form Inputs:**
- Border: slate-300
- Focus: emerald ring (2px)
- Error: red border + error message
- Labels above inputs

**Alerts/Notifications:**
- Toast notifications (top-right)
- Low stock: amber background, amber icon
- Success: emerald background, check icon

---

## 3. Functionality Specification

### Core Features

**Product Management:**
- Create, read, update, delete products
- Auto-generate SKU (format: CAT-XXXXX)
- Track stock quantity, reorder level, unit price
- Product image upload (optional)
- Category assignment

**Category Management:**
- CRUD for categories
- Category-based product filtering
- Category icons/colors

**Transaction Ledger:**
- Log all stock movements (in/out/adjustment)
- Timestamp, quantity, type, user reference
- Searchable/filterable audit trail
- Export capability

**Stock Operations:**
- Add stock (purchase/order received)
- Remove stock (sale/shipment)
- Stock adjustment (corrections)
- Each operation creates ledger entry

**Data Visualization:**
- Stock levels bar chart (by category)
- Transaction trend line chart (30 days)
- Top products pie chart
- Real-time updates via HTMX

**Search & Filtering:**
- Live search across products (name, SKU, category)
- Filter by category, stock status
- Sort by any column

**Low Stock Alerts:**
- Automatic detection when stock <= reorder level
- Visual indicators (amber badge)
- Dedicated alert panel
- Notification count in header

### User Interactions

- Click sidebar nav → content loads via HTMX
- Type in search → live filtering (300ms debounce)
- Click "Add Product" → modal opens
- Submit form → HTMX POST → modal closes → table refreshes
- Click stock +/- → modal with quantity input → confirm
- Click chart filter → chart re-renders

### Data Handling

- SQLite database (single file)
- Django ORM for queries
- DRF for API endpoints
- HTMX for partial page updates

---

## 4. Technical Architecture

### Models

```
Category:
  - id (PK)
  - name (Char 100)
  - description (Text)
  - color (Char 7 - hex)
  - created_at, updated_at

Product:
  - id (PK)
  - sku (Char 10, unique)
  - name (Char 200)
  - description (Text)
  - category (FK → Category)
  - quantity (Int)
  - reorder_level (Int)
  - unit_price (Decimal)
  - image (ImageField optional)
  - created_at, updated_at

Transaction:
  - id (PK)
  - product (FK → Product)
  - transaction_type (Enum: IN, OUT, ADJUST)
  - quantity (Int)
  - notes (Text)
  - created_at
```

### Views

- Dashboard (overview stats, charts)
- Product List (table, search, filter)
- Product Create/Edit (modal forms)
- Category List/Create
- Transaction Ledger (audit log)
- API endpoints (DRF)

### URLs

```
/                    → Dashboard
/products            → Product list
/products/new        → Create product (modal)
/products/<id>/edit  → Edit product (modal)
/products/<id>/stock → Stock operation (modal)
/categories          → Category management
/ledger              → Transaction audit log
/api/products        → DRF API
/api/categories      → DRF API
/api/transactions    → DRF API
```

---

## 5. Acceptance Criteria

### Visual Checkpoints
- [ ] Sidebar displays with dark slate background
- [ ] Cards have proper shadows and rounded corners
- [ ] Emerald accent color used for primary actions
- [ ] Tables have striped rows and hover states
- [ ] Charts render with proper colors
- [ ] Modals have backdrop blur effect
- [ ] Search input filters table in real-time

### Functional Checkpoints
- [ ] Products can be created via modal form
- [ ] SKU auto-generates in correct format
- [ ] Stock quantity updates without page reload
- [ ] Transaction ledger records all movements
- [ ] Low stock alerts show when qty <= reorder
- [ ] Charts update when data changes
- [ ] Search filters products instantly

### Performance
- [ ] Page loads under 2 seconds
- [ ] HTMX updates under 500ms
- [ ] No full page reloads on interactions