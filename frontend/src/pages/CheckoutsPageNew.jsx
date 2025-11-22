import { useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import UserCheckouts from '../components/checkouts/UserCheckouts';
import { Button } from '../components/ui/button';

const CheckoutsPageNew = () => {
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin || user?.department === 'Materials';

  return (
    <div className="w-full space-y-6">
      <div className="flex flex-wrap justify-between items-center gap-4">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">My Checkouts</h1>
        {isAdmin && (
          <Button asChild size="lg">
            <Link to="/checkouts/all">
              View All Active Checkouts
            </Link>
          </Button>
        )}
      </div>

      <UserCheckouts />
    </div>
  );
};

export default CheckoutsPageNew;
