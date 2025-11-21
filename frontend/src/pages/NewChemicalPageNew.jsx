import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import NewChemicalFormNew from '../components/chemicals/NewChemicalFormNew';

const NewChemicalPageNew = () => {
  const { user } = useSelector((state) => state.auth);
  const isAuthorized = user?.is_admin || user?.department === 'Materials';

  // Redirect if user doesn't have permission
  if (!isAuthorized) {
    return <Navigate to="/chemicals" replace />;
  }

  return (
    <div className="w-full min-h-screen bg-background p-6">
      <div className="max-w-4xl mx-auto">
        <NewChemicalFormNew />
      </div>
    </div>
  );
};

export default NewChemicalPageNew;
