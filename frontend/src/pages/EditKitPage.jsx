import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import EditKitForm from '../components/kits/EditKitForm';

const EditKitPage = () => {
  const { user } = useSelector((state) => state.auth);
  const isAuthorized = user?.is_admin || user?.department === 'Materials';
  
  // Redirect if user doesn't have permission
  if (!isAuthorized) {
    return <Navigate to="/kits" replace />;
  }
  
  return (
    <div className="w-100">
      <h1 className="mb-4">Edit Kit</h1>
      <EditKitForm />
    </div>
  );
};

export default EditKitPage;

