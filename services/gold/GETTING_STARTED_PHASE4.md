# Getting Started with Phase 4: Enhanced Ornament Catalog

## Quick Start Guide

### Prerequisites
- Phases 1-3 completed and running
- Database migrations applied
- Backend service running on port 8013
- Frontend running on port 3000

### 1. Apply Database Migration

```bash
# Navigate to project root
cd NBFCSUITE

# Apply Phase 4 migration
psql -U nbfc_user -d nbfcsuite -f infra/migrations/021_ornament_catalog.sql
```

**What this creates:**
- 10+ catalog tables (photos, stones, movements, conditions, etc.)
- Indexes for optimal performance
- Foreign keys for data integrity

### 2. Verify Backend Integration

The catalog router is already integrated in `services/gold/app/main.py`. Verify by checking:

```bash
# Test API documentation
curl http://localhost:8013/docs
```

You should see 30+ new endpoints under the "Ornament Catalog" tag.

### 3. Test API Endpoints

#### Add Photo to Ornament
```bash
curl -X POST http://localhost:8013/api/v1/gold/catalog/photos \
  -H "Content-Type: application/json" \
  -d '{
    "ornament_id": "orn-001",
    "photo_url": "https://example.com/photo.jpg",
    "photo_type": "general",
    "is_primary": true,
    "uploaded_by_user_id": "user-001"
  }'
```

#### Add Stone Details
```bash
curl -X POST http://localhost:8013/api/v1/gold/catalog/stones \
  -H "Content-Type: application/json" \
  -d '{
    "ornament_id": "orn-001",
    "stone_number": 1,
    "stone_type": "diamond",
    "stone_shape": "round",
    "carat_weight": 0.5,
    "is_certified": true
  }'
```

#### Record Movement with GPS
```bash
curl -X POST http://localhost:8013/api/v1/gold/catalog/movements \
  -H "Content-Type: application/json" \
  -d '{
    "ornament_id": "orn-001",
    "movement_type": "vaulted",
    "from_location": "Branch Counter",
    "to_location": "VAULT-A-R1-L5",
    "moved_by_user_id": "user-001",
    "gps_latitude": 12.9716,
    "gps_longitude": 77.5946,
    "qr_scanned": true
  }'
```

#### Verify Movement (Maker-Checker)
```bash
curl -X POST http://localhost:8013/api/v1/gold/catalog/movements/{movement_id}/verify \
  -H "Content-Type: application/json" \
  -d '{
    "verified_by_user_id": "user-002"
  }'
```


#### Record Condition Inspection
```bash
curl -X POST http://localhost:8013/api/v1/gold/catalog/conditions \
  -H "Content-Type: application/json" \
  -d '{
    "ornament_id": "orn-001",
    "inspector_user_id": "user-003",
    "overall_condition": "good",
    "has_damage": false,
    "weight_verified": true,
    "next_inspection_date": "2026-08-01"
  }'
```

#### Get Complete Ornament Profile
```bash
curl http://localhost:8013/api/v1/gold/catalog/profile/orn-001
```

### 4. Access Frontend

Navigate to the ornament catalog page:
```
http://localhost:3000/gold-lending/catalog/[ornamentId]
```

**Example:**
```
http://localhost:3000/gold-lending/catalog/orn-001
```

You'll see:
- 8 comprehensive tabs
- Quick stats dashboard
- Real-time data loading
- Professional UI

---

## Common Use Cases

### Use Case 1: Complete Ornament Onboarding

```javascript
// 1. Create appraisal session (Phase 3)
const session = await goldApi.createAppraisalSession({
  customer_id: "cust-001",
  branch_id: "branch-001"
});

// 2. Add ornament
const ornament = await goldApi.addOrnamentToSession(session.id, {
  ornament_type_id: "type-001",
  gross_weight_grams: 50.5,
  stone_weight_grams: 2.3
});

// 3. Add photos
await goldApi.addOrnamentPhoto({
  ornament_id: ornament.id,
  photo_type: "general",
  photo_url: "https://...",
  is_primary: true
});

await goldApi.addOrnamentPhoto({
  ornament_id: ornament.id,
  photo_type: "hallmark",
  photo_url: "https://..."
});

// 4. Catalog stones
await goldApi.addStone({
  ornament_id: ornament.id,
  stone_number: 1,
  stone_type: "diamond",
  carat_weight: 0.5
});

// 5. Record movement to vault
const movement = await goldApi.recordMovement({
  ornament_id: ornament.id,
  movement_type: "vaulted",
  to_location: "VAULT-A-R1-L5",
  moved_by_user_id: "officer-001",
  gps_latitude: 12.9716,
  gps_longitude: 77.5946,
  qr_scanned: true
});

// 6. Verify movement (different user)
await goldApi.verifyMovement(movement.id, "supervisor-001");

// 7. Add certificate
await goldApi.addCertificate({
  ornament_id: ornament.id,
  certificate_type: "hallmark",
  certificate_number: "HM-2026-12345",
  issuing_authority: "BIS"
});
```


### Use Case 2: Fraud Detection Workflow

```javascript
// System automatically compares new ornament with existing ones
const comparison = await goldApi.createComparison({
  ornament_id_1: "orn-new",
  ornament_id_2: "orn-existing",
  comparison_type: "duplicate_detection",
  similarity_score: 0.87,
  compared_by: "system"
});

// If high similarity, flag for investigation
if (comparison.similarity_score > 0.85) {
  // Investigation workflow triggered
  const flaggedComparisons = await goldApi.listComparisons(null, true);
  
  // Security team reviews
  // Photos compared
  // Customer history checked
  // Decision made: fraud or legitimate
}
```

### Use Case 3: Periodic Inspection

```javascript
// Get ornaments due for inspection
const dueInspections = await goldApi.getDueInspections(30);

// For each ornament, conduct inspection
for (const item of dueInspections) {
  const inspection = await goldApi.createConditionInspection({
    ornament_id: item.ornament_id,
    inspector_user_id: "inspector-001",
    overall_condition: "good",
    has_damage: false,
    weight_verified: true,
    next_inspection_date: "2026-10-01"
  });
}
```

### Use Case 4: Insurance Management

```javascript
// Add insurance policy
const insurance = await goldApi.addInsurance({
  ornament_id: "orn-001",
  policy_number: "INS-2026-001",
  insurance_provider: "ICICI Lombard",
  insured_value: 250000,
  premium_amount: 5000,
  policy_start_date: "2026-07-01",
  policy_end_date: "2027-07-01",
  coverage_type: "comprehensive"
});

// Check expiring policies
const allOrnaments = await getAllOrnaments();
for (const orn of allOrnaments) {
  const ins = await goldApi.getOrnamentInsurance(orn.id);
  const expiryDate = new Date(ins.policy_end_date);
  const daysToExpiry = (expiryDate - new Date()) / (1000 * 60 * 60 * 24);
  
  if (daysToExpiry < 30) {
    // Send renewal notification
  }
}
```

---

## Testing Checklist

### Backend Tests

- [ ] Photo upload and retrieval
- [ ] Primary photo designation
- [ ] Stone catalog CRUD
- [ ] Movement recording with GPS
- [ ] Maker-checker verification
- [ ] Condition inspection creation
- [ ] Tag management
- [ ] Comparison creation
- [ ] Certificate verification
- [ ] Insurance lifecycle
- [ ] Group management
- [ ] Complete profile aggregation

### Frontend Tests

- [ ] Navigate to catalog page
- [ ] View all 8 tabs
- [ ] Quick stats display correctly
- [ ] Photos load and display
- [ ] Stone catalog renders
- [ ] Movement history shows GPS
- [ ] Condition inspections visible
- [ ] Certificates display
- [ ] Insurance shows expiry alerts
- [ ] Groups membership visible


---

## Troubleshooting

### Issue: "Photo not uploading"
**Solution:** Ensure `photo_url` is valid and accessible. For production, use S3/CDN URLs.

### Issue: "Maker-checker verification failing"
**Solution:** Verify that `verified_by_user_id` is different from `moved_by_user_id`. Same user cannot verify their own actions.

### Issue: "GPS coordinates not saving"
**Solution:** Ensure coordinates are valid floats. Latitude: -90 to 90, Longitude: -180 to 180.

### Issue: "Complete profile returns empty data"
**Solution:** Ensure ornament has been created in Phase 3 appraisal first. Catalog extends appraisal data.

### Issue: "Certificate verification not working"
**Solution:** Certificate must be created first before verification. Use two-step process: create, then verify.

---

## Performance Tips

### 1. Use Pagination
```javascript
// For large lists, use pagination
const movements = await goldApi.listOrnamentMovements(ornamentId);
// Implement client-side pagination or modify API to support it
```

### 2. Cache Complete Profiles
```javascript
// Cache frequently accessed profiles
const profileCache = new Map();

async function getCachedProfile(ornamentId) {
  if (!profileCache.has(ornamentId)) {
    const profile = await goldApi.getOrnamentCompleteProfile(ornamentId);
    profileCache.set(ornamentId, profile);
  }
  return profileCache.get(ornamentId);
}
```

### 3. Batch Operations
```javascript
// Instead of multiple individual calls
const photos = await Promise.all([
  goldApi.addOrnamentPhoto(photo1),
  goldApi.addOrnamentPhoto(photo2),
  goldApi.addOrnamentPhoto(photo3)
]);
```

---

## Security Best Practices

### 1. Always Use Maker-Checker for Critical Operations
```javascript
// Movement should always be verified
const movement = await goldApi.recordMovement(data);
// Ensure different user verifies
await goldApi.verifyMovement(movement.id, differentUserId);
```

### 2. Validate GPS Coordinates
```javascript
function isValidGPS(lat, lon) {
  return lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180;
}
```

### 3. Implement Photo Size Limits
```javascript
// Client-side validation
const MAX_PHOTO_SIZE = 5 * 1024 * 1024; // 5MB

if (file.size > MAX_PHOTO_SIZE) {
  alert('Photo too large. Maximum 5MB allowed.');
  return;
}
```

### 4. Use HTTPS for Photo URLs
```javascript
// Ensure all photo URLs use HTTPS
if (!photoUrl.startsWith('https://')) {
  throw new Error('Photo URL must use HTTPS');
}
```

---

## Next Steps

After completing Phase 4, you're ready for:

### **Phase 5: Vault & Packet Management**
- Hierarchical vault structure
- QR code generation
- Automated packet tracking
- Vault capacity management

### Integration Points
Phase 4 catalog data will integrate with:
- Phase 5: Movement tracking feeds vault operations
- Phase 6: Disbursement uses complete profile
- Phase 8: Auction uses photos and certificates
- Phase 10: AI uses tags and comparison data

---

## Resources

- **API Documentation**: http://localhost:8013/docs
- **Phase 4 Detailed Docs**: `services/gold/PHASE4_ORNAMENT_CATALOG.md`
- **Complete Platform Summary**: `services/gold/GOLD_LENDING_PLATFORM_SUMMARY.md`
- **Database Schema**: `infra/migrations/021_ornament_catalog.sql`

---

## Support

For issues or questions:
1. Check API documentation at `/docs`
2. Review Phase 4 comprehensive documentation
3. Verify database migration was applied correctly
4. Check backend logs for errors

**Phase 4 Status**: ✅ Complete and Ready for Production Testing
