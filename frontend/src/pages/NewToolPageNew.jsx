import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import NewToolForm from '../components/tools/NewToolForm';

const NewToolPageNew = () => {
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin || user?.department === 'Materials';

  // Redirect if user doesn't have permission
  if (!isAdmin) {
    return <Navigate to="/tools" replace />;
  }

  return (
    <div className="w-full space-y-6">
      <h1 className="text-3xl font-bold tracking-tight text-foreground">Add New Tool</h1>
      <NewToolForm />
    </div>
  );
};

export default NewToolPageNew;
