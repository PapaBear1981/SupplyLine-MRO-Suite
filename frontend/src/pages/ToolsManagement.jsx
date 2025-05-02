import { useSelector } from 'react-redux';
import { Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import ToolList from '../components/tools/ToolList';

const ToolsManagement = () => {
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin || user?.department === 'Materials';

  return (
    <div className="w-100">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
        <h1 className="mb-0">Tool Inventory</h1>
        {isAdmin && (
          <Button as={Link} to="/tools/new" variant="success" size="lg">
            <i className="bi bi-plus-circle me-2"></i>
            Add New Tool
          </Button>
        )}
      </div>

      <ToolList />
    </div>
  );
};

export default ToolsManagement;
