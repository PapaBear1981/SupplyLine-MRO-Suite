import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import ChemicalIssueForm from '../components/chemicals/ChemicalIssueForm';

const ChemicalIssuePageNew = () => {
  const { user } = useSelector((state) => state.auth);
  const isAuthorized = user?.is_admin || user?.department === 'Materials';

  // Redirect if user doesn't have permission
  if (!isAuthorized) {
    return <Navigate to="/chemicals" replace />;
  }

  return (
    <div className="w-full space-y-6">
      <h1 className="text-3xl font-bold tracking-tight text-foreground">Issue Chemical</h1>
      <ChemicalIssueForm />
    </div>
  );
};

export default ChemicalIssuePageNew;
