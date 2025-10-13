import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useParams } from 'react-router-dom';
import { Form, Button, Card, Alert } from 'react-bootstrap';
import { fetchKitById, updateKit, fetchAircraftTypes } from '../../store/kitsSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const EditKitForm = () => {
  const { id } = useParams();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { currentKit, aircraftTypes, loading, error } = useSelector((state) => state.kits);

  const [kitData, setKitData] = useState({
    name: '',
    aircraft_type_id: '',
    description: '',
    status: 'active'
  });
  const [validated, setValidated] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);

  useEffect(() => {
    // Fetch aircraft types
    dispatch(fetchAircraftTypes());
    
    // Fetch kit details
    if (id) {
      dispatch(fetchKitById(id))
        .unwrap()
        .then(() => {
          setInitialLoading(false);
        })
        .catch((err) => {
          console.error('Failed to fetch kit:', err);
          setInitialLoading(false);
        });
    }
  }, [dispatch, id]);

  useEffect(() => {
    if (currentKit && currentKit.id === parseInt(id)) {
      setKitData({
        name: currentKit.name || '',
        aircraft_type_id: currentKit.aircraft_type_id || '',
        description: currentKit.description || '',
        status: currentKit.status || 'active'
      });
    }
  }, [currentKit, id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setKitData(prev => ({
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

    // Prepare data for submission
    const dataToSend = {
      name: kitData.name,
      aircraft_type_id: parseInt(kitData.aircraft_type_id),
      description: kitData.description,
      status: kitData.status
    };

    dispatch(updateKit({ id, data: dataToSend }))
      .unwrap()
      .then(() => {
        navigate(`/kits/${id}`);
      })
      .catch((err) => {
        console.error('Failed to update kit:', err);
      });
  };

  if (initialLoading) {
    return <LoadingSpinner />;
  }

  return (
    <Card className="shadow-sm">
      <Card.Header>
        <h4>Edit Kit</h4>
      </Card.Header>
      <Card.Body>
        {error && <Alert variant="danger">{error.message || error}</Alert>}

        <Form noValidate validated={validated} onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Kit Name*</Form.Label>
            <Form.Control
              type="text"
              name="name"
              value={kitData.name}
              onChange={handleChange}
              required
              placeholder="Enter kit name"
            />
            <Form.Control.Feedback type="invalid">
              Kit name is required
            </Form.Control.Feedback>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Aircraft Type*</Form.Label>
            <Form.Select
              name="aircraft_type_id"
              value={kitData.aircraft_type_id}
              onChange={handleChange}
              required
            >
              <option value="">Select aircraft type...</option>
              {aircraftTypes.map(type => (
                <option key={type.id} value={type.id}>
                  {type.name}
                </option>
              ))}
            </Form.Select>
            <Form.Control.Feedback type="invalid">
              Aircraft type is required
            </Form.Control.Feedback>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Description</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              name="description"
              value={kitData.description}
              onChange={handleChange}
              placeholder="Enter kit description (optional)"
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Status*</Form.Label>
            <Form.Select
              name="status"
              value={kitData.status}
              onChange={handleChange}
              required
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="maintenance">Maintenance</option>
            </Form.Select>
            <Form.Control.Feedback type="invalid">
              Status is required
            </Form.Control.Feedback>
          </Form.Group>

          <div className="d-flex justify-content-end gap-2">
            <Button variant="secondary" onClick={() => navigate(`/kits/${id}`)}>
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

export default EditKitForm;

