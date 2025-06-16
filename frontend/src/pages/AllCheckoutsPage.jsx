import { Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import AllCheckouts from '../components/checkouts/AllCheckouts';

const AllCheckoutsPage = () => {

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
