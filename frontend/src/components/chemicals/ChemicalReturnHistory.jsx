import PropTypes from 'prop-types';
import { Card, Table, Alert } from 'react-bootstrap';
import LoadingSpinner from '../common/LoadingSpinner';

const ChemicalReturnHistory = ({ returns = [], loading }) => {
  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <Card className="shadow-sm">
      <Card.Header className="bg-light">
        <h4 className="mb-0">Return History</h4>
      </Card.Header>
      <Card.Body>
        {returns.length === 0 ? (
          <Alert variant="info">No returns have been recorded for this chemical.</Alert>
        ) : (
          <div className="table-responsive">
            <Table hover bordered className="align-middle">
              <thead className="bg-light">
                <tr>
                  <th>Date</th>
                  <th>Returned By</th>
                  <th>Quantity</th>
                  <th>Warehouse</th>
                  <th>Location</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                {returns.map((entry) => (
                  <tr key={entry.id}>
                    <td>{entry.return_date ? new Date(entry.return_date).toLocaleString() : '—'}</td>
                    <td>{entry.returned_by_name || 'Unknown'}</td>
                    <td>{entry.quantity}</td>
                    <td>{entry.warehouse_name || 'N/A'}</td>
                    <td>{entry.location || 'N/A'}</td>
                    <td>{entry.notes || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

ChemicalReturnHistory.propTypes = {
  returns: PropTypes.array,
  loading: PropTypes.bool,
};

export default ChemicalReturnHistory;
