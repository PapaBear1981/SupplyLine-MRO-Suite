import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import EditToolForm from '../components/tools/EditToolForm';

const EditToolPageNew = () => {
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin || user?.department === 'Materials';

  // Redirect if user doesn't have permission
  if (!isAdmin) {
    return <Navigate to="/tools" replace />;
  }

  return (
    <div className="w-full space-y-6">
      <h1 className="text-3xl font-bold tracking-tight text-foreground">Edit Tool</h1>
      <EditToolForm />
    </div>
  );
};

export default EditToolPageNew;
