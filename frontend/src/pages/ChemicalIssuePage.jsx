import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import ChemicalIssueForm from '../components/chemicals/ChemicalIssueForm';

const ChemicalIssuePage = () => {
  const { user } = useSelector((state) => state.auth);
  const isAuthorized = user?.is_admin || user?.department === 'Materials';
  
  // Redirect if user doesn't have permission
  if (!isAuthorized) {
    return <Navigate to="/chemicals" replace />;
  }
  
  return (
    <div className="w-100">
      <h1 className="mb-4">Issue Chemical</h1>
      <ChemicalIssueForm />
    </div>
  );
};

export default ChemicalIssuePage;
