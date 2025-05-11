import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import EditChemicalForm from '../components/chemicals/EditChemicalForm';

const EditChemicalPage = () => {
  const { user } = useSelector((state) => state.auth);
  const isAuthorized = user?.is_admin || user?.department === 'Materials';
  
  // Redirect if user doesn't have permission
  if (!isAuthorized) {
    return <Navigate to="/chemicals" replace />;
  }
  
  return (
    <div className="w-100">
      <h1 className="mb-4">Edit Chemical</h1>
      <EditChemicalForm />
    </div>
  );
};

export default EditChemicalPage;
