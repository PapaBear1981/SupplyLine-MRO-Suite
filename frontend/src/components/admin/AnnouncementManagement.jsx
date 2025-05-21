import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { 
  Card, Table, Button, Badge, Pagination, 
  Form, Modal, Alert, Spinner, Row, Col, 
  InputGroup, FormControl, Dropdown
} from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faPlus, faEdit, faTrash, faTimes, 
  faCheck, faExclamationTriangle, faSearch, 
  faFilter, faSort, faSortUp, faSortDown
} from '@fortawesome/free-solid-svg-icons';
import { 
  fetchAnnouncements, 
  createAnnouncement, 
  updateAnnouncement, 
  deleteAnnouncement,
  clearErrors
} from '../../store/announcementSlice';
import { formatDate } from '../../utils/dateUtils';

const AnnouncementManagement = () => {
  const dispatch = useDispatch();
  const { announcements, pagination, loading, error } = useSelector((state) => state.announcements);
  
  // Local state
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [currentAnnouncement, setCurrentAnnouncement] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    priority: 'medium',
    expiration_date: '',
    is_active: true
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    priority: '',
    active_only: true
  });
  const [sortField, setSortField] = useState('created_at');
  const [sortDirection, setSortDirection] = useState('desc');
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);
  
  // Load announcements on component mount and when filters/pagination change
  useEffect(() => {
    loadAnnouncements();
  }, [page, limit, filters, sortField, sortDirection]);
  
  const loadAnnouncements = () => {
    dispatch(fetchAnnouncements({ 
      page, 
      limit, 
      filters: {
        ...filters,
        sort_by: sortField,
        sort_direction: sortDirection,
        search: searchTerm.trim() || undefined
      }
    }));
  };
  
  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };
  
  // Open add modal
  const handleAddClick = () => {
    setFormData({
      title: '',
      content: '',
      priority: 'medium',
      expiration_date: '',
      is_active: true
    });
    setShowAddModal(true);
  };
  
  // Open edit modal
  const handleEditClick = (announcement) => {
    setCurrentAnnouncement(announcement);
    setFormData({
      title: announcement.title,
      content: announcement.content,
      priority: announcement.priority,
      expiration_date: announcement.expiration_date ? announcement.expiration_date.split('T')[0] : '',
      is_active: announcement.is_active
    });
    setShowEditModal(true);
  };
  
  // Open delete modal
  const handleDeleteClick = (announcement) => {
    setCurrentAnnouncement(announcement);
    setShowDeleteModal(true);
  };
  
  // Submit add form
  const handleAddSubmit = (e) => {
    e.preventDefault();
    dispatch(createAnnouncement(formData))
      .unwrap()
      .then(() => {
        setShowAddModal(false);
        loadAnnouncements();
      })
      .catch((error) => {
        console.error('Failed to create announcement:', error);
      });
  };
  
  // Submit edit form
  const handleEditSubmit = (e) => {
    e.preventDefault();
    dispatch(updateAnnouncement({ 
      id: currentAnnouncement.id, 
      announcementData: formData 
    }))
      .unwrap()
      .then(() => {
        setShowEditModal(false);
        loadAnnouncements();
      })
      .catch((error) => {
        console.error('Failed to update announcement:', error);
      });
  };
  
  // Confirm delete
  const handleDeleteConfirm = () => {
    dispatch(deleteAnnouncement(currentAnnouncement.id))
      .unwrap()
      .then(() => {
        setShowDeleteModal(false);
        loadAnnouncements();
      })
      .catch((error) => {
        console.error('Failed to delete announcement:', error);
      });
  };
  
  // Handle search
  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1); // Reset to first page
    loadAnnouncements();
  };
  
  // Handle filter changes
  const handleFilterChange = (name, value) => {
    setFilters({
      ...filters,
      [name]: value
    });
    setPage(1); // Reset to first page
  };
  
  // Handle sort
  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };
  
  // Get sort icon
  const getSortIcon = (field) => {
    if (sortField !== field) return <FontAwesomeIcon icon={faSort} className="ms-1 text-muted" />;
    return sortDirection === 'asc' 
      ? <FontAwesomeIcon icon={faSortUp} className="ms-1" />
      : <FontAwesomeIcon icon={faSortDown} className="ms-1" />;
  };
  
  // Get priority badge variant
  const getPriorityBadgeVariant = (priority) => {
    switch (priority) {
      case 'high': return 'danger';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'secondary';
    }
  };
  
  // Pagination controls
  const handlePageChange = (newPage) => {
    setPage(newPage);
  };
  
  // Render pagination
  const renderPagination = () => {
    if (!pagination || pagination.pages <= 1) return null;
    
    const items = [];
    for (let i = 1; i <= pagination.pages; i++) {
      items.push(
        <Pagination.Item 
          key={i} 
          active={i === pagination.page}
          onClick={() => handlePageChange(i)}
        >
          {i}
        </Pagination.Item>
      );
    }
    
    return (
      <Pagination className="mt-3 justify-content-center">
        <Pagination.First onClick={() => handlePageChange(1)} disabled={pagination.page === 1} />
        <Pagination.Prev onClick={() => handlePageChange(pagination.page - 1)} disabled={pagination.page === 1} />
        {items}
        <Pagination.Next onClick={() => handlePageChange(pagination.page + 1)} disabled={pagination.page === pagination.pages} />
        <Pagination.Last onClick={() => handlePageChange(pagination.pages)} disabled={pagination.page === pagination.pages} />
      </Pagination>
    );
  };
  
  return (
    <div className="announcement-management">
      <Card className="mb-4">
        <Card.Header className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Announcement Management</h5>
          <Button variant="primary" size="sm" onClick={handleAddClick}>
            <FontAwesomeIcon icon={faPlus} className="me-1" /> New Announcement
          </Button>
        </Card.Header>
        <Card.Body>
          {/* Search and filters */}
          <Row className="mb-3">
            <Col md={6}>
              <Form onSubmit={handleSearch}>
                <InputGroup>
                  <FormControl
                    placeholder="Search announcements..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                  <Button type="submit" variant="outline-secondary">
                    <FontAwesomeIcon icon={faSearch} />
                  </Button>
                </InputGroup>
              </Form>
            </Col>
            <Col md={6} className="d-flex justify-content-end">
              <Dropdown className="me-2">
                <Dropdown.Toggle variant="outline-secondary" id="priority-filter">
                  <FontAwesomeIcon icon={faFilter} className="me-1" />
                  Priority: {filters.priority || 'All'}
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item onClick={() => handleFilterChange('priority', '')}>All</Dropdown.Item>
                  <Dropdown.Item onClick={() => handleFilterChange('priority', 'high')}>High</Dropdown.Item>
                  <Dropdown.Item onClick={() => handleFilterChange('priority', 'medium')}>Medium</Dropdown.Item>
                  <Dropdown.Item onClick={() => handleFilterChange('priority', 'low')}>Low</Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
              <Form.Check
                type="switch"
                id="active-only-switch"
                label="Active only"
                checked={filters.active_only}
                onChange={(e) => handleFilterChange('active_only', e.target.checked)}
                className="d-flex align-items-center"
              />
            </Col>
          </Row>
          
          {/* Error message */}
          {error.fetchAnnouncements && (
            <Alert variant="danger" onClose={() => dispatch(clearErrors())} dismissible>
              {error.fetchAnnouncements.message || 'Failed to load announcements'}
            </Alert>
          )}
          
          {/* Loading indicator */}
          {loading.fetchAnnouncements ? (
            <div className="text-center py-5">
              <Spinner animation="border" role="status">
                <span className="visually-hidden">Loading...</span>
              </Spinner>
            </div>
          ) : (
            <>
              {/* Announcements table */}
              {announcements.length === 0 ? (
                <Alert variant="info">No announcements found.</Alert>
              ) : (
                <div className="table-responsive">
                  <Table hover className="align-middle">
                    <thead>
                      <tr>
                        <th onClick={() => handleSort('title')} style={{ cursor: 'pointer' }}>
                          Title {getSortIcon('title')}
                        </th>
                        <th onClick={() => handleSort('priority')} style={{ cursor: 'pointer' }}>
                          Priority {getSortIcon('priority')}
                        </th>
                        <th onClick={() => handleSort('created_at')} style={{ cursor: 'pointer' }}>
                          Created {getSortIcon('created_at')}
                        </th>
                        <th onClick={() => handleSort('expiration_date')} style={{ cursor: 'pointer' }}>
                          Expires {getSortIcon('expiration_date')}
                        </th>
                        <th onClick={() => handleSort('is_active')} style={{ cursor: 'pointer' }}>
                          Status {getSortIcon('is_active')}
                        </th>
                        <th className="text-end">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {announcements.map((announcement) => (
                        <tr key={announcement.id}>
                          <td>{announcement.title}</td>
                          <td>
                            <Badge bg={getPriorityBadgeVariant(announcement.priority)}>
                              {announcement.priority}
                            </Badge>
                          </td>
                          <td>{formatDate(announcement.created_at)}</td>
                          <td>
                            {announcement.expiration_date 
                              ? formatDate(announcement.expiration_date)
                              : <span className="text-muted">Never</span>
                            }
                          </td>
                          <td>
                            {announcement.is_active 
                              ? <Badge bg="success">Active</Badge>
                              : <Badge bg="secondary">Inactive</Badge>
                            }
                          </td>
                          <td className="text-end">
                            <Button 
                              variant="outline-primary" 
                              size="sm" 
                              className="me-1"
                              onClick={() => handleEditClick(announcement)}
                            >
                              <FontAwesomeIcon icon={faEdit} />
                            </Button>
                            <Button 
                              variant="outline-danger" 
                              size="sm"
                              onClick={() => handleDeleteClick(announcement)}
                            >
                              <FontAwesomeIcon icon={faTrash} />
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              )}
              
              {/* Pagination */}
              {renderPagination()}
            </>
          )}
        </Card.Body>
      </Card>
      
      {/* Add Announcement Modal */}
      <Modal show={showAddModal} onHide={() => setShowAddModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Create New Announcement</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleAddSubmit}>
          <Modal.Body>
            {error.createAnnouncement && (
              <Alert variant="danger">
                {error.createAnnouncement.message || 'Failed to create announcement'}
              </Alert>
            )}
            <Form.Group className="mb-3">
              <Form.Label>Title</Form.Label>
              <Form.Control
                type="text"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Content</Form.Label>
              <Form.Control
                as="textarea"
                rows={5}
                name="content"
                value={formData.content}
                onChange={handleInputChange}
                required
              />
            </Form.Group>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Priority</Form.Label>
                  <Form.Select
                    name="priority"
                    value={formData.priority}
                    onChange={handleInputChange}
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Expiration Date (Optional)</Form.Label>
                  <Form.Control
                    type="date"
                    name="expiration_date"
                    value={formData.expiration_date}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Check
                type="checkbox"
                label="Active"
                name="is_active"
                checked={formData.is_active}
                onChange={handleInputChange}
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowAddModal(false)}>
              Cancel
            </Button>
            <Button 
              variant="primary" 
              type="submit"
              disabled={loading.createAnnouncement}
            >
              {loading.createAnnouncement ? (
                <>
                  <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-1" />
                  Creating...
                </>
              ) : 'Create Announcement'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
      
      {/* Edit Announcement Modal */}
      <Modal show={showEditModal} onHide={() => setShowEditModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Edit Announcement</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleEditSubmit}>
          <Modal.Body>
            {error.updateAnnouncement && (
              <Alert variant="danger">
                {error.updateAnnouncement.message || 'Failed to update announcement'}
              </Alert>
            )}
            <Form.Group className="mb-3">
              <Form.Label>Title</Form.Label>
              <Form.Control
                type="text"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Content</Form.Label>
              <Form.Control
                as="textarea"
                rows={5}
                name="content"
                value={formData.content}
                onChange={handleInputChange}
                required
              />
            </Form.Group>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Priority</Form.Label>
                  <Form.Select
                    name="priority"
                    value={formData.priority}
                    onChange={handleInputChange}
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Expiration Date (Optional)</Form.Label>
                  <Form.Control
                    type="date"
                    name="expiration_date"
                    value={formData.expiration_date}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Check
                type="checkbox"
                label="Active"
                name="is_active"
                checked={formData.is_active}
                onChange={handleInputChange}
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowEditModal(false)}>
              Cancel
            </Button>
            <Button 
              variant="primary" 
              type="submit"
              disabled={loading.updateAnnouncement}
            >
              {loading.updateAnnouncement ? (
                <>
                  <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-1" />
                  Updating...
                </>
              ) : 'Update Announcement'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
      
      {/* Delete Confirmation Modal */}
      <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Delete</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {error.deleteAnnouncement && (
            <Alert variant="danger">
              {error.deleteAnnouncement.message || 'Failed to delete announcement'}
            </Alert>
          )}
          <p>
            <FontAwesomeIcon icon={faExclamationTriangle} className="text-warning me-2" />
            Are you sure you want to delete the announcement "{currentAnnouncement?.title}"?
          </p>
          <p className="mb-0 text-danger">This action cannot be undone.</p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
            Cancel
          </Button>
          <Button 
            variant="danger" 
            onClick={handleDeleteConfirm}
            disabled={loading.deleteAnnouncement}
          >
            {loading.deleteAnnouncement ? (
              <>
                <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-1" />
                Deleting...
              </>
            ) : 'Delete Announcement'}
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default AnnouncementManagement;
