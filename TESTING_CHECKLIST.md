# Kit Transfer System - Comprehensive Testing Checklist

## Prerequisites
- ✅ Backend server running on http://localhost:5000
- ✅ Frontend server running on http://localhost:5173
- ✅ Database cleaned of bad data
- ✅ Fix applied to `backend/routes_kit_transfers.py`

## Test Scenarios

### 1. Kit-to-Kit Chemical Transfer (Full Quantity)

**Setup:**
- Kit 1 (Boeing 737) has chemical PR-1440-B2 LOT-2024-002-A (Qty: 1)
- Kit 2 (Airbus A320) is the destination

**Steps:**
1. Navigate to Kit Boeing 737 - 001
2. Go to "Items" tab
3. Find chemical PR-1440-B2 LOT-2024-002-A
4. Click "Transfer" button
5. Select destination: Kit Airbus A320 - 001
6. Select destination box
7. Enter quantity: 1
8. Click "Submit"

**Expected Results:**
- ✅ Transfer completes successfully
- ✅ Item is removed from Boeing 737 kit
- ✅ Item appears in Airbus A320 kit with correct lot number (LOT-2024-002-A)
- ✅ No random chemicals appear in Airbus kit
- ✅ Transfer history shows correct item details

**Verification:**
- Check Boeing 737 Items tab: PR-1440-B2 LOT-2024-002-A should be gone
- Check Airbus A320 Items tab: PR-1440-B2 LOT-2024-002-A should appear
- Check Transfers tab: Transfer record should show correct chemical

---

### 2. Kit-to-Kit Chemical Transfer (Partial Quantity)

**Setup:**
- Kit 1 has chemical CHEM001 LOT001-A (Qty: 1)
- Transfer only partial quantity (not applicable for qty=1, skip this test)

**Note:** This test requires a chemical with quantity > 1. If not available, skip.

---

### 3. Kit-to-Kit Tool Transfer

**Setup:**
- Add a tool to Kit 1 from warehouse
- Transfer it to Kit 2

**Steps:**
1. Navigate to Kit Boeing 737 - 001
2. Add a tool from warehouse (if not already present)
3. Click "Transfer" on the tool
4. Select destination: Kit Airbus A320 - 001
5. Complete transfer

**Expected Results:**
- ✅ Tool is removed from Kit 1
- ✅ Tool appears in Kit 2 with correct serial number
- ✅ Transfer history is accurate

---

### 4. Warehouse-to-Kit Chemical Transfer

**Setup:**
- Warehouse has chemical CHEM001 LOT001 (Qty: 6)
- Transfer to Kit 1

**Steps:**
1. Navigate to Kit Boeing 737 - 001
2. Click "Add Item" or use transfer interface
3. Select warehouse as source
4. Select chemical CHEM001 LOT001
5. Enter quantity: 2
6. Complete transfer

**Expected Results:**
- ✅ New child lot created (e.g., LOT001-D)
- ✅ Child lot appears in Kit 1
- ✅ Parent lot quantity reduced by 2 in warehouse
- ✅ Parent lot remains in warehouse

---

### 5. Kit-to-Warehouse Transfer (Return)

**Setup:**
- Kit 1 has a chemical
- Return it to warehouse

**Steps:**
1. Navigate to Kit Boeing 737 - 001
2. Select a chemical item
3. Click "Transfer"
4. Select destination: Warehouse
5. Complete transfer

**Expected Results:**
- ✅ Item removed from kit
- ✅ Chemical's warehouse_id updated to destination warehouse
- ✅ Transfer history accurate

---

### 6. Multiple Transfers in Sequence

**Setup:**
- Transfer item from Kit 1 → Kit 2
- Then transfer same item from Kit 2 → Kit 1

**Steps:**
1. Transfer chemical from Boeing 737 to Airbus A320
2. Verify it appears in Airbus A320
3. Transfer the same chemical back from Airbus A320 to Boeing 737
4. Verify it appears back in Boeing 737

**Expected Results:**
- ✅ Item moves correctly in both directions
- ✅ Lot numbers preserved throughout
- ✅ No duplicate items created
- ✅ Transfer history shows both transfers

---

### 7. Tab Updates After Transfer

**Test all tabs update correctly after a transfer:**

**Steps:**
1. Perform a kit-to-kit transfer
2. Check all tabs in both kits

**Tabs to verify:**
- ✅ **Items Tab**: Shows updated inventory
- ✅ **Transfers Tab**: Shows new transfer record
- ✅ **Overview Tab**: Shows updated item counts
- ✅ **Boxes Tab**: Shows correct item counts per box

---

### 8. Edge Cases

#### 8.1 Transfer with Invalid Quantity
**Steps:**
1. Try to transfer more than available quantity
2. Verify error message appears

**Expected:**
- ✅ Error: "Insufficient quantity"

#### 8.2 Transfer to Same Kit
**Steps:**
1. Try to transfer item to the same kit it's already in
2. Verify appropriate handling

**Expected:**
- ✅ Either prevented or handled gracefully

#### 8.3 Transfer Without Selecting Box
**Steps:**
1. Initiate transfer without selecting destination box
2. Verify default box is used or error shown

**Expected:**
- ✅ Uses first box or shows error

---

## Database Verification

After each transfer, you can verify the database state using:

```bash
python backend/debug_transfers.py
```

**Check for:**
- ✅ No KitItems pointing to chemicals with warehouse_id != None
- ✅ Transfer records have correct item_id (Chemical/Tool ID, not KitItem ID)
- ✅ Lot numbers match between KitItem and Chemical records

---

## Known Issues (Fixed)

### ✅ FIXED: Items not appearing in destination kit
**Cause:** Backend was using KitItem ID instead of Chemical ID
**Fix:** Use `source_item.item_id` for kit-to-kit transfers

### ✅ FIXED: Random chemicals appearing
**Cause:** Wrong item_id caused lookup of wrong chemical
**Fix:** Correct item_id resolution logic

### ✅ FIXED: Warehouse chemicals in kits
**Cause:** KitItems pointing to chemicals still marked as in warehouse
**Fix:** Proper item_id handling + database cleanup

---

## Regression Testing

After confirming all tests pass, verify these existing features still work:

- ✅ Adding items from warehouse to kit
- ✅ Issuing items from kit
- ✅ Kit creation wizard
- ✅ Kit reorder management
- ✅ Kit reports and analytics
- ✅ Kit messaging

---

## Performance Testing

For large kits (100+ items):
- ✅ Transfer completes in reasonable time (< 5 seconds)
- ✅ UI remains responsive
- ✅ No memory leaks or performance degradation

---

## Browser Compatibility

Test in:
- ✅ Chrome
- ✅ Firefox
- ✅ Edge
- ✅ Safari (if available)

---

## Sign-off

Once all tests pass:
- [ ] All test scenarios completed
- [ ] No regressions found
- [ ] Database verified clean
- [ ] Documentation updated
- [ ] Ready for production deployment

**Tested by:** _________________
**Date:** _________________
**Signature:** _________________

