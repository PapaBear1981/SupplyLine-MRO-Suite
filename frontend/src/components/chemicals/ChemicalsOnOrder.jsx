import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { Table, Button, Alert } from 'react-bootstrap';
import { markChemicalAsDelivered, fetchChemicalsOnOrder } from '../../store/chemicalsSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const ChemicalsOnOrder = () => {
  const dispatch = useDispatch();
  const { chemicalsOnOrder, loading } = useSelector((state) => state.chemicals);

  // Handle marking a chemical as delivered
  const handleMarkAsDelivered = async (id) => {
    if (!window.confirm('Are you sure you want to mark this chemical as delivered?')) return;
    
    try {
      await dispatch(markChemicalAsDelivered(id)).unwrap();
      
      // Refresh the list
      dispatch(fetchChemicalsOnOrder());
    } catch (error) {
      console.error('Failed to mark chemical as delivered:', error);
    }
  };

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  if (loading && !chemicalsOnOrder.length) {
    return <LoadingSpinner />;
  }

  return (
    <>
      {chemicalsOnOrder.length === 0 ? (
        <Alert variant="info">No chemicals are currently on order.</Alert>
      ) : (
        <div className="table-responsive">
          <Table hover bordered className="align-middle">
            <thead className="bg-light">
              <tr>
                <th>Part Number</th>
                <th>Lot Number</th>
                <th>Description</th>
                <th>Manufacturer</th>
                <th>Order Date</th>
                <th>Expected Delivery</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {chemicalsOnOrder.map((chemical) => (
                <tr key={chemical.id}>
                  <td>{chemical.part_number}</td>
                  <td>{chemical.lot_number}</td>
                  <td>{chemical.description}</td>
                  <td>{chemical.manufacturer}</td>
                  <td>{formatDate(chemical.reorder_date)}</td>
                  <td>{formatDate(chemical.expected_delivery_date)}</td>
                  <td>
                    <div className="d-flex gap-2">
                      <Button
                        as={Link}
                        to={`/chemicals/${chemical.id}`}
                        variant="primary"
                        size="sm"
                      >
                        View
                      </Button>
                      <Button
                        variant="success"
                        size="sm"
                        onClick={() => handleMarkAsDelivered(chemical.id)}
                      >
                        Mark as Delivered
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      )}
    </>
  );
};

export default ChemicalsOnOrder;
