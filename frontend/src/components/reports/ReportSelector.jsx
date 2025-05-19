import { useState, useEffect } from 'react';
import { Form, Row, Col, Button } from 'react-bootstrap';
import { useSelector } from 'react-redux';
import Tooltip from '../common/Tooltip';
import HelpIcon from '../common/HelpIcon';
import { useHelp } from '../../context/HelpContext';

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
  const { showTooltips, showHelp } = useHelp();

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
  const [categories, setCategories] = useState(['General', 'CL415', 'RJ85', 'Q400', 'Engine', 'CNC', 'Sheetmetal']);

  // Update categories when tools change
  useEffect(() => {
    if (tools && tools.length > 0) {
      const uniqueCategories = [...new Set(tools.map(tool => tool.category || 'General'))];
      setCategories(uniqueCategories.sort());
      console.log('Updated categories:', uniqueCategories);
    }
  }, [tools]);

  // Get unique departments from users
  const departments = users ?
    [...new Set(users.map(user => user.department))] :
    ['Maintenance', 'Materials', 'Engineering', 'Management'];

  return (
    <div>
      {showHelp && (
        <div className="mb-3">
          <HelpIcon
            title="Report Options"
            content={
              <>
                <p>Use these options to configure and generate reports:</p>
                <ul>
                  <li><strong>Report Type:</strong> Select the type of report you want to generate.</li>
                  <li><strong>Time Period:</strong> Choose the time range for your report data.</li>
                  <li><strong>Filters:</strong> Narrow down your report results using various filters.</li>
                  <li><strong>Apply Filters:</strong> Click this button to generate the report with your selected options.</li>
                </ul>
              </>
            }
            size="sm"
          />
        </div>
      )}

      <Row className="mb-3">
        <Col md={4}>
          <Form.Group>
            <div className="d-flex align-items-center mb-1">
              <Form.Label className="mb-0">Report Type</Form.Label>
              {showHelp && (
                <HelpIcon
                  title="Report Type"
                  content="Select the type of report you want to generate. Each report type provides different information and visualization options."
                  size="sm"
                />
              )}
            </div>
            <Tooltip text="Select the type of report to generate" placement="top" show={showTooltips}>
              <Form.Select
                value={currentReport}
                onChange={(e) => onReportTypeChange(e.target.value)}
              >
                <option value="tool-inventory">Tool Inventory</option>
                <option value="checkout-history">Checkout History</option>
                <option value="department-usage">Department Usage</option>
              </Form.Select>
            </Tooltip>
          </Form.Group>
        </Col>

        <Col md={4}>
          <Form.Group>
            <div className="d-flex align-items-center mb-1">
              <Form.Label className="mb-0">Time Period</Form.Label>
              {showHelp && (
                <HelpIcon
                  title="Time Period"
                  content="Select the time range for your report data. This option is disabled for Tool Inventory reports since they show current inventory status."
                  size="sm"
                />
              )}
            </div>
            <Tooltip
              text={currentReport === 'tool-inventory' ?
                "Time period not applicable for inventory reports" :
                "Select the time period for your report"}
              placement="top"
              show={showTooltips}
            >
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
            </Tooltip>
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
        <Tooltip text="Clear all filters" placement="top" show={showTooltips}>
          <Button
            variant="outline-secondary"
            className="me-2"
            onClick={resetFilters}
          >
            Reset Filters
          </Button>
        </Tooltip>
        <Tooltip text="Generate report with selected options" placement="top" show={showTooltips}>
          <Button
            variant="primary"
            onClick={applyFilters}
          >
            Apply Filters
          </Button>
        </Tooltip>
      </div>
    </div>
  );
};

export default ReportSelector;
