import { Card, Table, Alert } from 'react-bootstrap';
import LoadingSpinner from '../common/LoadingSpinner';

const ChemicalIssuanceHistory = ({ issuances, loading }) => {
  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <Card className="shadow-sm">
      <Card.Header className="bg-light">
        <h4 className="mb-0">Issuance History</h4>
      </Card.Header>
      <Card.Body>
        {issuances.length === 0 ? (
          <Alert variant="info">No issuance history found for this chemical.</Alert>
        ) : (
          <div className="table-responsive">
            <Table hover bordered className="align-middle">
              <thead className="bg-light">
                <tr>
                  <th>Date</th>
                  <th>Issued By</th>
                  <th>Quantity</th>
                  <th>Returned</th>
                  <th>Remaining</th>
                  <th>Hangar</th>
                  <th>Purpose</th>
                </tr>
              </thead>
              <tbody>
                {issuances.map((issuance) => (
                  <tr key={issuance.id}>
                    <td>{new Date(issuance.issue_date).toLocaleString()}</td>
                    <td>{issuance.user_name}</td>
                    <td>{issuance.quantity}</td>
                    <td>{issuance.total_returned ?? 0}</td>
                    <td>{issuance.remaining_quantity ?? issuance.quantity}</td>
                    <td>{issuance.hangar}</td>
                    <td>{issuance.purpose || 'N/A'}</td>
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

export default ChemicalIssuanceHistory;
