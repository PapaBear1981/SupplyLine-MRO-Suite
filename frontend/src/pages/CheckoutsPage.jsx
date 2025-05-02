import { useSelector } from 'react-redux';
import { Button, Row, Col, Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import UserCheckouts from '../components/checkouts/UserCheckouts';

const CheckoutsPage = () => {
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin || user?.department === 'Materials';

  return (
    <div className="w-100">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
        <h1 className="mb-0">Checkouts Management</h1>
        {isAdmin && (
          <div>
            <Button as={Link} to="/checkouts/all" variant="info" size="lg" className="me-2">
              View All Checkouts
            </Button>
          </div>
        )}
      </div>

      <UserCheckouts />
    </div>
  );
};

export default CheckoutsPage;
