import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useParams } from 'react-router-dom';
import { Form, Button, Card, Alert } from 'react-bootstrap';
import { fetchToolById, updateTool } from '../../store/toolsSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const EditToolForm = () => {
  const { id } = useParams();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { currentTool, loading, error } = useSelector((state) => state.tools);

  const [toolData, setToolData] = useState({
    tool_number: '',
    serial_number: '',
    description: '',
    condition: 'New',
    location: '',
    category: 'General'
  });
  const [validated, setValidated] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);

  useEffect(() => {
    if (id) {
      dispatch(fetchToolById(id))
        .unwrap()
        .then(() => {
          setInitialLoading(false);
        })
        .catch((err) => {
          console.error('Failed to fetch tool:', err);
          setInitialLoading(false);
        });
    }
  }, [dispatch, id]);

  useEffect(() => {
    if (currentTool) {
      setToolData({
        tool_number: currentTool.tool_number || '',
        serial_number: currentTool.serial_number || '',
        description: currentTool.description || '',
        condition: currentTool.condition || 'New',
        location: currentTool.location || '',
        category: currentTool.category || 'General'
      });
    }
  }, [currentTool]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setToolData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    setValidated(true);

    // Add more detailed logging
    console.log('Submitting tool data:', toolData);
    console.log('Tool data category:', toolData.category);
    console.log('Tool data type:', typeof toolData);
    console.log('Tool data keys:', Object.keys(toolData));

    // Create a copy of the data to ensure we're sending the right fields
    const toolDataToSend = {
      tool_number: toolData.tool_number,
      serial_number: toolData.serial_number,
      description: toolData.description,
      condition: toolData.condition,
      location: toolData.location,
      category: toolData.category
    };

    console.log('Tool data to send:', toolDataToSend);

    dispatch(updateTool({ id, toolData: toolDataToSend }))
      .unwrap()
      .then((result) => {
        console.log('Tool update result:', result);
        navigate(`/tools/${id}`);
      })
      .catch((err) => {
        console.error('Failed to update tool:', err);
      });
  };

  if (initialLoading) {
    return <LoadingSpinner />;
  }

  return (
    <Card className="shadow-sm">
      <Card.Header>
        <h4>Edit Tool</h4>
      </Card.Header>
      <Card.Body>
        {error && <Alert variant="danger">{error.message}</Alert>}

        <Form noValidate validated={validated} onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Tool Number*</Form.Label>
            <Form.Control
              type="text"
              name="tool_number"
              value={toolData.tool_number}
              onChange={handleChange}
              required
            />
            <Form.Control.Feedback type="invalid">
              Tool number is required
            </Form.Control.Feedback>
            <Form.Text className="text-muted">
              You can have multiple tools with the same tool number as long as they have different serial numbers.
            </Form.Text>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Serial Number*</Form.Label>
            <Form.Control
              type="text"
              name="serial_number"
              value={toolData.serial_number}
              onChange={handleChange}
              required
            />
            <Form.Control.Feedback type="invalid">
              Serial number is required
            </Form.Control.Feedback>
            <Form.Text className="text-muted">
              Serial number must be unique for tools with the same tool number.
            </Form.Text>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Description</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              name="description"
              value={toolData.description}
              onChange={handleChange}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Condition</Form.Label>
            <Form.Select
              name="condition"
              value={toolData.condition}
              onChange={handleChange}
            >
              <option value="New">New</option>
              <option value="Good">Good</option>
              <option value="Fair">Fair</option>
              <option value="Poor">Poor</option>
            </Form.Select>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Location</Form.Label>
            <Form.Control
              type="text"
              name="location"
              value={toolData.location}
              onChange={handleChange}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Category</Form.Label>
            <Form.Select
              name="category"
              value={toolData.category}
              onChange={handleChange}
            >
              <option value="General">General</option>
              <option value="Q400">Q400</option>
              <option value="CL415">CL415</option>
              <option value="RJ85">RJ85</option>
              <option value="Engine">Engine</option>
              <option value="Floor">Floor</option>
              <option value="CNC">CNC</option>
              <option value="Sheetmetal">Sheetmetal</option>
            </Form.Select>
          </Form.Group>

          <div className="d-flex justify-content-end gap-2">
            <Button variant="secondary" onClick={() => navigate(`/tools/${id}`)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default EditToolForm;
