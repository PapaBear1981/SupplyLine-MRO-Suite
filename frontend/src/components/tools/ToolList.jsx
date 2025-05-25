import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Table, Button, Form, InputGroup, Card, Row, Col, Collapse, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { fetchTools, searchTools } from '../../store/toolsSlice';
import LoadingSpinner from '../common/LoadingSpinner';
import CheckoutModal from '../checkouts/CheckoutModal';
import ToolBarcode from './ToolBarcode';
import DeleteToolModal from './DeleteToolModal';
import CalibrationStatusIndicator from './CalibrationStatusIndicator';
import Tooltip from '../common/Tooltip';
import HelpIcon from '../common/HelpIcon';
import HelpContent from '../common/HelpContent';
import { useHelp } from '../../context/HelpContext';
import './ToolList.css';

const ToolList = () => {
  const dispatch = useDispatch();
  const { tools, loading, searchResults } = useSelector((state) => state.tools);
  const { user } = useSelector((state) => state.auth);
  const { showTooltips, showHelp, getHelpContent } = useHelp();
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredTools, setFilteredTools] = useState([]);
  const [sortConfig, setSortConfig] = useState({ key: 'tool_number', direction: 'ascending' });
  const [showCheckoutModal, setShowCheckoutModal] = useState(false);
  const [showBarcodeModal, setShowBarcodeModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedTool, setSelectedTool] = useState(null);

  // Filter states
  const [showFilters, setShowFilters] = useState(false);
  const [hideRetired, setHideRetired] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [locationFilter, setLocationFilter] = useState('');

  // Available categories and locations for filtering
  const [availableCategories, setAvailableCategories] = useState([]);
  const [availableLocations, setAvailableLocations] = useState([]);

  useEffect(() => {
    console.log("ToolList: Fetching tools...");
    dispatch(fetchTools())
      .then(result => {
        console.log("ToolList: Fetch tools result:", result);
      })
      .catch(error => {
        console.error("ToolList: Error fetching tools:", error);
      });
  }, [dispatch]);

  // Extract available categories and locations for filtering
  useEffect(() => {
    if (tools && tools.length > 0) {
      // Extract unique categories
      const categories = [...new Set(tools.map(tool => tool.category || 'General').filter(Boolean))];
      setAvailableCategories(categories.sort());

      // Extract unique locations
      const locations = [...new Set(tools.map(tool => tool.location).filter(Boolean))];
      setAvailableLocations(locations.sort());
    }
  }, [tools]);

  useEffect(() => {
    // Filter tools based on search query and filter options
    let toolsToDisplay = [...tools];

    // Apply search query filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      toolsToDisplay = toolsToDisplay.filter(tool =>
        tool.tool_number.toLowerCase().includes(query) ||
        tool.serial_number.toLowerCase().includes(query) ||
        (tool.description && tool.description.toLowerCase().includes(query)) ||
        (tool.location && tool.location.toLowerCase().includes(query))
      );
      console.log(`Filtered to ${toolsToDisplay.length} tools matching "${query}"`);
    }

    // Apply status filter
    if (statusFilter) {
      toolsToDisplay = toolsToDisplay.filter(tool => tool.status === statusFilter);
    }

    // Apply category filter
    if (categoryFilter) {
      toolsToDisplay = toolsToDisplay.filter(tool => (tool.category || 'General') === categoryFilter);
    }

    // Apply location filter
    if (locationFilter) {
      toolsToDisplay = toolsToDisplay.filter(tool => tool.location === locationFilter);
    }

    // Hide retired tools if the option is selected
    if (hideRetired) {
      toolsToDisplay = toolsToDisplay.filter(tool => tool.status !== 'retired');
    }

    // Apply sorting
    const sortedTools = [...toolsToDisplay].sort((a, b) => {
      if (a[sortConfig.key] < b[sortConfig.key]) {
        return sortConfig.direction === 'ascending' ? -1 : 1;
      }
      if (a[sortConfig.key] > b[sortConfig.key]) {
        return sortConfig.direction === 'ascending' ? 1 : -1;
      }
      return 0;
    });

    setFilteredTools(sortedTools);
  }, [tools, searchQuery, sortConfig, statusFilter, categoryFilter, locationFilter, hideRetired]);

  const handleSearch = (e) => {
    e.preventDefault();
    // Search is now handled in the useEffect above
    console.log(`Searching for: ${searchQuery}`);
  };

  const handleSort = (key) => {
    setSortConfig({
      key,
      direction:
        sortConfig.key === key && sortConfig.direction === 'ascending'
          ? 'descending'
          : 'ascending',
    });
  };

  const getSortIcon = (key) => {
    if (sortConfig.key !== key) return null;
    return sortConfig.direction === 'ascending' ? '↑' : '↓';
  };

  if (loading && !filteredTools.length) {
    return <LoadingSpinner />;
  }

  const handleCheckoutClick = (tool) => {
    setSelectedTool(tool);
    setShowCheckoutModal(true);
  };

  // Handle barcode button click
  const handleBarcodeClick = (tool) => {
    setSelectedTool(tool);
    setShowBarcodeModal(true);
  };

  // Handle delete button click
  const handleDeleteClick = (tool) => {
    setSelectedTool(tool);
    setShowDeleteModal(true);
  };

  // Handle tool deletion
  const handleToolDelete = (toolId) => {
    // Remove the tool from the local state immediately for better UX
    const updatedTools = tools.filter(tool => tool.id !== toolId);
    // Note: In a real Redux implementation, we'd dispatch an action to remove the tool
    // For now, refresh the entire list to ensure data consistency
    dispatch(fetchTools());
  };

  // Handle tool retirement
  const handleToolRetire = (updatedTool) => {
    // Update the tool in local state immediately for better UX
    // Note: In a real Redux implementation, we'd dispatch an action to update the tool
    // For now, refresh the entire list to ensure data consistency
    dispatch(fetchTools());
  };

  const resetFilters = () => {
    setStatusFilter('');
    setCategoryFilter('');
    setLocationFilter('');
    setHideRetired(true);
  };

  const isAdmin = user?.is_admin || user?.department === 'Materials';

  return (
    <>
      {showHelp && (
        <HelpContent title="Tool Inventory" initialOpen={false}>
          <p>This page displays all tools in the inventory. You can search, filter, and sort tools by various criteria.</p>
          <ul>
            <li><strong>Search:</strong> Use the search box to find tools by number, serial, description, or location.</li>
            <li><strong>Filter:</strong> Click the Filters button to show/hide filtering options.</li>
            <li><strong>Sort:</strong> Click on any column header to sort the table by that column.</li>
            <li><strong>Actions:</strong> Use the action buttons to view details or checkout tools.</li>
          </ul>
        </HelpContent>
      )}

      <Card className="shadow-sm">
        <Card.Header className="bg-light">
          <div className="d-flex flex-wrap justify-content-between align-items-center gap-3">
            <div className="d-flex align-items-center">
              {showHelp && (
                <HelpIcon
                  title="Tool Inventory"
                  content={
                    <>
                      <p>This page displays all tools in the inventory. You can:</p>
                      <ul>
                        <li>Search for tools by number, description, or location</li>
                        <li>Filter tools by status, category, or location</li>
                        <li>Sort the table by clicking on column headers</li>
                        <li>View tool details or checkout tools using the action buttons</li>
                      </ul>
                    </>
                  }
                />
              )}
            </div>
            <div className="d-flex flex-grow-1 flex-md-grow-0" style={{ maxWidth: '500px' }}>
              <InputGroup>
                <Form.Control
                  type="text"
                  placeholder="Search tools..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  aria-label="Search tools"
                />
                <Tooltip text="Clear search" placement="top" show={showTooltips}>
                  <Button
                    variant="outline-secondary"
                    onClick={() => setSearchQuery('')}
                    style={{ display: searchQuery ? 'block' : 'none' }}
                  >
                    Clear
                  </Button>
                </Tooltip>
                <Tooltip text="Show/hide filter options" placement="top" show={showTooltips}>
                  <Button
                    variant="outline-primary"
                    onClick={() => setShowFilters(!showFilters)}
                    className="ms-2"
                  >
                    <i className={`bi bi-funnel${showFilters ? '-fill' : ''}`}></i> Filters
                    {(statusFilter || categoryFilter || locationFilter || !hideRetired) && (
                      <Badge bg="primary" className="ms-1">
                        {[
                          statusFilter && 1,
                          categoryFilter && 1,
                          locationFilter && 1,
                          !hideRetired && 1
                        ].filter(Boolean).reduce((a, b) => a + b, 0)}
                      </Badge>
                    )}
                  </Button>
                </Tooltip>
              </InputGroup>
            </div>
          </div>

          <Collapse in={showFilters}>
            <div className="mt-3 filter-section">
              <Row className="g-3">
                <Col xs={12} md={3}>
                  <Form.Group>
                    <Form.Label>Status</Form.Label>
                    <Form.Select
                      value={statusFilter}
                      onChange={(e) => setStatusFilter(e.target.value)}
                    >
                      <option value="">All Statuses</option>
                      <option value="available">Available</option>
                      <option value="checked_out">Checked Out</option>
                      <option value="maintenance">Maintenance</option>
                      <option value="retired">Retired</option>
                    </Form.Select>
                  </Form.Group>
                </Col>

                <Col xs={12} md={3}>
                  <Form.Group>
                    <Form.Label>Category</Form.Label>
                    <Form.Select
                      value={categoryFilter}
                      onChange={(e) => setCategoryFilter(e.target.value)}
                    >
                      <option value="">All Categories</option>
                      {availableCategories.map(category => (
                        <option key={category} value={category}>{category}</option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                </Col>

                <Col xs={12} md={3}>
                  <Form.Group>
                    <Form.Label>Location</Form.Label>
                    <Form.Select
                      value={locationFilter}
                      onChange={(e) => setLocationFilter(e.target.value)}
                    >
                      <option value="">All Locations</option>
                      {availableLocations.map(location => (
                        <option key={location} value={location}>{location}</option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                </Col>

                <Col xs={12} md={3} className="d-flex align-items-end">
                  <div className="d-flex gap-3 w-100">
                    <Form.Group className="mb-0 flex-grow-1">
                      <Form.Check
                        type="switch"
                        id="hide-retired-switch"
                        label="Hide Retired Tools"
                        checked={hideRetired}
                        onChange={(e) => setHideRetired(e.target.checked)}
                      />
                    </Form.Group>
                    <Button
                      variant="outline-secondary"
                      onClick={resetFilters}
                      className="mb-2"
                    >
                      Reset
                    </Button>
                  </div>
                </Col>
              </Row>

              <div className="mt-3 text-muted">
                <small>
                  Showing {filteredTools.length} of {tools.length} tools
                  {hideRetired && (
                    <span> (retired tools hidden)</span>
                  )}
                </small>
              </div>
            </div>
          </Collapse>
        </Card.Header>
        <Card.Body className="p-0">
          <div className="table-responsive">
            <Table striped bordered hover className="mb-0">
              <thead className="bg-light">
                <tr>
                  <th onClick={() => handleSort('tool_number')} className="cursor-pointer">
                    Tool Number {getSortIcon('tool_number')}
                  </th>
                  <th onClick={() => handleSort('serial_number')} className="cursor-pointer">
                    Serial Number {getSortIcon('serial_number')}
                  </th>
                  <th onClick={() => handleSort('description')} className="cursor-pointer">
                    Description {getSortIcon('description')}
                  </th>
                  <th onClick={() => handleSort('category')} className="cursor-pointer">
                    Category {getSortIcon('category')}
                  </th>
                  <th onClick={() => handleSort('location')} className="cursor-pointer">
                    Location {getSortIcon('location')}
                  </th>
                  <th onClick={() => handleSort('status')} className="cursor-pointer">
                    Status {getSortIcon('status')}
                  </th>
                  <th>Calibration</th>
                  <th style={{ width: '250px' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredTools.length > 0 ? (
                  filteredTools.map((tool) => (
                    <tr key={tool.id}>
                      <td>{tool.tool_number}</td>
                      <td>{tool.serial_number}</td>
                      <td>{tool.description || 'N/A'}</td>
                      <td>{tool.category || 'General'}</td>
                      <td>{tool.location || 'N/A'}</td>
                      <td>
                        <span
                          className={`status-badge ${
                            tool.status === 'available'
                              ? 'status-available'
                              : tool.status === 'checked_out'
                              ? 'status-checked-out'
                              : tool.status === 'maintenance'
                              ? 'status-maintenance'
                              : 'status-retired'
                          }`}
                        >
                          {tool.status === 'available' && <i className="bi bi-check-circle-fill me-1"></i>}
                          {tool.status === 'checked_out' && <i className="bi bi-person-fill me-1"></i>}
                          {tool.status === 'maintenance' && <i className="bi bi-tools me-1"></i>}
                          {tool.status === 'retired' && <i className="bi bi-archive-fill me-1"></i>}
                          {tool.status === 'available'
                            ? 'Available'
                            : tool.status === 'checked_out'
                            ? 'Checked Out'
                            : tool.status === 'maintenance'
                            ? 'Maintenance'
                            : 'Retired'}
                        </span>
                      </td>
                      <td>
                        <CalibrationStatusIndicator tool={tool} />
                      </td>
                      <td>
                        <div className="d-flex gap-1 flex-wrap">
                          <Tooltip text={showTooltips ? "View tool details" : null} placement="top">
                            <Button
                              as={Link}
                              to={`/tools/${tool.id}`}
                              variant="info"
                              size="sm"
                            >
                              View
                            </Button>
                          </Tooltip>
                          {tool.status === 'available' && (
                            <>
                              <Tooltip text={showTooltips ? "Check out this tool to yourself" : null} placement="top">
                                <Button
                                  as={Link}
                                  to={`/checkout/${tool.id}`}
                                  variant="success"
                                  size="sm"
                                >
                                  Checkout to Me
                                </Button>
                              </Tooltip>
                              {isAdmin && (
                                <Tooltip text={showTooltips ? "Check out this tool to another user" : null} placement="top">
                                  <Button
                                    variant="primary"
                                    size="sm"
                                    onClick={() => handleCheckoutClick(tool)}
                                  >
                                    Checkout to User
                                  </Button>
                                </Tooltip>
                              )}
                            </>
                          )}
                          <Tooltip text={showTooltips ? "Generate barcode/QR code for this tool" : null} placement="top">
                            <Button
                              variant="info"
                              size="sm"
                              onClick={() => handleBarcodeClick(tool)}
                            >
                              <i className="bi bi-upc-scan"></i>
                            </Button>
                          </Tooltip>
                          {user?.is_admin && (
                            <Tooltip text="Delete or retire this tool" placement="top" show={showTooltips}>
                              <Button
                                variant="danger"
                                size="sm"
                                onClick={() => handleDeleteClick(tool)}
                              >
                                <i className="bi bi-trash"></i>
                              </Button>
                            </Tooltip>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="7" className="text-center py-4">
                      No tools found.
                    </td>
                  </tr>
                )}
              </tbody>
            </Table>
          </div>
        </Card.Body>
      </Card>

      {/* Checkout Modal */}
      {selectedTool && (
        <CheckoutModal
          show={showCheckoutModal}
          onHide={() => setShowCheckoutModal(false)}
          tool={selectedTool}
        />
      )}

      {/* Barcode Modal */}
      {selectedTool && (
        <ToolBarcode
          show={showBarcodeModal}
          onHide={() => setShowBarcodeModal(false)}
          tool={selectedTool}
        />
      )}

      {/* Delete Modal */}
      {selectedTool && (
        <DeleteToolModal
          show={showDeleteModal}
          onHide={() => setShowDeleteModal(false)}
          tool={selectedTool}
          onDelete={handleToolDelete}
          onRetire={handleToolRetire}
        />
      )}
    </>
  );
};

export default ToolList;
