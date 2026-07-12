# Facility & Administration - Complete Component Index

Quick reference guide for all 30+ React components in the Facility module.

---

## 🏢 Building Management (6 Components)

### BuildingList.tsx
**Path**: `frontend/src/components/facility/building/BuildingList.tsx`  
**Purpose**: Main building management interface  
**Features**:
- Search buildings by code/name/location
- Filter by building type and status
- Paginated table view
- Quick actions (View, Edit, Delete)
- Statistics cards (Total, Active, Under Construction)

**Usage**:
```tsx
import { BuildingList } from '@/components/facility/building';
<BuildingList />
```

---

### BuildingForm.tsx
**Path**: `frontend/src/components/facility/building/BuildingForm.tsx`  
**Purpose**: Create/Edit building dialog  
**Props**:
- `building?: Building | null` - Building to edit (null for new)
- `onClose: () => void` - Close callback
- `onSuccess: () => void` - Success callback

**Usage**:
```tsx
<BuildingForm 
  building={selectedBuilding}
  onClose={() => setShowForm(false)}
  onSuccess={handleSuccess}
/>
```

---

### BuildingDetails.tsx
**Path**: `frontend/src/components/facility/building/BuildingDetails.tsx`  
**Purpose**: Detailed building view with tabs  
**Features**:
- Overview tab with specifications
- Floors tab with FloorManager
- Rooms tab with RoomGrid
- Statistics and metrics

---

### FloorManager.tsx
**Path**: `frontend/src/components/facility/building/FloorManager.tsx`  
**Purpose**: Manage floors within a building  
**Features**:
- Add new floors
- Edit floor details
- Track floor area and facilities
- Manage restroom/pantry flags

---

### RoomGrid.tsx
**Path**: `frontend/src/components/facility/building/RoomGrid.tsx`  
**Purpose**: Visual grid of rooms  
**Features**:
- Card-based room layout
- Quick status updates
- Filter by floor
- Room capacity and amenities

---

### RoomStatusCard.tsx
**Path**: `frontend/src/components/facility/building/RoomStatusCard.tsx`  
**Purpose**: Room availability widget  
**Features**:
- Real-time status overview
- Occupancy rate calculation
- Color-coded indicators
- Utilization statistics

---

## 🧹 Housekeeping Management (5 Components)

### TaskBoard.tsx
**Path**: `frontend/src/components/facility/housekeeping/TaskBoard.tsx`  
**Purpose**: Kanban-style task management  
**Features**:
- 4-column workflow (Pending → In Progress → Completed → On Hold)
- Drag-like card interface
- Priority badges
- Quick status updates

---

### TaskList.tsx
**Path**: `frontend/src/components/facility/housekeeping/TaskList.tsx`  
**Purpose**: Table view of all tasks  
**Features**:
- Search by task code/name
- Filter by status and priority
- Sort by date/priority
- Bulk operations

---

### TaskForm.tsx
**Path**: `frontend/src/components/facility/housekeeping/TaskForm.tsx`  
**Purpose**: Create/Edit task dialog  
**Features**:
- Task type selection (8 types)
- Location picker (building/floor/room)
- Schedule date and time
- Assign to employee
- Priority levels

---

### SupplyInventory.tsx
**Path**: `frontend/src/components/facility/housekeeping/SupplyInventory.tsx`  
**Purpose**: Stock management table  
**Features**:
- Real-time inventory levels
- Low-stock indicators
- Category filtering
- Total value calculation
- Supplier information

---

### SupplyAlerts.tsx
**Path**: `frontend/src/components/facility/housekeeping/SupplyAlerts.tsx`  
**Purpose**: Low-stock warning system  
**Features**:
- Critical/urgent/low severity levels
- Reorder recommendations
- Bulk reorder functionality
- Cost estimation

---

## 🍽️ Cafeteria Management (6 Components)

### MenuManager.tsx
**Path**: `frontend/src/components/facility/cafeteria/MenuManager.tsx`  
**Purpose**: Menu item CRUD interface  
**Features**:
- Add/edit menu items
- Filter by meal type and category
- Pricing (regular & employee)
- Availability toggle
- Vegetarian indicator

---

### MenuCard.tsx
**Path**: `frontend/src/components/facility/cafeteria/MenuCard.tsx`  
**Purpose**: Visual menu item display  
**Features**:
- Image support
- Nutritional information
- Pricing display
- Add to cart button

---

### OrderForm.tsx
**Path**: `frontend/src/components/facility/cafeteria/OrderForm.tsx`  
**Purpose**: Multi-item order creation  
**Features**:
- Shopping cart functionality
- Quantity adjustment
- Meal type selection
- Delivery location
- Real-time total calculation

---

### OrderTracking.tsx
**Path**: `frontend/src/components/facility/cafeteria/OrderTracking.tsx`  
**Purpose**: Customer order tracking  
**Features**:
- Real-time status updates
- Progress bar
- 5-stage timeline
- Estimated time display
- Auto-refresh (10s)

---

### OrderHistory.tsx
**Path**: `frontend/src/components/facility/cafeteria/OrderHistory.tsx`  
**Purpose**: Past orders report  
**Features**:
- Date range filtering
- Revenue statistics
- Order analytics
- Export capabilities

---

### KitchenDisplay.tsx
**Path**: `frontend/src/components/facility/cafeteria/KitchenDisplay.tsx`  
**Purpose**: Kitchen workflow management  
**Features**:
- Order queue by status
- Urgency alerts (color-coded)
- Quick action buttons
- Order age tracking
- Auto-refresh (5s)

---

## 🚗 Transport Management (6 Components)

### VehicleList.tsx
**Path**: `frontend/src/components/facility/transport/VehicleList.tsx`  
**Purpose**: Fleet overview table  
**Features**:
- Vehicle status tracking
- Filter by type and status
- Mileage monitoring
- Fuel type and ownership
- Fleet statistics

---

### VehicleCard.tsx
**Path**: `frontend/src/components/facility/transport/VehicleCard.tsx`  
**Purpose**: Vehicle display card  
**Features**:
- Availability status
- Capacity and specifications
- Quick actions
- Visual status indicators

---

### TripScheduler.tsx
**Path**: `frontend/src/components/facility/transport/TripScheduler.tsx`  
**Purpose**: Calendar-based trip planner  
**Features**:
- Date navigation
- Trip statistics by status
- Detailed trip cards
- Vehicle and driver info

---

### TripForm.tsx
**Path**: `frontend/src/components/facility/transport/TripForm.tsx`  
**Purpose**: Trip booking dialog  
**Features**:
- Vehicle selection (available only)
- Driver assignment
- Route planning
- Passenger count
- Purpose tracking

---

### TripTracker.tsx
**Path**: `frontend/src/components/facility/transport/TripTracker.tsx`  
**Purpose**: Live trip monitoring  
**Features**:
- Real-time tracking
- In-progress trips only
- Route visualization
- Auto-refresh

---

### MaintenanceCalendar.tsx
**Path**: `frontend/src/components/facility/transport/MaintenanceCalendar.tsx`  
**Purpose**: Service scheduling  
**Features**:
- Upcoming maintenance
- Priority levels (High/Medium/Low)
- Mileage-based alerts
- 30-day forecast

---

## 👥 Visitor Management (7 Components)

### VisitorKiosk.tsx
**Path**: `frontend/src/components/facility/visitor/VisitorKiosk.tsx`  
**Purpose**: Self-service registration  
**Features**:
- Touch-friendly interface
- Simplified form
- Instant pass generation
- Success confirmation

---

### VisitorForm.tsx
**Path**: `frontend/src/components/facility/visitor/VisitorForm.tsx`  
**Purpose**: Full visitor registration  
**Features**:
- Complete visitor details
- ID proof capture
- Host employee selection
- Purpose tracking
- Visit scheduling

---

### VisitorList.tsx
**Path**: `frontend/src/components/facility/visitor/VisitorList.tsx`  
**Purpose**: Visitor registry  
**Features**:
- Search and filtering
- Check-in/out actions
- Status management
- Visit history

---

### CheckInOutWidget.tsx
**Path**: `frontend/src/components/facility/visitor/CheckInOutWidget.tsx`  
**Purpose**: Quick check-in/out  
**Features**:
- Pass number lookup
- Fast processing
- Minimal clicks
- Error handling

---

### ActiveVisitorsBoard.tsx
**Path**: `frontend/src/components/facility/visitor/ActiveVisitorsBoard.tsx`  
**Purpose**: Live visitor display  
**Features**:
- Currently on premises
- Auto-refresh (30s)
- Badge information
- Host details

---

### VisitorBadge.tsx
**Path**: `frontend/src/components/facility/visitor/VisitorBadge.tsx`  
**Purpose**: Badge printing component  
**Features**:
- Formatted visitor pass
- QR code ready
- Company branding
- Print-optimized layout

---

### VisitorHistory.tsx
**Path**: `frontend/src/components/facility/visitor/VisitorHistory.tsx`  
**Purpose**: Historical visitor records  
**Features**:
- Date range filtering
- Visit duration calculation
- Analytics data
- Export capabilities

---

## 📦 Import Examples

### Import Single Component
```tsx
import { BuildingList } from '@/components/facility/building';
```

### Import Multiple Components
```tsx
import { 
  BuildingList, 
  BuildingForm, 
  BuildingDetails 
} from '@/components/facility/building';
```

### Import from Different Modules
```tsx
import { TaskBoard } from '@/components/facility/housekeeping';
import { MenuManager } from '@/components/facility/cafeteria';
import { VehicleList } from '@/components/facility/transport';
```

---

## 🎨 Common Props Pattern

Most components follow this pattern:

```tsx
interface CommonProps {
  // For forms/dialogs
  onClose?: () => void;
  onSuccess?: () => void;
  
  // For edit mode
  item?: T | null;
  
  // For display cards
  showActions?: boolean;
  onEdit?: () => void;
  onSelect?: (item: T) => void;
}
```

---

## 🔗 Component Dependencies

All components depend on:
- `@/components/ui/*` - shadcn/ui components
- `@/services/facility/*` - API service layers
- `@/types/facility` - TypeScript types
- `lucide-react` - Icons
- `react-hook-form` - Form handling

---

## 📊 Component Complexity Matrix

| Component | Lines | Complexity | API Calls |
|-----------|-------|------------|-----------|
| BuildingList | ~150 | Medium | 2 |
| BuildingForm | ~180 | High | 2 |
| TaskBoard | ~140 | High | 3 |
| KitchenDisplay | ~160 | High | 2 |
| OrderForm | ~200 | Very High | 3 |
| TripScheduler | ~180 | High | 2 |
| VisitorKiosk | ~150 | Medium | 1 |

---

## 🚀 Quick Start Guide

1. **Import the component**:
```tsx
import { ComponentName } from '@/components/facility/module';
```

2. **Use in your page**:
```tsx
export default function Page() {
  return <ComponentName />;
}
```

3. **Handle callbacks** (for forms):
```tsx
const [showForm, setShowForm] = useState(false);

<ComponentForm 
  onClose={() => setShowForm(false)}
  onSuccess={() => {
    setShowForm(false);
    loadData();
  }}
/>
```

---

*Last Updated: December 2024*  
*Total Components: 30+*  
*Status: Production Ready*
