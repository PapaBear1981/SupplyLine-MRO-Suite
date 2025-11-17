import { useSelector } from 'react-redux';
import { Button, Alert, Space } from 'antd';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  PlusCircleOutlined,
  ToolOutlined,
  UploadOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import EnterprisePageHeader from '../components/common/EnterprisePageHeader';
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
  useHotkeys(
    {
      n: () => {
        if (isAdmin) {
          navigate('/tools/new');
        }
      },
    },
    {
      enabled: isAdmin,
      deps: [navigate, isAdmin],
    }
  );

  const pageActions = [];

  if (isAdmin) {
    pageActions.push(
      {
        label: 'Calibration Management',
        icon: <SettingOutlined />,
        onClick: () => navigate('/calibrations'),
      },
      {
        label: 'Add New Tool',
        icon: <PlusCircleOutlined />,
        type: 'primary',
        onClick: () => navigate('/tools/new'),
      }
    );
  }

  return (
    <div className="enterprise-tools-management">
      {unauthorized && (
        <Alert
          message="Access Denied"
          description="You do not have permission to access the Admin Dashboard. This area is restricted to administrators only."
          type="error"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      <EnterprisePageHeader
        title="Tool Inventory Management"
        subtitle="View, search, and manage all tools in your organization's inventory"
        icon={<ToolOutlined />}
        breadcrumbs={[{ title: 'Tools' }]}
        actions={pageActions}
      />

      {isAdmin && (
        <div style={{ marginBottom: 16 }}>
          <BulkImportTools />
        </div>
      )}

      <div className="enterprise-card" style={{ padding: 0 }}>
        <ToolList />
      </div>
    </div>
  );
};

export default ToolsManagement;
