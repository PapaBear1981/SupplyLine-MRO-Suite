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
    dispatch(fetchTools());
  }, [dispatch]);

  useEffect(() => {
    // Use search results if available, otherwise use all tools
    const toolsToDisplay = searchQuery ? searchResults : tools;

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
  }, [tools, searchResults, searchQuery, sortConfig]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      dispatch(searchTools(searchQuery));
    }
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
            <Form onSubmit={handleSearch} className="d-flex flex-grow-1 flex-md-grow-0" style={{ maxWidth: '500px' }}>
              <InputGroup>
                <Form.Control
                  type="text"
                  placeholder="Search tools..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                <Button type="submit" variant="primary">
                  Search
                </Button>
              </InputGroup>
            </Form>
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
                      <td>
                        <span
                          className={`badge ${
                            tool.status === 'available'
                              ? 'bg-success'
                              : tool.status === 'checked_out'
                              ? 'bg-warning'
                              : 'bg-danger'
                          }`}
                        >
                          {tool.status === 'available' ? 'Available' : 'Checked Out'}
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
                    <td colSpan="5" className="text-center py-4">
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
