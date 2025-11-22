import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import NewChemicalForm from '../components/chemicals/NewChemicalForm';

const NewChemicalPageNew = () => {
  const { user } = useSelector((state) => state.auth);
  const isAuthorized = user?.is_admin || user?.department === 'Materials';

  // Redirect if user doesn't have permission
  if (!isAuthorized) {
    return <Navigate to="/chemicals" replace />;
  }

  return (
    <div className="w-full space-y-6">
      <h1 className="text-3xl font-bold tracking-tight text-foreground">Add New Chemical</h1>
      <NewChemicalForm />
    </div>
  );
};

export default NewChemicalPageNew;
