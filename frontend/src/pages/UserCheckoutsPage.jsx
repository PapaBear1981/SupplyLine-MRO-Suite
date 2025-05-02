import { Card } from 'react-bootstrap';
import UserCheckouts from '../components/checkouts/UserCheckouts';

const UserCheckoutsPage = () => {
  return (
    <div className="w-100">
      <h1 className="mb-4">My Checkouts</h1>
      <UserCheckouts />
    </div>
  );
};

export default UserCheckoutsPage;
