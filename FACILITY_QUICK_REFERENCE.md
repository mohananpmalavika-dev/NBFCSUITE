# Facility & Administration - Quick Reference Guide

## 🚀 Quick Start

### Backend Testing
```bash
# Start the backend server
cd backend
python main.py

# API Documentation
http://localhost:8000/docs
```

### Frontend Integration
```typescript
// Import services
import { buildingService, visitorService } from '@/services/facility';

// Example: Get buildings
const buildings = await buildingService.getBuildings();

// Example: Check in visitor
const visitor = await visitorService.checkInVisitor(visitorId, badgeNumber);
```

---

## 📋 API Endpoints Cheat Sheet

### Building Management
```
POST   /api/v1/facility/buildings                     - Create building
GET    /api/v1/facility/buildings                     - List buildings
GET    /api/v1/facility/buildings/{id}                - Get building
PUT    /api/v1/facility/buildings/{id}                - Update building
DELETE /api/v1/facility/buildings/{id}                - Delete building
POST   /api/v1/facility/buildings/{id}/floors         - Add floor
GET    /api/v1/facility/buildings/rooms               - List all rooms
```

### Housekeeping
```
POST   /api/v1/facility/housekeeping/tasks            - Create task
GET    /api/v1/facility/housekeeping/tasks            - List tasks
PATCH  /api/v1/facility/housekeeping/tasks/{id}/status - Update status
POST   /api/v1/facility/housekeeping/tasks/{id}/assign - Assign task
```

### Cafeteria
```
POST   /api/v1/facility/cafeteria/menu                - Add menu item
GET    /api/v1/facility/cafeteria/menu                - List menu
POST   /api/v1/facility/cafeteria/orders              - Create order
GET    /api/v1/facility/cafeteria/orders              - List orders
```

### Transport
```
POST   /api/v1/facility/transport/vehicles            - Add vehicle
GET    /api/v1/facility/transport/vehicles            - List vehicles
POST   /api/v1/facility/transport/trips               - Schedule trip
POST   /api/v1/facility/transport/trips/{id}/start    - Start trip
POST   /api/v1/facility/transport/trips/{id}/complete - Complete trip
```

### Visitor Management
```
POST   /api/v1/facility/visitors                      - Register visitor
GET    /api/v1/facility/visitors                      - List visitors
POST   /api/v1/facility/visitors/{id}/check-in        - Check in
POST   /api/v1/facility/visitors/{id}/check-out       - Check out
GET    /api/v1/facility/visitors/active/current       - Active visitors
```

---

## 🔑 Common Status Values

### Building Status
- `active` - Building is operational
- `under_construction` - Under construction
- `maintenance` - Under maintenance
- `inactive` - Not in use

### Room Status
- `available` - Ready for use
- `occupied` - Currently in use
- `under_maintenance` - Being maintained
- `reserved` - Reserved for future use
- `out_of_service` - Not available

### Task Status
- `pending` - Not started
- `in_progress` - Being worked on
- `completed` - Finished
- `cancelled` - Cancelled
- `on_hold` - Paused

### Order Status
- `pending` - Order placed
- `confirmed` - Order confirmed
- `preparing` - Being prepared
- `ready` - Ready for pickup
- `served` - Delivered
- `cancelled` - Cancelled

### Trip Status
- `scheduled` - Planned
- `in_progress` - Ongoing
- `completed` - Finished
- `cancelled` - Cancelled

### Visitor Status
- `scheduled` - Pre-registered
- `checked_in` - Entered premises
- `in_meeting` - In meeting
- `checked_out` - Left premises
- `cancelled` - Visit cancelled

---

## 💡 Common Use Cases

### 1. Register a New Building
```typescript
const building = await buildingService.createBuilding({
  building_code: 'BLD001',
  building_name: 'Main Office',
  building_type: 'office',
  city: 'Mumbai',
  state: 'Maharashtra',
  total_area_sqft: 50000,
  has_elevator: true,
  has_parking: true,
  parking_capacity: 100
});
```

### 2. Create a Housekeeping Task
```typescript
const task = await housekeepingService.createTask({
  task_type: 'cleaning',
  task_name: 'Floor 3 Deep Cleaning',
  building_id: 1,
  floor_id: 3,
  scheduled_date: '2026-12-10',
  priority: 'high'
});
```

### 3. Place a Cafeteria Order
```typescript
const order = await cafeteriaService.createOrder({
  employee_id: 123,
  meal_type: 'lunch',
  delivery_location: 'Floor 2, Room 201',
  items: [
    { menu_item_id: 5, quantity: 1 },
    { menu_item_id: 12, quantity: 2 }
  ]
});
```

### 4. Schedule a Trip
```typescript
const trip = await transportService.createTrip({
  vehicle_id: 10,
  driver_id: 45,
  trip_date: '2026-12-11',
  start_location: 'Main Office',
  end_location: 'Branch Office - Pune',
  purpose: 'Document delivery',
  passenger_count: 2
});
```

### 5. Register a Visitor
```typescript
const visitor = await visitorService.createVisitor({
  visitor_name: 'John Doe',
  visitor_type: 'customer',
  company_name: 'ABC Corp',
  mobile_number: '9876543210',
  purpose: 'meeting',
  host_employee_id: 78,
  visit_date: '2026-12-08',
  expected_in_time: '14:00:00'
});
```

---

## 🔍 Filtering Examples

### Filter Buildings by Type
```typescript
const offices = await buildingService.getBuildings({
  building_type: 'office',
  status: 'active'
});
```

### Filter Tasks by Status and Date
```typescript
const tasks = await housekeepingService.getTasks({
  status: 'pending',
  priority: 'high',
  from_date: '2026-12-01',
  to_date: '2026-12-31',
  building_id: 1
});
```

### Search Visitors
```typescript
const visitors = await visitorService.getVisitors({
  search: 'john',
  status: 'checked_in',
  from_date: '2026-12-01'
});
```

---

## 🛠️ Database Queries

### Check Building Capacity
```sql
SELECT 
  b.building_name,
  COUNT(r.id) as total_rooms,
  SUM(CASE WHEN r.status = 'available' THEN 1 ELSE 0 END) as available_rooms
FROM facility_buildings b
LEFT JOIN facility_rooms r ON b.id = r.building_id
GROUP BY b.id, b.building_name;
```

### Today's Pending Tasks
```sql
SELECT * FROM facility_housekeeping_tasks
WHERE scheduled_date = CURRENT_DATE
  AND status = 'pending'
  AND is_deleted = false
ORDER BY priority DESC;
```

### Active Visitors Count
```sql
SELECT COUNT(*) as active_visitors
FROM facility_visitors
WHERE status IN ('checked_in', 'in_meeting')
  AND is_deleted = false;
```

---

## 🎯 Best Practices

### 1. Always Use Tenant ID
```typescript
// Tenant ID is automatically added by middleware
// Just ensure user is authenticated
```

### 2. Handle Errors Gracefully
```typescript
try {
  const building = await buildingService.getBuilding(id);
} catch (error) {
  if (error.response?.status === 404) {
    console.log('Building not found');
  }
}
```

### 3. Use Pagination for Large Lists
```typescript
const buildings = await buildingService.getBuildings({
  skip: 0,
  limit: 50
});
```

### 4. Update Status Progressively
```typescript
// Task workflow
await housekeepingService.updateTaskStatus(taskId, 'in_progress');
// ... work on task ...
await housekeepingService.updateTaskStatus(taskId, 'completed', 'All areas cleaned');
```

---

## 🚨 Common Issues & Solutions

### Issue: Building Not Found
**Solution**: Check if building exists and user has access to tenant

### Issue: Task Assignment Failed
**Solution**: Verify employee_id exists in HRMS module

### Issue: Order Creation Failed
**Solution**: Ensure all menu items are available and prices are set

### Issue: Vehicle Already In Use
**Solution**: Check vehicle status and existing trips for the date

### Issue: Visitor Check-in Failed
**Solution**: Verify visitor has a scheduled entry for today

---

## 📞 Support

For issues or questions:
1. Check API documentation at `/docs`
2. Review error messages in API responses
3. Check database logs for detailed errors
4. Verify tenant ID and user permissions

---

**Last Updated**: December 7, 2026
**Module Version**: 1.0.0
**Status**: Production Ready
