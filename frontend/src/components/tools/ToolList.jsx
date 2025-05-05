import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Table, Button, Form, InputGroup, Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { fetchTools, searchTools } from '../../store/toolsSlice';
import LoadingSpinner from '../common/LoadingSpinner';
import CheckoutModal from '../checkouts/CheckoutModal';

const ToolList = () => {
  const dispatch = useDispatch();
  const { tools, loading, searchResults } = useSelector((state) => state.tools);
  const { user } = useSelector((state) => state.auth);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredTools, setFilteredTools] = useState([]);
  const [sortConfig, setSortConfig] = useState({ key: 'tool_number', direction: 'ascending' });
  const [showCheckoutModal, setShowCheckoutModal] = useState(false);
  const [selectedTool, setSelectedTool] = useState(null);

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

  useEffect(() => {
    // Filter tools based on search query
    let toolsToDisplay = [...tools];

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      toolsToDisplay = tools.filter(tool =>
        tool.tool_number.toLowerCase().includes(query) ||
        tool.serial_number.toLowerCase().includes(query) ||
        (tool.description && tool.description.toLowerCase().includes(query)) ||
        (tool.location && tool.location.toLowerCase().includes(query))
      );
      console.log(`Filtered to ${toolsToDisplay.length} tools matching "${query}"`);
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
  }, [tools, searchQuery, sortConfig]);

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

  const isAdmin = user?.is_admin || user?.department === 'Materials';

  return (
    <>
      <Card className="shadow-sm">
        <Card.Header className="bg-light">
          <div className="d-flex flex-wrap justify-content-between align-items-center gap-3">
            <h5 className="mb-0">Tool Inventory</h5>
            <div className="d-flex flex-grow-1 flex-md-grow-0" style={{ maxWidth: '500px' }}>
              <InputGroup>
                <Form.Control
                  type="text"
                  placeholder="Search tools..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  aria-label="Search tools"
                />
                <Button
                  variant="outline-secondary"
                  onClick={() => setSearchQuery('')}
                  style={{ display: searchQuery ? 'block' : 'none' }}
                >
                  Clear
                </Button>
              </InputGroup>
            </div>
          </div>
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
                  <th onClick={() => handleSort('location')} className="cursor-pointer">
                    Location {getSortIcon('location')}
                  </th>
                  <th onClick={() => handleSort('status')} className="cursor-pointer">
                    Status {getSortIcon('status')}
                  </th>
                  <th style={{ width: '200px' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredTools.length > 0 ? (
                  filteredTools.map((tool) => (
                    <tr key={tool.id}>
                      <td>{tool.tool_number}</td>
                      <td>{tool.serial_number}</td>
                      <td>{tool.description || 'N/A'}</td>
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
                        <div className="d-flex gap-2">
                          <Button
                            as={Link}
                            to={`/tools/${tool.id}`}
                            variant="info"
                            size="sm"
                          >
                            View
                          </Button>
                          {tool.status === 'available' && (
                            <>
                              <Button
                                as={Link}
                                to={`/checkout/${tool.id}`}
                                variant="success"
                                size="sm"
                              >
                                Checkout to Me
                              </Button>
                              {isAdmin && (
                                <Button
                                  variant="primary"
                                  size="sm"
                                  onClick={() => handleCheckoutClick(tool)}
                                >
                                  Checkout to User
                                </Button>
                              )}
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" className="text-center py-4">
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
    </>
  );
};

export default ToolList;
