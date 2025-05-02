import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Table, Button, Form, InputGroup, Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { fetchTools, searchTools } from '../../store/toolsSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const ToolList = () => {
  const dispatch = useDispatch();
  const { tools, loading, searchResults } = useSelector((state) => state.tools);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredTools, setFilteredTools] = useState([]);
  const [sortConfig, setSortConfig] = useState({ key: 'name', direction: 'ascending' });

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

  return (
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
                <th onClick={() => handleSort('id')} className="cursor-pointer">
                  ID {getSortIcon('id')}
                </th>
                <th onClick={() => handleSort('name')} className="cursor-pointer">
                  Name {getSortIcon('name')}
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
                <th style={{ width: '200px' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredTools.length > 0 ? (
                filteredTools.map((tool) => (
                  <tr key={tool.id}>
                    <td>{tool.id}</td>
                    <td>{tool.name}</td>
                    <td>{tool.category}</td>
                    <td>{tool.location}</td>
                    <td>
                      <span
                        className={`badge ${
                          tool.status === 'Available'
                            ? 'bg-success'
                            : tool.status === 'Checked Out'
                            ? 'bg-warning'
                            : 'bg-danger'
                        }`}
                      >
                        {tool.status}
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
                        {tool.status === 'Available' && (
                          <Button
                            as={Link}
                            to={`/checkout/${tool.id}`}
                            variant="primary"
                            size="sm"
                          >
                            Checkout
                          </Button>
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
  );
};

export default ToolList;
