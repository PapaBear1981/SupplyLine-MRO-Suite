import { useEffect, useState } from 'react';
import { Table, Card, Badge, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { formatDate } from '../../utils/dateUtils';
import LoadingSpinner from '../common/LoadingSpinner';
import HelpIcon from '../common/HelpIcon';
import { useHelp } from '../../context/HelpContext';
import api from '../../services/api';

const RecentTransactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { showHelp } = useHelp();
  const [limit, setLimit] = useState(50);

  useEffect(() => {
    const fetchTransactions = async () => {
      setLoading(true);
      setError(null);
      try {
        // Fetch recent checkouts and returns
        const response = await api.get(`/checkouts?limit=${limit}&include_returned=true`);

        // Transform the data to show both checkouts and returns as transactions
        const checkoutTransactions = response.data.map(checkout => ({
          id: checkout.id,
          type: checkout.return_date ? 'return' : 'checkout',
          date: checkout.return_date || checkout.checkout_date,
          tool_id: checkout.tool_id,
          tool_number: checkout.tool_number,
          serial_number: checkout.serial_number,
          description: checkout.description,
          user_name: checkout.user_name,
          checkout_date: checkout.checkout_date,
          return_date: checkout.return_date
        }));

        // Sort by date descending (most recent first)
        checkoutTransactions.sort((a, b) => new Date(b.date) - new Date(a.date));

        setTransactions(checkoutTransactions);
      } catch (err) {
        console.error('Error fetching transactions:', err);
        setError('Failed to load recent transactions');
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, [limit]);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <Card>
        <Card.Body>
          <div className="alert alert-danger">{error}</div>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm">
      <Card.Header className="bg-light">
        <div className="d-flex justify-content-between align-items-center">
          <h4 className="mb-0">Recent Tool Transactions</h4>
          <div className="d-flex align-items-center gap-2">
            {showHelp && (
              <HelpIcon
                title="Recent Transactions"
                content={
                  <>
                    <p>This tab shows the most recent tool checkout and return transactions.</p>
                    <ul>
                      <li><strong>Checkout:</strong> When a tool is checked out to a user</li>
                      <li><strong>Return:</strong> When a tool is returned to inventory</li>
                    </ul>
                    <p>Transactions are sorted by date with the most recent first.</p>
                  </>
                }
                size="sm"
              />
            )}
            <div className="btn-group" role="group">
              <Button
                variant={limit === 50 ? 'primary' : 'outline-primary'}
                size="sm"
                onClick={() => setLimit(50)}
              >
                50
              </Button>
              <Button
                variant={limit === 100 ? 'primary' : 'outline-primary'}
                size="sm"
                onClick={() => setLimit(100)}
              >
                100
              </Button>
              <Button
                variant={limit === 200 ? 'primary' : 'outline-primary'}
                size="sm"
                onClick={() => setLimit(200)}
              >
                200
              </Button>
            </div>
          </div>
        </div>
      </Card.Header>
      <Card.Body className="p-0">
        <div className="table-responsive">
          <Table striped bordered hover className="mb-0">
            <thead className="bg-light">
              <tr>
                <th>Date</th>
                <th>Type</th>
                <th>Tool Number</th>
                <th>Serial Number</th>
                <th>Description</th>
                <th>User</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {transactions.length > 0 ? (
                transactions.map((transaction) => (
                  <tr key={`${transaction.id}-${transaction.type}`}>
                    <td>{formatDate(transaction.date)}</td>
                    <td>
                      {transaction.type === 'checkout' ? (
                        <Badge bg="primary">
                          <i className="bi bi-box-arrow-right me-1"></i>
                          Checkout
                        </Badge>
                      ) : (
                        <Badge bg="success">
                          <i className="bi bi-box-arrow-in-left me-1"></i>
                          Return
                        </Badge>
                      )}
                    </td>
                    <td>
                      <Link to={`/tools/${transaction.tool_id}`} className="fw-bold">
                        {transaction.tool_number}
                      </Link>
                    </td>
                    <td>{transaction.serial_number || 'N/A'}</td>
                    <td>{transaction.description || 'N/A'}</td>
                    <td>{transaction.user_name}</td>
                    <td>
                      <Button
                        as={Link}
                        to={`/tools/${transaction.tool_id}`}
                        variant="info"
                        size="sm"
                      >
                        <i className="bi bi-eye me-1"></i>
                        View Tool
                      </Button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" className="text-center py-4">
                    No recent transactions found.
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

export default RecentTransactions;
