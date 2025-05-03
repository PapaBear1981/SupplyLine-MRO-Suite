import { useSelector } from 'react-redux';
import { Button } from 'react-bootstrap';
import { Link, Navigate } from 'react-router-dom';
import AllCheckouts from '../components/checkouts/AllCheckouts';

const AllCheckoutsPage = () => {
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin || user?.department === 'Materials';

  // Redirect if user doesn't have permission
  if (!isAdmin) {
    return <Navigate to="/checkouts" />;
  }

  return (
    <div className="w-100">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
        <h1 className="mb-0">All Active Checkouts</h1>
        <div>
          <Button as={Link} to="/checkouts" variant="secondary" size="lg">
            Back to My Checkouts
          </Button>
        </div>
      </div>

      <AllCheckouts />
    </div>
  );
};

export default AllCheckoutsPage;
