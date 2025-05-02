import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import NewToolForm from '../components/tools/NewToolForm';

const NewToolPage = () => {
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin || user?.department === 'Materials';
  
  // Redirect if user doesn't have permission
  if (!isAdmin) {
    return <Navigate to="/tools" replace />;
  }
  
  return (
    <div className="w-100">
      <h1 className="mb-4">Add New Tool</h1>
      <NewToolForm />
    </div>
  );
};

export default NewToolPage;
