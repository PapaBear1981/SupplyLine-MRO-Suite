# Concurrent User Testing Guide

This guide explains how to run and interpret concurrent user tests that simulate multiple users operating the application simultaneously.

## Overview

The concurrent testing suite simulates 3-10 users performing operations at the same time to test:
- **Race conditions**: Multiple users trying to modify the same resource
- **Collision handling**: How the system prevents conflicts (e.g., two users checking out the same tool)
- **Data consistency**: Ensuring inventory quantities and records remain accurate
- **Performance**: How the application handles concurrent load
- **Locking mechanisms**: Verifying database locks work correctly

## Test Files

### 1. `concurrent-checkouts.spec.js`
Tests concurrent tool checkout operations:
- ✅ 3 users trying to checkout the same tool simultaneously (only 1 should succeed)
- ✅ 5 users with staggered checkout attempts
- ✅ Concurrent checkout and return operations on the same tool

**What it tests:**
- Tool availability locking
- Checkout collision prevention
- Status updates during concurrent operations

### 2. `concurrent-chemicals.spec.js`
Tests concurrent chemical issuance operations:
- ✅ 3 users issuing from the same chemical lot simultaneously
- ✅ Over-issuance prevention (4 users requesting from a lot with only 2-3 units)
- ✅ Staggered issuances with quantity tracking

**What it tests:**
- Quantity tracking accuracy
- Prevention of over-issuance
- Inventory consistency after concurrent operations
- Race condition handling in quantity updates

### 3. `concurrent-calibrations.spec.js`
Tests concurrent calibrations and inventory updates:
- ✅ Multiple users adding calibrations to the same tool
- ✅ Concurrent kit transfers
- ✅ Concurrent API requests
- ✅ Rapid successive updates and navigation

**What it tests:**
- Multiple calibrations per tool (should all succeed)
- Kit access during concurrent operations
- API rate limiting and concurrent request handling
- Data consistency during rapid navigation

## Running the Tests

### Prerequisites

1. **Backend must be running:**
   ```bash
   # From project root
   cd backend
   python run.py
   ```

2. **Frontend dev server must be running:**
   ```bash
   # From project root
   cd frontend
   npm run dev
   ```

3. **Docker containers (alternative):**
   ```bash
   # From project root
   docker-compose up
   ```

### Run All Concurrent Tests

```bash
# From frontend directory
npx playwright test concurrent-*.spec.js
```

### Run Specific Test Suites

```bash
# Tool checkout tests only
npx playwright test concurrent-checkouts.spec.js

# Chemical issuance tests only
npx playwright test concurrent-chemicals.spec.js

# Calibration and inventory tests only
npx playwright test concurrent-calibrations.spec.js
```

### Run with UI Mode (Recommended for Debugging)

```bash
npx playwright test concurrent-*.spec.js --ui
```

### Run in Headed Mode (See Browsers)

```bash
npx playwright test concurrent-*.spec.js --headed
```

### Run with Specific Browser

```bash
# Chromium only
npx playwright test concurrent-*.spec.js --project=chromium

# Firefox only
npx playwright test concurrent-*.spec.js --project=firefox
```

## Understanding Test Results

### Success Criteria

Each test validates specific behaviors:

#### Tool Checkouts
- **Expected**: Only 1 user succeeds when 3 try to checkout the same tool
- **Pass**: `successCount = 1, failureCount = 2`
- **Fail**: Multiple users succeed (race condition not handled)

#### Chemical Issuance
- **Expected**: Quantity decreases by exactly the number of successful issuances
- **Pass**: `finalQty = initialQty - successCount`
- **Fail**: Quantity mismatch (indicates race condition in quantity tracking)

#### Over-Issuance Prevention
- **Expected**: System prevents issuing more than available
- **Pass**: `successCount <= availableQty`
- **Fail**: More issuances than available quantity

#### Calibrations
- **Expected**: All calibrations succeed (multiple allowed per tool)
- **Pass**: `successCount = userCount`
- **Fail**: Some calibrations fail unexpectedly

### Test Output

Tests output detailed analysis:

```json
{
  "totalOperations": 3,
  "successCount": 1,
  "failureCount": 2,
  "successRate": "33.33%",
  "totalDuration": 2543,
  "avgDuration": "847.67",
  "maxDuration": 1023,
  "minDuration": 654,
  "uniqueErrors": ["Tool already checked out"],
  "errorBreakdown": [
    {
      "error": "Tool already checked out",
      "count": 2
    }
  ]
}
```

## Common Issues and Solutions

### Issue: All users succeed when only 1 should

**Problem**: Race condition in checkout logic - no locking mechanism

**Solution**: Implement database-level locking or optimistic concurrency control

**Example Fix**:
```python
# In backend checkout endpoint
tool = Tool.query.with_for_update().get(tool_id)  # Row-level lock
if tool.status != 'Available':
    return {'error': 'Tool not available'}, 409
```

### Issue: Quantity becomes negative

**Problem**: Race condition in quantity updates

**Solution**: Use atomic updates or database constraints

**Example Fix**:
```python
# Atomic update
Chemical.query.filter_by(id=chem_id).update({
    'quantity': Chemical.quantity - issued_qty
})
db.session.commit()

# Add constraint
__table_args__ = (
    CheckConstraint('quantity >= 0', name='check_quantity_positive'),
)
```

### Issue: Inconsistent final quantities

**Problem**: Lost updates due to concurrent modifications

**Solution**: Use optimistic locking with version numbers

**Example Fix**:
```python
class Chemical(db.Model):
    version = db.Column(db.Integer, default=0)
    
    def issue(self, qty):
        current_version = self.version
        self.quantity -= qty
        self.version += 1
        
        # Update with version check
        rows = db.session.query(Chemical).filter(
            Chemical.id == self.id,
            Chemical.version == current_version
        ).update({'quantity': self.quantity, 'version': self.version})
        
        if rows == 0:
            raise ConcurrentModificationError()
```

## Performance Benchmarks

Expected performance for concurrent operations:

| Operation | Users | Expected Duration | Max Acceptable |
|-----------|-------|-------------------|----------------|
| Tool Checkout | 3 | < 3s | < 5s |
| Chemical Issuance | 3 | < 3s | < 5s |
| Calibration Add | 3 | < 4s | < 6s |
| API Requests | 5 | < 2s | < 4s |

If tests exceed max acceptable duration, investigate:
- Database query optimization
- Index creation
- Connection pool sizing
- API response caching

## Extending the Tests

### Add More Users

```javascript
const userCount = 10; // Increase from 3
const contexts = await createConcurrentUsers(userCount);
```

### Add Custom Operations

```javascript
const operations = contexts.map(({ page, user }) => async () => {
  // Your custom concurrent operation
  await page.goto('/your-page');
  // ... perform actions
});

const results = await executeConcurrently(operations);
```

### Test Different Timing Patterns

```javascript
// Simultaneous (all at once)
await executeConcurrently(operations);

// Staggered (100ms apart)
await executeStaggered(operations, 100);

// Custom timing with barrier
const barrier = new ConcurrencyBarrier(userCount);
await barrier.wait(); // All users wait here until all arrive
```

## Continuous Integration

Add to your CI pipeline:

```yaml
# .github/workflows/concurrent-tests.yml
name: Concurrent Tests

on: [push, pull_request]

jobs:
  concurrent-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
      - name: Install dependencies
        run: cd frontend && npm ci
      - name: Install Playwright
        run: cd frontend && npx playwright install --with-deps
      - name: Start backend
        run: cd backend && python run.py &
      - name: Run concurrent tests
        run: cd frontend && npx playwright test concurrent-*.spec.js
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: concurrent-test-results
          path: frontend/test-results/
```

## Best Practices

1. **Always clean up**: Tests use `cleanupConcurrentUsers()` in `finally` blocks
2. **Use barriers**: Synchronize users with `ConcurrencyBarrier` for true simultaneous operations
3. **Analyze results**: Use `analyzeResults()` to get detailed metrics
4. **Test edge cases**: Test with limited resources (e.g., 2 units, 4 users)
5. **Monitor performance**: Track test duration to catch performance regressions
6. **Test realistic scenarios**: Mix simultaneous and staggered operations

## Troubleshooting

### Tests timeout
- Increase timeout in test: `test.setTimeout(120000)` (120 seconds)
- Check backend is running and responsive
- Verify database is not locked

### Inconsistent results
- Add delays between operations: `await page.waitForTimeout(1000)`
- Use barriers to ensure true simultaneity
- Check for timing-dependent bugs

### Browser crashes
- Reduce concurrent user count
- Run tests serially: `test.describe.configure({ mode: 'serial' })`
- Increase system resources

## Support

For issues or questions:
1. Check test output and error messages
2. Run with `--debug` flag for verbose logging
3. Use `--ui` mode to step through tests
4. Review backend logs for API errors

