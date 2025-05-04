import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import EditToolForm from '../components/tools/EditToolForm';

const EditToolPage = () => {
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin || user?.department === 'Materials';
  
  // Redirect if user doesn't have permission
  if (!isAdmin) {
    return <Navigate to="/tools" replace />;
  }
  
  return (
    <div className="w-100">
      <h1 className="mb-4">Edit Tool</h1>
      <EditToolForm />
    </div>
  );
};

export default EditToolPage;
