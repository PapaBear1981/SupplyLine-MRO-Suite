import { useSelector } from 'react-redux';
import { Link, Navigate } from 'react-router-dom';
import AllCheckouts from '../components/checkouts/AllCheckouts';
import { Button } from '../components/ui/button';

const AllCheckoutsPageNew = () => {
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin || user?.department === 'Materials';

  // Redirect if user doesn't have permission
  if (!isAdmin) {
    return <Navigate to="/checkouts" />;
  }

  return (
    <div className="w-full space-y-6">
      <div className="flex flex-wrap justify-between items-center gap-4">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">All Active Checkouts</h1>
        <Button asChild variant="secondary" size="lg">
          <Link to="/checkouts">
            Back to My Checkouts
          </Link>
        </Button>
      </div>

      <AllCheckouts />
    </div>
  );
};

export default AllCheckoutsPageNew;
