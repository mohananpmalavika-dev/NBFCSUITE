# Getting Started with Phase 5: Vault & Packet Management
## Quick Start Guide - 15 Minutes to Complete Vault Setup

---

## 🎯 What You'll Learn

In this quick start guide, you'll:
1. Set up your first vault with complete hierarchy
2. Create and seal your first packet
3. Add ornaments to the packet
4. Record packet movements
5. Schedule and conduct a vault audit
6. Verify security seals

**Time Required:** 15 minutes  
**Prerequisites:** Phase 3 & 4 completed, ornaments available in catalog

---

## 🚀 Step 1: Database Setup (2 minutes)

### Run Migration

```bash
# Navigate to project root
cd c:\NBFCSUITE

# Run Phase 5 migration
psql -U postgres -d nbfc_gold_lending -f infra/migrations/022_vault_packet_management.sql

# Verify tables created
psql -U postgres -d nbfc_gold_lending -c "\dt gold_vault*"
psql -U postgres -d nbfc_gold_lending -c "\dt gold_packet*"
```

**Expected Output:**
```
 gold_vaults
 gold_vault_racks
 gold_vault_lockers
 gold_vault_trays
 gold_packets
 gold_packet_ornaments
 gold_packet_movements
 gold_vault_audits
 gold_audit_findings
 gold_vault_access_log
 gold_security_seals
```

### Install Dependencies

```bash
# Install QR code library
pip install qrcode[pil]

# Verify installation
python -c "import qrcode; print('QR code library installed successfully')"
```

---

## 🏢 Step 2: Create Your First Vault (3 minutes)



### Using API

```bash
curl -X POST http://localhost:8003/api/v1/gold/vaults \
  -H "Content-Type: application/json" \
  -d '{
    "vault_code": "VLT-MUM-001",
    "vault_name": "Mumbai Main Vault",
    "location": "Ground Floor, Security Wing, Mumbai Branch",
    "vault_type": "high_security",
    "capacity_racks": 20,
    "security_level": "high_security",
    "manager_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Save the returned `vault_id` for next steps!**

### Using Frontend

1. Navigate to: `http://localhost:3000/gold-lending/vault`
2. Click **"Create Vault"** button
3. Fill in vault details:
   - Vault Code: `VLT-MUM-001`
   - Vault Name: `Mumbai Main Vault`
   - Location: Your branch location
   - Type: `high_security`
   - Capacity: `20 racks`
4. Click **"Create"**
5. Notice the QR code generated automatically!

---

## 📦 Step 3: Build Vault Hierarchy (3 minutes)

### Create a Rack

```bash
curl -X POST http://localhost:8003/api/v1/gold/vaults/{VAULT_ID}/racks \
  -H "Content-Type: application/json" \
  -d '{
    "rack_number": "R01",
    "position_code": "A1",
    "capacity_lockers": 20
  }'
```

### Create a Locker

```bash
curl -X POST http://localhost:8003/api/v1/gold/racks/{RACK_ID}/lockers \
  -H "Content-Type: application/json" \
  -d '{
    "locker_number": "L01",
    "capacity_trays": 10,
    "lock_type": "electronic"
  }'
```

### Create a Tray

```bash
curl -X POST http://localhost:8003/api/v1/gold/lockers/{LOCKER_ID}/trays \
  -H "Content-Type: application/json" \
  -d '{
    "tray_number": "T01",
    "capacity_packets": 20
  }'
```

**Quick Tip:** Use the frontend vault detail page to visualize your hierarchy!

---

## 📦 Step 4: Create and Seal Packet (4 minutes)

### Create Packet

```bash
curl -X POST http://localhost:8003/api/v1/gold/packets \
  -H "Content-Type: application/json" \
  -d '{
    "packet_number": "PKT-2024-001",
    "vault_id": "YOUR_VAULT_ID",
    "rack_id": "YOUR_RACK_ID",
    "locker_id": "YOUR_LOCKER_ID",
    "tray_id": "YOUR_TRAY_ID",
    "current_location": "VLT-MUM-001/R01/L01/T01"
  }'
```

**QR code generated automatically!**

### Add Ornaments to Packet

```bash
# Add first ornament
curl -X POST http://localhost:8003/api/v1/gold/packets/{PACKET_ID}/ornaments \
  -H "Content-Type: application/json" \
  -d '{
    "ornament_id": "YOUR_ORNAMENT_ID_1"
  }'

# Add second ornament
curl -X POST http://localhost:8003/api/v1/gold/packets/{PACKET_ID}/ornaments \
  -H "Content-Type: application/json" \
  -d '{
    "ornament_id": "YOUR_ORNAMENT_ID_2"
  }'
```

**Note:** Packet totals (count, weight, value) update automatically!

### Seal the Packet

```bash
curl -X POST http://localhost:8003/api/v1/gold/packets/{PACKET_ID}/seal \
  -H "Content-Type: application/json" \
  -d '{
    "seal_number": "SEAL-2024-001",
    "seal_type": "tamper_evident",
    "sealed_by": "YOUR_USER_ID"
  }'
```

✅ **Packet is now sealed and secure!**

---

## 🚚 Step 5: Record Packet Movement (2 minutes)

### Storage Movement

```bash
curl -X POST http://localhost:8003/api/v1/gold/packets/{PACKET_ID}/movements \
  -H "Content-Type: application/json" \
  -d '{
    "movement_type": "storage",
    "to_location": "VLT-MUM-001/R01/L01/T01",
    "reason": "Initial storage after appraisal",
    "gps_coordinates": "19.0760,72.8777",
    "notes": "Packet contains 2 gold necklaces"
  }'
```

### Relocation Movement

```bash
curl -X POST http://localhost:8003/api/v1/gold/packets/{PACKET_ID}/movements \
  -H "Content-Type: application/json" \
  -d '{
    "movement_type": "relocation",
    "from_location": "VLT-MUM-001/R01/L01/T01",
    "to_location": "VLT-MUM-001/R05/L12/T03",
    "reason": "Vault reorganization",
    "gps_coordinates": "19.0760,72.8777"
  }'
```

**View Movement History:**
```bash
curl http://localhost:8003/api/v1/gold/packets/{PACKET_ID}/movements
```

---

## 🔍 Step 6: Schedule Vault Audit (1 minute)

```bash
curl -X POST http://localhost:8003/api/v1/gold/vaults/{VAULT_ID}/audits \
  -H "Content-Type: application/json" \
  -d '{
    "audit_type": "routine",
    "scheduled_date": "2024-03-15",
    "auditor_id": "YOUR_USER_ID",
    "notes": "Q1 2024 routine compliance audit"
  }'
```

**Audit Types:**
- `routine`: Regular scheduled audits
- `surprise`: Unannounced spot checks
- `compliance`: Regulatory verification
- `incident`: Post-incident investigation

---

## 🎨 Frontend Walkthrough (Bonus)

### 1. Vault Dashboard
**URL:** `http://localhost:3000/gold-lending/vault`

**Features:**
- View all vaults with stats
- Total packets, ornaments, value
- Capacity utilization
- Create new vaults

### 2. Vault Detail Page
**URL:** `http://localhost:3000/gold-lending/vault/{vault-id}`

**Tabs:**
- **Overview**: Vault information
- **Hierarchy**: Rack → Locker → Tray structure
- **Inventory**: All packets in vault
- **Movements**: Recent movements
- **Audits**: Audit history

### 3. Packet Management
**URL:** `http://localhost:3000/gold-lending/vault/packets`

**Features:**
- List all packets with filters
- Search by packet number
- Filter by status, vault, seal status
- View packet details with QR code

### 4. Packet Detail
**URL:** `http://localhost:3000/gold-lending/vault/packets/{packet-id}`

**Tabs:**
- **Overview**: Packet info and location
- **Ornaments**: All ornaments in packet
- **Movement History**: Complete audit trail
- **Security Seals**: Seal status and history
- **QR Code**: Large QR with download

### 5. Audit Management
**URL:** `http://localhost:3000/gold-lending/vault/audits`

**Features:**
- Schedule new audits
- View audit calendar
- Start/complete audits
- Add findings
- Track compliance scores

---

## 🔐 Common Workflows

### Workflow 1: Daily Storage Operations

```bash
# 1. Create packet
PACKET_ID=$(curl -X POST http://localhost:8003/api/v1/gold/packets \
  -H "Content-Type: application/json" \
  -d '{"packet_number":"PKT-2024-001","vault_id":"VAULT_ID"}' \
  | jq -r '.id')

# 2. Add ornaments (repeat as needed)
curl -X POST http://localhost:8003/api/v1/gold/packets/$PACKET_ID/ornaments \
  -H "Content-Type: application/json" \
  -d '{"ornament_id":"ORNAMENT_ID"}'

# 3. Seal packet
curl -X POST http://localhost:8003/api/v1/gold/packets/$PACKET_ID/seal \
  -H "Content-Type: application/json" \
  -d '{"seal_number":"SEAL-001","seal_type":"tamper_evident","sealed_by":"USER_ID"}'

# 4. Record storage
curl -X POST http://localhost:8003/api/v1/gold/packets/$PACKET_ID/movements \
  -H "Content-Type: application/json" \
  -d '{"movement_type":"storage","to_location":"VLT-MUM-001/R01/L01/T01","reason":"Daily storage"}'
```

### Workflow 2: Packet Retrieval for Loan

```bash
# 1. Verify seal before access
curl http://localhost:8003/api/v1/gold/packets/{PACKET_ID}/seals

# 2. Break seal (authorized)
curl -X POST http://localhost:8003/api/v1/gold/seals/{SEAL_ID}/break \
  -H "Content-Type: application/json" \
  -d '{"broken_by":"USER_ID","break_reason":"Loan disbursement authorized"}'

# 3. Record withdrawal
curl -X POST http://localhost:8003/api/v1/gold/packets/{PACKET_ID}/movements \
  -H "Content-Type: application/json" \
  -d '{"movement_type":"withdrawal","from_location":"VLT-MUM-001/R01/L01/T01","reason":"Loan processing"}'
```

### Workflow 3: Conducting Audit

```bash
# 1. Get audit details
curl http://localhost:8003/api/v1/gold/audits/{AUDIT_ID}

# 2. Start audit
curl -X POST http://localhost:8003/api/v1/gold/audits/{AUDIT_ID}/start

# 3. Add finding (if issues found)
curl -X POST http://localhost:8003/api/v1/gold/audits/{AUDIT_ID}/findings \
  -H "Content-Type: application/json" \
  -d '{
    "finding_type": "location_mismatch",
    "severity": "medium",
    "description": "Packet found in different location than recorded",
    "location": "VLT-MUM-001/R01/L01/T02",
    "expected_value": "T01",
    "actual_value": "T02"
  }'

# 4. Complete audit
curl -X POST http://localhost:8003/api/v1/gold/audits/{AUDIT_ID}/complete \
  -H "Content-Type: application/json" \
  -d '{"compliance_score":98.5,"notes":"Minor issues resolved"}'
```

---

## 🎯 Success Criteria

After completing this guide, you should have:

✅ 1 vault created with QR code  
✅ Complete hierarchy (1 rack → 1 locker → 1 tray)  
✅ 1 packet created with QR code  
✅ 2+ ornaments added to packet  
✅ Packet sealed with tamper-evident seal  
✅ 2+ movement records created  
✅ 1 audit scheduled  

---

## 🔍 Verification Commands

### Check Vault Inventory

```bash
curl http://localhost:8003/api/v1/gold/vaults/{VAULT_ID}/inventory
```

### Check Packet Location

```bash
curl http://localhost:8003/api/v1/gold/packets/{PACKET_ID}
```

### View Movement History

```bash
curl http://localhost:8003/api/v1/gold/packets/{PACKET_ID}/movements
```

### Check Seal Status

```bash
curl http://localhost:8003/api/v1/gold/packets/{PACKET_ID}/seals
```

---

## 🐛 Troubleshooting

### Issue: QR Code Not Displaying

**Solution:**
```bash
# Verify qrcode library installed
pip list | grep qrcode

# Reinstall if needed
pip install --upgrade qrcode[pil]
```

### Issue: Movement API Returns 422

**Check movement_type values:**
- Valid: `storage`, `relocation`, `withdrawal`, `return`, `transfer`, `audit`
- Invalid: `move`, `store`, `retrieve`

### Issue: Cannot Add Ornament to Sealed Packet

**Solution:** This is by design. Unseal packet first:
```bash
# Break seal with proper authorization
curl -X POST http://localhost:8003/api/v1/gold/seals/{SEAL_ID}/break \
  -H "Content-Type: application/json" \
  -d '{"broken_by":"USER_ID","break_reason":"Need to add ornament"}'

# Add ornament
# Re-seal with new seal
```

### Issue: Hierarchy Not Loading in Frontend

**Check foreign key relationships:**
```sql
-- Verify vault hierarchy
SELECT 
  v.vault_code,
  r.rack_number,
  l.locker_number,
  t.tray_number
FROM gold_vaults v
LEFT JOIN gold_vault_racks r ON r.vault_id = v.id
LEFT JOIN gold_vault_lockers l ON l.rack_id = r.id
LEFT JOIN gold_vault_trays t ON t.locker_id = l.id;
```

---

## 📚 Next Steps

1. **Create More Test Data**
   - Add 5 more vaults
   - Create 10 packets
   - Add 50 ornaments across packets

2. **Test Complete Workflows**
   - Storage → Retrieval → Return cycle
   - Inter-vault transfers
   - Audit with findings

3. **Explore Advanced Features**
   - Seal verification workflows
   - Audit finding resolution
   - Movement analytics

4. **Integrate with Phase 6**
   - Prepare for loan origination
   - Test packet retrieval for loans
   - Setup loan-related movements

---

## 🎉 Congratulations!

You've successfully set up Phase 5 Vault & Packet Management System!

**What's Next?**
- Proceed to Phase 6: Loan Origination & Disbursement
- Review [Phase 5 Documentation](./PHASE5_VAULT_PACKET_MANAGEMENT.md)
- Check [Platform Summary](../../GOLD_LENDING_PLATFORM_SUMMARY.md)

---

*Quick Start Guide - Phase 5 - Version 1.0*  
*Enterprise Gold Lending Platform - NBFCSuite*
