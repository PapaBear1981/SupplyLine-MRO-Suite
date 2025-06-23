# Cycle Count Technical Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Database Schema](#database-schema)
3. [API Documentation](#api-documentation)
4. [Component Documentation](#component-documentation)
5. [Redux State Management](#redux-state-management)
6. [Performance Considerations](#performance-considerations)
7. [Security Implementation](#security-implementation)
8. [Testing Strategy](#testing-strategy)

## Architecture Overview

### System Components
The cycle count functionality is built using a modern web architecture:

```
Frontend (React/Redux) ↔ Backend (Flask/SQLAlchemy) ↔ Database (SQLite)
```

#### Frontend Stack
- **React 18**: Component-based UI framework
- **Redux Toolkit**: State management
- **React Router**: Client-side routing
- **Material-UI**: Component library
- **html5-qrcode**: Barcode scanning

#### Backend Stack
- **Flask 2.2**: Web framework
- **SQLAlchemy 1.4**: ORM
- **PyJWT**: JWT authentication
- **Flask-CORS**: Cross-origin requests

#### Database
- **SQLite**: Lightweight database
- **Indexed tables**: Optimized for performance
- **Foreign key constraints**: Data integrity

### Data Flow
1. **User Interaction**: React components dispatch Redux actions
2. **API Calls**: Redux thunks make HTTP requests to Flask backend
3. **Data Processing**: Flask routes process requests and interact with database
4. **Response Handling**: Frontend updates state and re-renders components

## Database Schema

### Core Tables

#### cycle_count_schedules
```sql
CREATE TABLE cycle_count_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    frequency TEXT NOT NULL,  -- daily, weekly, monthly, quarterly, annual
    method TEXT NOT NULL,     -- ABC, random, location, category
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

#### cycle_count_batches
```sql
CREATE TABLE cycle_count_batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL,     -- draft, active, review, completed, archived
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (schedule_id) REFERENCES cycle_count_schedules(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

#### cycle_count_items
```sql
CREATE TABLE cycle_count_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL,
    item_type TEXT NOT NULL,  -- tool, chemical
    item_id INTEGER NOT NULL,
    expected_quantity REAL,
    expected_location TEXT,
    assigned_to INTEGER,
    status TEXT NOT NULL,     -- pending, counted, skipped
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES cycle_count_batches(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id)
);
```

#### cycle_count_results
```sql
CREATE TABLE cycle_count_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    counted_by INTEGER NOT NULL,
    counted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actual_quantity REAL,
    actual_location TEXT,
    condition TEXT,
    notes TEXT,
    has_discrepancy BOOLEAN DEFAULT 0,
    discrepancy_type TEXT,    -- quantity, location, condition, missing, extra
    discrepancy_notes TEXT,
    FOREIGN KEY (item_id) REFERENCES cycle_count_items(id),
    FOREIGN KEY (counted_by) REFERENCES users(id)
);
```

#### cycle_count_adjustments
```sql
CREATE TABLE cycle_count_adjustments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id INTEGER NOT NULL,
    approved_by INTEGER NOT NULL,
    approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    adjustment_type TEXT NOT NULL,  -- quantity, location, condition, status
    old_value TEXT,
    new_value TEXT,
    notes TEXT,
    FOREIGN KEY (result_id) REFERENCES cycle_count_results(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);
```

### Indexes for Performance
```sql
-- Single column indexes
CREATE INDEX idx_cycle_count_schedules_is_active ON cycle_count_schedules(is_active);
CREATE INDEX idx_cycle_count_batches_status ON cycle_count_batches(status);
CREATE INDEX idx_cycle_count_items_batch_id ON cycle_count_items(batch_id);
CREATE INDEX idx_cycle_count_results_item_id ON cycle_count_results(item_id);

-- Composite indexes
CREATE INDEX idx_cycle_count_items_batch_status ON cycle_count_items(batch_id, status);
CREATE INDEX idx_cycle_count_items_type_id ON cycle_count_items(item_type, item_id);
CREATE INDEX idx_cycle_count_results_discrepancy ON cycle_count_results(has_discrepancy, discrepancy_type);
```

### Relationships
- **Schedules → Batches**: One-to-many
- **Batches → Items**: One-to-many
- **Items → Results**: One-to-many
- **Results → Adjustments**: One-to-many
- **Users → Schedules**: Many-to-one (creator)
- **Users → Items**: Many-to-one (assignee)

## API Documentation

### Authentication
All API endpoints require authentication via JWT tokens provided in the Authorization header.

```python
@require_auth
def protected_route():
    # Route implementation
```

### Base URL
```
/api/cycle-count/
```

### Endpoints

#### Schedules

**GET /api/cycle-count/schedules**
- Description: Retrieve all cycle count schedules
- Parameters: None
- Response: Array of schedule objects

**POST /api/cycle-count/schedules**
- Description: Create a new schedule
- Body: Schedule object
- Response: Created schedule object

**GET /api/cycle-count/schedules/{id}**
- Description: Get specific schedule
- Parameters: schedule ID
- Response: Schedule object with batches

**PUT /api/cycle-count/schedules/{id}**
- Description: Update schedule
- Body: Updated schedule fields
- Response: Updated schedule object

**DELETE /api/cycle-count/schedules/{id}**
- Description: Delete schedule
- Parameters: schedule ID
- Response: Success message

#### Batches

**GET /api/cycle-count/batches**
- Description: Retrieve all batches
- Parameters: Optional schedule_id filter
- Response: Array of batch objects

**POST /api/cycle-count/batches**
- Description: Create new batch
- Body: Batch object
- Response: Created batch object

**GET /api/cycle-count/batches/{id}**
- Description: Get specific batch
- Parameters: batch ID
- Response: Batch object with items

**PUT /api/cycle-count/batches/{id}**
- Description: Update batch
- Body: Updated batch fields
- Response: Updated batch object

**POST /api/cycle-count/batches/{id}/generate-items**
- Description: Generate items for batch
- Body: Generation parameters
- Response: Generated items count

#### Items

**GET /api/cycle-count/batches/{batch_id}/items**
- Description: Get items for batch
- Parameters: batch ID, optional filters
- Response: Array of item objects

**GET /api/cycle-count/items/assigned**
- Description: Get user's assigned items
- Parameters: Optional status filter
- Response: Array of assigned items

**POST /api/cycle-count/items/{id}/count**
- Description: Submit count result
- Body: Count result data
- Response: Created result object

#### Analytics

**GET /api/cycle-count/analytics/summary**
- Description: Get summary analytics
- Parameters: Optional date range
- Response: Analytics summary object

**GET /api/cycle-count/analytics/performance**
- Description: Get performance metrics
- Parameters: Optional filters
- Response: Performance data

### Error Handling
All endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

Common HTTP status codes:
- **200**: Success
- **201**: Created
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **500**: Internal Server Error

## Component Documentation

### Component Hierarchy
```
CycleCountDashboard
├── CycleCountStatsOverview
├── CycleCountScheduleList
│   └── CycleCountScheduleCard
├── CycleCountBatchList
│   └── CycleCountBatchCard
└── CycleCountAdvancedAnalytics
    ├── AccuracyTrendChart
    ├── DiscrepancyTypeChart
    └── CoverageMetricsChart
```

### Key Components

#### CycleCountDashboard
**Purpose**: Main dashboard for cycle count functionality
**Props**: None
**State**: Connected to Redux store
**Features**:
- Overview statistics
- Schedule management
- Batch monitoring
- Analytics visualization

#### CycleCountScheduleForm
**Purpose**: Create/edit cycle count schedules
**Props**:
- `schedule`: Existing schedule for editing (optional)
- `onSubmit`: Callback function for form submission
- `onCancel`: Callback function for cancellation

**Validation**:
- Name: Required, max 100 characters
- Frequency: Required, predefined values
- Method: Required, predefined values

#### CycleCountBatchForm
**Purpose**: Create/edit cycle count batches
**Props**:
- `batch`: Existing batch for editing (optional)
- `schedules`: Available schedules
- `onSubmit`: Callback function
- `onCancel`: Callback function

#### MobileCycleCountBatch
**Purpose**: Mobile-optimized counting interface
**Props**:
- `batchId`: ID of the batch to count
- `onItemCounted`: Callback for completed counts

**Features**:
- Touch-friendly interface
- Barcode scanning
- Offline capability
- Photo capture

### Component Best Practices
- **Prop Validation**: Use PropTypes for type checking
- **Error Boundaries**: Wrap components in error boundaries
- **Loading States**: Show loading indicators during API calls
- **Accessibility**: Include ARIA labels and keyboard navigation
- **Responsive Design**: Support mobile and desktop layouts

## Redux State Management

### State Structure
```javascript
{
  cycleCount: {
    schedules: {
      items: [],
      loading: false,
      error: null
    },
    batches: {
      items: [],
      loading: false,
      error: null
    },
    items: {
      byBatchId: {},
      loadingByBatchId: {},
      errorByBatchId: {}
    },
    analytics: {
      data: null,
      loading: false,
      error: null
    }
  }
}
```

### Actions
- **fetchSchedules**: Load all schedules
- **createSchedule**: Create new schedule
- **updateSchedule**: Update existing schedule
- **deleteSchedule**: Remove schedule
- **fetchBatches**: Load batches
- **createBatch**: Create new batch
- **fetchBatchItems**: Load items for batch
- **submitCountResult**: Submit count result
- **fetchAnalytics**: Load analytics data

### Async Thunks
```javascript
export const fetchSchedules = createAsyncThunk(
  'cycleCount/fetchSchedules',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/cycle-count/schedules');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);
```

### Selectors
```javascript
// Get active schedules
export const selectActiveSchedules = createSelector(
  [state => state.cycleCount.schedules.items],
  schedules => schedules.filter(schedule => schedule.is_active)
);

// Get batch items by batch ID
export const selectBatchItems = (batchId) => createSelector(
  [state => state.cycleCount.items.byBatchId],
  itemsByBatch => itemsByBatch[batchId] || []
);
```

## Performance Considerations

### Database Optimization
1. **Indexes**: Comprehensive indexing strategy implemented
2. **Query Optimization**: Efficient queries with proper joins
3. **Pagination**: Large datasets paginated to reduce load
4. **Caching**: Redis caching for frequently accessed data

### Frontend Optimization
1. **Code Splitting**: Lazy loading of components
2. **Memoization**: React.memo and useMemo for expensive operations
3. **Virtual Scrolling**: For large item lists
4. **Image Optimization**: Compressed images and lazy loading

### API Optimization
1. **Response Compression**: Gzip compression enabled
2. **Efficient Serialization**: Optimized JSON responses
3. **Rate Limiting**: Prevent API abuse
4. **Connection Pooling**: Database connection optimization

## Security Implementation

### Authentication & Authorization
- **JWT-Based Auth**: Stateless authentication using access and refresh tokens
- **Role-based Access**: Different permissions by user role
- **CSRF Protection**: Cross-site request forgery prevention
- **Input Validation**: Comprehensive input sanitization

### Data Protection
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: HTML escaping and CSP headers
- **Secure Headers**: Security-focused HTTP headers
- **Audit Logging**: Complete audit trail for all actions

## Testing Strategy

### Backend Testing
- **Unit Tests**: Individual function testing
- **Integration Tests**: API endpoint testing
- **Database Tests**: Model and migration testing
- **Performance Tests**: Load and stress testing

### Frontend Testing
- **Component Tests**: React component testing
- **Redux Tests**: State management testing
- **Integration Tests**: User workflow testing
- **E2E Tests**: Complete application testing

### Test Coverage Goals
- **Backend**: 90%+ code coverage
- **Frontend**: 85%+ code coverage
- **Critical Paths**: 100% coverage for core functionality

---

*This technical documentation is maintained by the development team and updated with each release.*
