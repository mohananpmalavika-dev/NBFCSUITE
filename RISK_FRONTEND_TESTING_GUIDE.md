# Risk Management Frontend - Testing Guide

**Version:** 1.0  
**Date:** January 2024  
**Status:** Ready for Testing

---

## 🎯 Testing Objectives

1. Verify all pages render correctly
2. Test CRUD operations
3. Validate form submissions
4. Test data fetching and display
5. Verify navigation and routing
6. Test error handling
7. Verify responsive design

---

## 🧪 Test Cases

### 1. Risk Dashboard (`/risk`)

#### Test Case 1.1: Page Load
- **Steps:**
  1. Navigate to `/risk`
  2. Observe page loading
- **Expected:**
  - ✅ Statistics cards display (4 cards)
  - ✅ Risk distribution chart loads
  - ✅ Module navigation cards (6 cards)
  - ✅ No console errors

#### Test Case 1.2: Navigation
- **Steps:**
  1. Click on "Credit Policies" card
- **Expected:**
  - ✅ Navigates to `/risk/policies`

---

### 2. Credit Policies List (`/risk/policies`)

#### Test Case 2.1: List Display
- **Steps:**
  1. Navigate to `/risk/policies`
- **Expected:**
  - ✅ Table displays policies
  - ✅ Pagination controls visible
  - ✅ Stats cards show counts
  - ✅ Search box visible

#### Test Case 2.2: Search
- **Steps:**
  1. Enter text in search box
  2. Wait for results
- **Expected:**
  - ✅ Table filters in real-time
  - ✅ Results match search term

#### Test Case 2.3: Filter by Status
- **Steps:**
  1. Select "Active Only" from dropdown
- **Expected:**
  - ✅ Table shows only active policies
  - ✅ Count updates

#### Test Case 2.4: Pagination
- **Steps:**
  1. Click "Next" button
- **Expected:**
  - ✅ Next page loads
  - ✅ Page indicator updates
  - ✅ Previous button enables

#### Test Case 2.5: View Details
- **Steps:**
  1. Click "View Details" on any policy
- **Expected:**
  - ✅ Navigates to policy details page
  - ✅ All policy information displayed

#### Test Case 2.6: Delete Policy
- **Steps:**
  1. Click "Delete" on a policy
  2. Confirm deletion
- **Expected:**
  - ✅ Confirmation dialog appears
  - ✅ Policy deleted after confirm
  - ✅ Success toast shows
  - ✅ List refreshes

---

### 3. Create Credit Policy (`/risk/policies/new`)

#### Test Case 3.1: Form Display
- **Steps:**
  1. Click "New Policy" button
- **Expected:**
  - ✅ Form loads with all sections
  - ✅ Default values populated
  - ✅ All fields editable

#### Test Case 3.2: Basic Information
- **Steps:**
  1. Fill in policy code, name, version
  2. Leave required fields empty
  3. Try to submit
- **Expected:**
  - ✅ Validation errors display
  - ✅ Cannot submit with errors
  - ✅ Error messages helpful

#### Test Case 3.3: Product Selection
- **Steps:**
  1. Click on product type badges
  2. Select/deselect multiple
- **Expected:**
  - ✅ Badges toggle selected state
  - ✅ Multiple selection works
  - ✅ Visual feedback clear

#### Test Case 3.4: CIBIL Score Validation
- **Steps:**
  1. Enter CIBIL score < 300
  2. Try to submit
- **Expected:**
  - ✅ Validation error shows
  - ✅ Error message: "Min 300"

#### Test Case 3.5: State Selection
- **Steps:**
  1. Scroll through allowed states
  2. Check multiple states
- **Expected:**
  - ✅ Checkboxes work
  - ✅ Scroll works in container
  - ✅ All states selectable

#### Test Case 3.6: Successful Creation
- **Steps:**
  1. Fill all required fields correctly
  2. Click "Save Policy"
- **Expected:**
  - ✅ Success toast shows
  - ✅ Redirects to policies list
  - ✅ New policy visible in list

---

### 4. Edit Credit Policy (`/risk/policies/[id]/edit`)

#### Test Case 4.1: Data Loading
- **Steps:**
  1. Navigate to edit page
- **Expected:**
  - ✅ Form pre-populated with data
  - ✅ All sections show correct values
  - ✅ Badges show selected items

#### Test Case 4.2: Update Policy
- **Steps:**
  1. Change policy name
  2. Update CIBIL score
  3. Click "Save Changes"
- **Expected:**
  - ✅ Changes saved
  - ✅ Success toast shows
  - ✅ Redirects to list

---

### 5. Policy Details (`/risk/policies/[id]`)

#### Test Case 5.1: Display All Sections
- **Steps:**
  1. Navigate to policy details
- **Expected:**
  - ✅ All sections visible
  - ✅ Data formatted correctly
  - ✅ Badges display properly
  - ✅ Audit trail shows

#### Test Case 5.2: Edit Button
- **Steps:**
  1. Click "Edit Policy"
- **Expected:**
  - ✅ Navigates to edit page

---

### 6. Risk Pricing (`/risk/pricing`)

#### Test Case 6.1: Rules Table
- **Steps:**
  1. Navigate to `/risk/pricing`
- **Expected:**
  - ✅ Pricing rules displayed
  - ✅ Rate adjustments color-coded
  - ✅ Stats cards visible

#### Test Case 6.2: Create Rule
- **Steps:**
  1. Click "New Rule"
  2. Fill in form
  3. Submit
- **Expected:**
  - ✅ Modal opens
  - ✅ Form validation works
  - ✅ Rule created successfully

#### Test Case 6.3: Calculator
- **Steps:**
  1. Click "Calculator"
  2. Enter CIBIL, DTI, Risk Grade
  3. Click "Calculate"
- **Expected:**
  - ✅ Calculator modal opens
  - ✅ Calculation displays
  - ✅ Final rate shown

---

### 7. Exposure Limits (`/risk/exposure`)

#### Test Case 7.1: Utilization Display
- **Steps:**
  1. Navigate to `/risk/exposure`
- **Expected:**
  - ✅ Progress bars show utilization
  - ✅ Colors correct (green/yellow/red)
  - ✅ Percentages accurate

#### Test Case 7.2: Charts
- **Steps:**
  1. View charts
- **Expected:**
  - ✅ Doughnut chart loads
  - ✅ Bar chart loads
  - ✅ Data displays correctly

#### Test Case 7.3: Utilize Exposure
- **Steps:**
  1. Click "Utilize" on a limit
  2. Enter amount
  3. Enter reference
  4. Submit
- **Expected:**
  - ✅ Modal opens
  - ✅ Current limits shown
  - ✅ Amount validated (max available)
  - ✅ Success toast shows
  - ✅ Table updates

#### Test Case 7.4: Release Exposure
- **Steps:**
  1. Click "Release"
  2. Enter amount
  3. Submit
- **Expected:**
  - ✅ Release processed
  - ✅ Utilization decreases

---

### 8. Risk Ratings (`/risk/ratings`)

#### Test Case 8.1: Dashboard Load
- **Steps:**
  1. Navigate to `/risk/ratings`
- **Expected:**
  - ✅ Donut chart shows distribution
  - ✅ Line chart shows PD trend
  - ✅ Bar chart shows breakdown
  - ✅ Stats cards display

#### Test Case 8.2: Filter by Grade
- **Steps:**
  1. Select "A+" from dropdown
- **Expected:**
  - ✅ Table filters to A+ only
  - ✅ Count updates

#### Test Case 8.3: Rating Badges
- **Steps:**
  1. View table
- **Expected:**
  - ✅ Risk grade badges color-coded
  - ✅ Colors match grade severity

---

### 9. Early Warning Alerts (`/risk/alerts`)

#### Test Case 9.1: Alerts Display
- **Steps:**
  1. Navigate to `/risk/alerts`
- **Expected:**
  - ✅ Alerts table loads
  - ✅ Severity badges color-coded
  - ✅ Status badges visible

#### Test Case 9.2: Charts
- **Steps:**
  1. View charts
- **Expected:**
  - ✅ Bar chart (by category) loads
  - ✅ Line chart (trend) loads

#### Test Case 9.3: Take Action
- **Steps:**
  1. Click "Take Action"
  2. Select action type
  3. Enter remarks
  4. Submit
- **Expected:**
  - ✅ Modal opens with alert summary
  - ✅ Action dropdown works
  - ✅ Remarks required
  - ✅ Action recorded
  - ✅ Success toast shows

#### Test Case 9.4: Multiple Filters
- **Steps:**
  1. Select status = "Open"
  2. Select severity = "Critical"
  3. Select category
- **Expected:**
  - ✅ All filters apply together
  - ✅ Table shows correct results

---

## 🔍 Cross-Browser Testing

Test in:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

---

## 📱 Responsive Testing

Test on:
- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

### Expected Behavior:
- Tables should scroll horizontally on mobile
- Cards should stack vertically
- Charts should resize appropriately
- Modals should be full-width on mobile

---

## ⚠️ Error Scenarios

### Test Case E1: Network Error
- **Steps:**
  1. Disconnect network
  2. Try to load a page
- **Expected:**
  - ✅ Error toast shows
  - ✅ Helpful error message
  - ✅ No app crash

### Test Case E2: Invalid Data
- **Steps:**
  1. Enter invalid data in form
  2. Submit
- **Expected:**
  - ✅ Validation errors show
  - ✅ Form not submitted
  - ✅ Specific field errors

### Test Case E3: API Error
- **Steps:**
  1. Trigger API error (e.g., delete non-existent item)
- **Expected:**
  - ✅ Error toast shows
  - ✅ Error message from API displayed
  - ✅ UI remains functional

### Test Case E4: Empty State
- **Steps:**
  1. View page with no data
- **Expected:**
  - ✅ Empty state message shows
  - ✅ Helpful CTA button
  - ✅ No broken UI

---

## 🎨 Visual Testing

### Check:
- [ ] Colors consistent with design system
- [ ] Fonts correct (size, weight)
- [ ] Spacing consistent
- [ ] Icons aligned properly
- [ ] Badges readable
- [ ] Charts legible
- [ ] No overlapping text
- [ ] Proper alignment

---

## ♿ Accessibility Testing

### Test:
- [ ] Keyboard navigation (Tab key)
- [ ] Form labels associated
- [ ] Buttons have accessible names
- [ ] Contrast ratios meet WCAG AA
- [ ] Screen reader compatibility
- [ ] Focus indicators visible
- [ ] Error messages announced

---

## 🚀 Performance Testing

### Metrics to Check:
- [ ] Page load time < 3 seconds
- [ ] Charts render smoothly
- [ ] No layout shifts
- [ ] Smooth scrolling
- [ ] No memory leaks
- [ ] Efficient re-renders

---

## 📋 Test Summary Template

```markdown
## Test Execution Report

**Date:** [Date]
**Tester:** [Name]
**Environment:** [Dev/Staging/Prod]

### Pages Tested
- [ ] Risk Dashboard
- [ ] Credit Policies List
- [ ] Create Policy
- [ ] Edit Policy
- [ ] Policy Details
- [ ] Risk Pricing
- [ ] Exposure Limits
- [ ] Risk Ratings
- [ ] Early Warning Alerts

### Results Summary
- **Total Test Cases:** [Number]
- **Passed:** [Number]
- **Failed:** [Number]
- **Blocked:** [Number]

### Issues Found
1. [Issue description]
2. [Issue description]

### Recommendations
- [Recommendation]
- [Recommendation]
```

---

## 🐛 Bug Reporting Template

```markdown
**Bug Title:** [Short description]

**Severity:** Critical / High / Medium / Low

**Page:** [Page path]

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected Result:**
[What should happen]

**Actual Result:**
[What actually happened]

**Screenshots:**
[Attach screenshots]

**Browser:** [Chrome 120 / Firefox 121 / etc.]
**OS:** [Windows 11 / macOS / etc.]
**Screen Size:** [1920x1080 / etc.]

**Console Errors:**
```
[Paste console errors if any]
```

**Additional Notes:**
[Any other relevant information]
```

---

## ✅ Sign-Off Checklist

Before marking testing complete:

- [ ] All test cases executed
- [ ] All critical bugs fixed
- [ ] All pages load correctly
- [ ] All forms validate properly
- [ ] All CRUD operations work
- [ ] All charts render correctly
- [ ] Navigation works smoothly
- [ ] Error handling works
- [ ] Responsive design verified
- [ ] Cross-browser tested
- [ ] Accessibility checked
- [ ] Performance acceptable
- [ ] Documentation reviewed

---

## 📞 Support

**For Testing Issues:**
- Check browser console for errors
- Verify API is running and accessible
- Check network tab for failed requests
- Review `RISK_FRONTEND_IMPLEMENTATION_COMPLETE.md`

**For Bug Reports:**
- Use bug template above
- Include screenshots
- Provide detailed steps
- Note browser and OS

---

**Happy Testing! 🎉**

*Remember: Quality testing ensures quality product!*
