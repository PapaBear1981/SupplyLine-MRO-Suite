import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Modal, Button, Form, Table, Alert, InputGroup } from 'react-bootstrap';
import { fetchTools } from '../../store/toolsSlice';
import { checkoutTool } from '../../store/checkoutsSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const ToolSelectionModal = ({ show, onHide }) => {
  const dispatch = useDispatch();
  const { tools, loading } = useSelector((state) => state.tools);
  const { loading: checkoutLoading, error } = useSelector((state) => state.checkouts);
  
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTool, setSelectedTool] = useState(null);
  const [expectedReturnDate, setExpectedReturnDate] = useState('');
  const [validated, setValidated] = useState(false);

  useEffect(() => {
    if (show) {
      dispatch(fetchTools());
      // Set default return date to 7 days from now
      const defaultDate = new Date();
      defaultDate.setDate(defaultDate.getDate() + 7);
      setExpectedReturnDate(defaultDate.toISOString().split('T')[0]);
    }
  }, [show, dispatch]);

  const handleClose = () => {
    setSearchTerm('');
    setSelectedTool(null);
    setExpectedReturnDate('');
    setValidated(false);
    onHide();
  };

  const handleToolSelect = (tool) => {
    setSelectedTool(tool);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false || !selectedTool) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    setValidated(true);

    dispatch(checkoutTool({
      toolId: selectedTool.id,
      expectedReturnDate
    })).unwrap()
      .then(() => {
        handleClose();
      })
      .catch((err) => {
        console.error('Checkout failed:', err);
      });
  };

  // Filter available tools based on search term
  const availableTools = tools.filter(tool => 
    tool.status === 'available' && 
    (tool.tool_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
     tool.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
     tool.serial_number?.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <Modal show={show} onHide={handleClose} size="lg" centered>
      <Modal.Header closeButton>
        <Modal.Title>Checkout Tool</Modal.Title>
      </Modal.Header>
      <Form noValidate validated={validated} onSubmit={handleSubmit}>
        <Modal.Body>
          {error && <Alert variant="danger">{error.message}</Alert>}

          {/* Search Tools */}
          <div className="mb-3">
            <Form.Label>Search Available Tools</Form.Label>
            <InputGroup>
              <InputGroup.Text>
                <i className="bi bi-search"></i>
              </InputGroup.Text>
              <Form.Control
                type="text"
                placeholder="Search by tool number, description, or serial number..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </InputGroup>
          </div>

          {/* Tool Selection */}
          <div className="mb-3">
            <Form.Label>Select Tool to Checkout</Form.Label>
            {loading ? (
              <LoadingSpinner />
            ) : (
              <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                <Table striped bordered hover size="sm">
                  <thead>
                    <tr>
                      <th>Select</th>
                      <th>Tool Number</th>
                      <th>Description</th>
                      <th>Serial Number</th>
                      <th>Location</th>
                    </tr>
                  </thead>
                  <tbody>
                    {availableTools.length === 0 ? (
                      <tr>
                        <td colSpan="5" className="text-center text-muted">
                          {searchTerm ? 'No tools found matching your search.' : 'No available tools.'}
                        </td>
                      </tr>
                    ) : (
                      availableTools.map((tool) => (
                        <tr 
                          key={tool.id} 
                          className={selectedTool?.id === tool.id ? 'table-primary' : ''}
                          style={{ cursor: 'pointer' }}
                          onClick={() => handleToolSelect(tool)}
                        >
                          <td>
                            <Form.Check
                              type="radio"
                              name="selectedTool"
                              checked={selectedTool?.id === tool.id}
                              onChange={() => handleToolSelect(tool)}
                            />
                          </td>
                          <td>{tool.tool_number}</td>
                          <td>{tool.description}</td>
                          <td>{tool.serial_number}</td>
                          <td>{tool.location}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </Table>
              </div>
            )}
            {!selectedTool && validated && (
              <div className="invalid-feedback d-block">
                Please select a tool to checkout.
              </div>
            )}
          </div>

          {/* Expected Return Date */}
          <div className="mb-3">
            <Form.Label>Expected Return Date</Form.Label>
            <Form.Control
              type="date"
              value={expectedReturnDate}
              onChange={(e) => setExpectedReturnDate(e.target.value)}
              min={new Date().toISOString().split('T')[0]}
              required
            />
            <Form.Control.Feedback type="invalid">
              Please provide an expected return date.
            </Form.Control.Feedback>
          </div>

          {/* Selected Tool Summary */}
          {selectedTool && (
            <Alert variant="info">
              <strong>Selected Tool:</strong> {selectedTool.tool_number} - {selectedTool.description}
              <br />
              <strong>Serial Number:</strong> {selectedTool.serial_number}
              <br />
              <strong>Location:</strong> {selectedTool.location}
            </Alert>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>
            Cancel
          </Button>
          <Button 
            variant="primary" 
            type="submit" 
            disabled={checkoutLoading || !selectedTool}
          >
            {checkoutLoading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Checking Out...
              </>
            ) : (
              'Checkout Tool'
            )}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
};

export default ToolSelectionModal;
