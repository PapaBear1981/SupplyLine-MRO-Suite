import { useSelector } from 'react-redux';
import { Button, Alert, Badge } from 'react-bootstrap';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import ToolList from '../components/tools/ToolList';
import BulkImportTools from '../components/tools/BulkImportTools';
import useHotkeys from '../hooks/useHotkeys';

const ToolsManagement = () => {
  const { user } = useSelector((state) => state.auth);
  const location = useLocation();
  const navigate = useNavigate();
  const isAdmin = user?.is_admin || user?.department === 'Materials';
  const unauthorized = location.state?.unauthorized;

  // Page-specific hotkeys
  useHotkeys({
    'n': () => {
      if (isAdmin) {
        navigate('/tools/new');
      }
    }
  }, {
    enabled: isAdmin,
    deps: [navigate, isAdmin]
  });

  return (
    <div className="w-100">
      {/* Show unauthorized message if redirected from admin page */}
      {unauthorized && (
        <Alert variant="danger" className="mb-4">
          <Alert.Heading>Access Denied</Alert.Heading>
          <p>
            You do not have permission to access the Admin Dashboard. This area is restricted to administrators only.
          </p>
        </Alert>
      )}

      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
        <h1 className="mb-0">Tool Inventory</h1>
        <div className="d-flex gap-2">
          {isAdmin && (
            <Button as={Link} to="/calibrations" variant="outline-primary" size="lg">
              <i className="bi bi-tools me-2"></i>
              Calibration Management
            </Button>
          )}
          {isAdmin && <BulkImportTools />}
          {isAdmin && (
            <Button as={Link} to="/tools/new" variant="success" size="lg">
              <i className="bi bi-plus-circle me-2"></i>
              Add New Tool
            </Button>
          )}
        </div>
      </div>

      <ToolList />
    </div>
  );
};

export default ToolsManagement;
