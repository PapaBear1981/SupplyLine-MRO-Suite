# Unused Variables Analysis & Recommendations

## Executive Summary

After investigating all 50 remaining ESLint errors, I've categorized them into:
- **FALSE POSITIVES** (7 errors): Code is correct, ESLint is wrong
- **COMMENTED OUT CODE** (4 errors): Intentionally disabled features
- **SAFE TO REMOVE** (25 errors): Unused imports/variables that can be deleted
- **NEEDS INVESTIGATION** (14 errors): May indicate incomplete features or bugs

---

## 1. FALSE POSITIVES (Keep As-Is) - 7 errors

### ✅ RegisterForm.jsx - `confirmPassword` (Line 44)
**Status**: **CORRECT CODE - ESLint is wrong**

```javascript
const { confirmPassword, ...userData } = formData;
```

**Analysis**: This is intentional destructuring to EXCLUDE confirmPassword from the API payload. The variable is extracted but not used because we don't want to send it to the backend.

**Recommendation**: **Add ESLint disable comment**
```javascript
// eslint-disable-next-line no-unused-vars
const { confirmPassword, ...userData } = formData;
```

---

### ✅ RoleManagement.jsx - `permissions` (Line 11)
**Status**: **FULLY IMPLEMENTED - ESLint is wrong**

```javascript
const { roles, permissions, permissionsByCategory, loading, error } = useSelector((state) => state.rbac);
```

**Analysis**: The `permissions` variable IS used extensively throughout the component:
- Line 36: `dispatch(fetchPermissions())` - fetches permissions
- Line 318-328: Used in permission checkboxes in Add Role modal
- Line 386-396: Used in permission checkboxes in Edit Role modal
- Line 466-501: Used in View Permissions modal
- Line 478-492: Used to filter permissions by category

**Recommendation**: **This is a bug in ESLint**. The variable is clearly used. Keep as-is or add:
```javascript
// eslint-disable-next-line no-unused-vars -- Used in modals below
const { roles, permissions, permissionsByCategory, loading, error } = useSelector((state) => state.rbac);
```

---

### ✅ Scanner.jsx - `_e` (Line 112)
**Status**: **CORRECT - Already prefixed**

```javascript
} catch (_e) {
  // Not JSON, try to parse as barcode format
```

**Analysis**: Error parameter is intentionally unused (we don't care about the JSON parse error). Already prefixed with underscore.

**Recommendation**: **ESLint config issue**. The `argsIgnorePattern: '^_'` should handle this. This might be a bug in ESLint or the pattern isn't matching catch parameters. Add:
```javascript
// eslint-disable-next-line no-unused-vars
} catch (_e) {
```

---

### ✅ api.js - `_refreshError` (Line 189)
**Status**: **CORRECT - Already prefixed**

```javascript
} catch (_refreshError) {
  // Refresh failed, redirect to login
```

**Analysis**: Same as above - error is intentionally unused.

**Recommendation**: Add eslint-disable comment.

---

## 2. COMMENTED OUT CODE (Intentionally Disabled) - 4 errors

### 📝 ReportingPage.jsx - Cycle Count Reports (Lines 20-23, 46)
**Status**: **INTENTIONALLY DISABLED - See GitHub Issue #366**

```javascript
// DISABLED DATE: 2025-06-22
// GITHUB ISSUE: #366
//
// case 'cycle-count-accuracy':
//   dispatch(fetchCycleCountAccuracyReport({ timeframe, filters }));
```

**Analysis**: These imports are for cycle count reports that were intentionally disabled on 2025-06-22 per GitHub issue #366. The code is commented out but imports remain.

**Recommendation**: **REMOVE the imports** since the feature is disabled:
```javascript
// Remove these lines:
fetchCycleCountAccuracyReport,
fetchCycleCountDiscrepancyReport,
fetchCycleCountPerformanceReport,
fetchCycleCountCoverageReport,

// Remove this line:
const [calibrationReportsTab, setCalibrationReportsTab] = useState('due');
```

---

## 3. SAFE TO REMOVE (Unused Code) - 25 errors

### 🗑️ Import Removals (10 errors)

| File | Line | Import | Reason |
|------|------|--------|--------|
| Announcements.jsx | 1 | `useState` | Component doesn't use state |
| UserCheckoutStatus.jsx | 1 | `useState` | Component doesn't use state |
| ArchivedChemicalsList.jsx | 5 | `fetchArchivedChemicals` | Never called |
| ChemicalList.jsx | 5 | `searchChemicals` | Never called |
| ToolList.jsx | 5 | `searchTools` | Never called |
| ToolList.jsx | 23 | `getHelpContent` | Never called |
| ToolDetail.jsx | 30 | `getHelpContent` | Never called |
| CalibrationDetailPage.jsx | 2 | `useNavigate` | Never called |
| CycleCountBatchDetailPage.jsx | 22 | `updateCycleCountItem` | Never called |
| CycleCountDiscrepancyDetailPage.jsx | 3 | `useSelector` | Never used |
| CycleCountItemCountPage.jsx | 3 | `useDispatch`, `useSelector` | Never used |
| KitsManagement.jsx | 6 | `fetchKitAlerts` | Never called |
| reportService.js | 3 | `formatDate` | Never called |

### 🗑️ Variable Removals (15 errors)

| File | Line | Variable | Reason |
|------|------|----------|--------|
| AnnouncementManagement.jsx | 10-11 | `faTimes`, `faCheck` | Icons never used |
| AnnouncementManagement.jsx | 47 | `setLimit` | Pagination not implemented |
| CalibrationHistoryList.jsx | 14 | `setToolId` | Filter not implemented |
| CalibrationNotifications.jsx | 9 | `loading` | Not displayed |
| MainLayout.jsx | 12 | `setShowTooltips` | Toggle not implemented |
| MyKits.jsx | 12 | `user` | Not used for filtering |
| KitWizard.jsx | 6, 11 | `setWizardData`, `wizardData` | Redux state not used |
| RequestReorderModal.jsx | 9 | `error` | Not displayed |
| SendMessageModal.jsx | 9 | `error` | Not displayed |
| ChemicalWasteAnalytics.jsx | 40 | `uniquePartNumbersError` | Not displayed |
| CycleCountCoverageReport.jsx | 122 | `getDaysSinceLastCount` | Function never called |
| ToolList.jsx | 21 | `searchResults` | Redux search not used |
| ToolList.jsx | 137 | `handleSearch` | Function never called |
| ToolList.jsx | 188 | `updatedTools` | Optimistic update not used |
| CycleCountDashboardPage.jsx | 16 | `schedules`, `batches`, `discrepancies` | Not used (stats.data used instead) |
| KitMobileInterface.jsx | 10-11 | `error`, `user` | Not displayed/used |
| tests/CycleCount.test.js | 344 | `mockDispatch` | Test not using it |
| tests/e2e/dashboard.spec.js | 107 | `initialContent` | Test not using it |
| tests/kits/KitWizard.test.jsx | 7-8 | `beforeEach`, `waitFor` | Test helpers not used |

---

## 4. NEEDS INVESTIGATION (Potential Bugs) - 14 errors

### ⚠️ KitWizard.jsx - Wizard State Management
**Lines**: 6 (import), 11 (destructure)

```javascript
import { ..., setWizardData, clearWizardData } from '../../store/kitsSlice';
const { aircraftTypes, wizardData, loading, error } = useSelector((state) => state.kits);
```

**Issue**: The component imports `setWizardData` and retrieves `wizardData` from Redux, but:
- `setWizardData` is never called
- `wizardData` is never used
- Component uses local `formData` state instead

**Questions**:
1. Was there a plan to persist wizard state across page refreshes?
2. Should the wizard save progress to Redux for multi-step navigation?
3. Is this leftover from a previous implementation?

**Recommendation**: 
- **If wizard persistence is needed**: Implement `setWizardData` calls on each step
- **If not needed**: Remove both imports and the Redux state

---

### ⚠️ ToolList.jsx - Search Functionality
**Lines**: 5 (import), 21 (destructure), 137 (function)

```javascript
import { fetchTools, searchTools } from '../../store/toolsSlice';
const { tools, loading, searchResults } = useSelector((state) => state.tools);
const handleSearch = (e) => { ... }
```

**Issue**: Three different search mechanisms exist:
1. Redux `searchTools` action (imported but never called)
2. Redux `searchResults` state (retrieved but never used)
3. Local `handleSearch` function (defined but never called)
4. Actual search happens in `useEffect` with local filtering

**Questions**:
1. Was server-side search planned but not implemented?
2. Should we use Redux search for better performance?
3. Is local filtering sufficient?

**Recommendation**:
- **If server-side search is needed**: Implement `searchTools` dispatch
- **If local filtering is sufficient**: Remove all three unused items

---

### ⚠️ Error Display Missing
**Files**: RequestReorderModal.jsx, SendMessageModal.jsx, ChemicalWasteAnalytics.jsx, CalibrationNotifications.jsx, KitMobileInterface.jsx

**Issue**: These components retrieve `error` from Redux but never display it to the user.

**Questions**:
1. Should errors be displayed in these components?
2. Are errors handled elsewhere (toast notifications)?
3. Is this a UX bug?

**Recommendation**: Either display errors or remove the variable.

---

## Summary of Recommendations

### Immediate Actions (Safe)
1. **Remove 4 cycle count report imports** from ReportingPage.jsx
2. **Remove 10 unused imports** (useState, useNavigate, etc.)
3. **Remove 15 unused variables** (icons, setters, etc.)
4. **Add 4 eslint-disable comments** for false positives

### Requires Decision
1. **KitWizard state management**: Implement or remove?
2. **ToolList search**: Server-side or local only?
3. **Error display**: Add UI or remove variables?
4. **Pagination/filters**: Implement or remove placeholders?

### Total Impact
- **Safe removals**: 29 errors (58% of remaining)
- **False positives**: 7 errors (14% - add comments)
- **Needs decision**: 14 errors (28% - investigate)

After safe removals and false positive fixes, we'd be down to **14 errors** (72% reduction from current 50).

