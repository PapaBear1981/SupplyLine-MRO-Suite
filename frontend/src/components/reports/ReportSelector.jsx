import { useState, useEffect } from 'react';
import { Form, Row, Col, Button } from 'react-bootstrap';
import { useSelector } from 'react-redux';

const ReportSelector = ({
  currentReport,
  timeframe,
  filters,
  onReportTypeChange,
  onTimeframeChange,
  onFilterChange
}) => {
  const [localFilters, setLocalFilters] = useState(filters || {});
  const { tools } = useSelector((state) => state.tools);
  const { users } = useSelector((state) => state.users);
  
  // Update local filters when props change
  useEffect(() => {
    setLocalFilters(filters || {});
  }, [filters]);
  
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setLocalFilters((prev) => ({
      ...prev,
      [name]: value
    }));
  };
  
  const applyFilters = () => {
    onFilterChange(localFilters);
  };
  
  const resetFilters = () => {
    setLocalFilters({});
    onFilterChange({});
  };
  
  // Get unique categories from tools
  const categories = tools ? 
    [...new Set(tools.map(tool => tool.category || 'General'))] : 
    ['General', 'CL415', 'RJ85', 'Q400', 'Engine', 'CNC', 'Sheetmetal'];
  
  // Get unique departments from users
  const departments = users ? 
    [...new Set(users.map(user => user.department))] : 
    ['Maintenance', 'Materials', 'Engineering', 'Management'];
  
  return (
    <div>
      <Row className="mb-3">
        <Col md={4}>
          <Form.Group>
            <Form.Label>Report Type</Form.Label>
            <Form.Select
              value={currentReport}
              onChange={(e) => onReportTypeChange(e.target.value)}
            >
              <option value="tool-inventory">Tool Inventory</option>
              <option value="checkout-history">Checkout History</option>
              <option value="department-usage">Department Usage</option>
            </Form.Select>
          </Form.Group>
        </Col>
        
        <Col md={4}>
          <Form.Group>
            <Form.Label>Time Period</Form.Label>
            <Form.Select
              value={timeframe}
              onChange={(e) => onTimeframeChange(e.target.value)}
              disabled={currentReport === 'tool-inventory'}
            >
              <option value="week">Last Week</option>
              <option value="month">Last Month</option>
              <option value="quarter">Last Quarter</option>
              <option value="year">Last Year</option>
              <option value="all">All Time</option>
            </Form.Select>
          </Form.Group>
        </Col>
      </Row>
      
      <h5 className="mt-4 mb-3">Filters</h5>
      
      {currentReport === 'tool-inventory' && (
        <Row className="mb-3">
          <Col md={4}>
            <Form.Group>
              <Form.Label>Category</Form.Label>
              <Form.Select
                name="category"
                value={localFilters.category || ''}
                onChange={handleFilterChange}
              >
                <option value="">All Categories</option>
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
          </Col>
          
          <Col md={4}>
            <Form.Group>
              <Form.Label>Status</Form.Label>
              <Form.Select
                name="status"
                value={localFilters.status || ''}
                onChange={handleFilterChange}
              >
                <option value="">All Statuses</option>
                <option value="available">Available</option>
                <option value="checked_out">Checked Out</option>
                <option value="maintenance">In Maintenance</option>
                <option value="retired">Retired</option>
              </Form.Select>
            </Form.Group>
          </Col>
          
          <Col md={4}>
            <Form.Group>
              <Form.Label>Location</Form.Label>
              <Form.Control
                type="text"
                name="location"
                value={localFilters.location || ''}
                onChange={handleFilterChange}
                placeholder="Filter by location"
              />
            </Form.Group>
          </Col>
        </Row>
      )}
      
      {currentReport === 'checkout-history' && (
        <Row className="mb-3">
          <Col md={4}>
            <Form.Group>
              <Form.Label>Department</Form.Label>
              <Form.Select
                name="department"
                value={localFilters.department || ''}
                onChange={handleFilterChange}
              >
                <option value="">All Departments</option>
                {departments.map((department) => (
                  <option key={department} value={department}>
                    {department}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
          </Col>
          
          <Col md={4}>
            <Form.Group>
              <Form.Label>Status</Form.Label>
              <Form.Select
                name="checkoutStatus"
                value={localFilters.checkoutStatus || ''}
                onChange={handleFilterChange}
              >
                <option value="">All</option>
                <option value="active">Currently Checked Out</option>
                <option value="returned">Returned</option>
              </Form.Select>
            </Form.Group>
          </Col>
          
          <Col md={4}>
            <Form.Group>
              <Form.Label>Tool Category</Form.Label>
              <Form.Select
                name="toolCategory"
                value={localFilters.toolCategory || ''}
                onChange={handleFilterChange}
              >
                <option value="">All Categories</option>
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
          </Col>
        </Row>
      )}
      
      <div className="d-flex justify-content-end mt-3">
        <Button 
          variant="outline-secondary" 
          className="me-2"
          onClick={resetFilters}
        >
          Reset Filters
        </Button>
        <Button 
          variant="primary"
          onClick={applyFilters}
        >
          Apply Filters
        </Button>
      </div>
    </div>
  );
};

export default ReportSelector;
