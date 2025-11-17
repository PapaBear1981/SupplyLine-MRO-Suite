import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate, Navigate } from 'react-router-dom';
import { Tabs, Tab } from 'react-bootstrap';
import { ExperimentOutlined, PlusCircleOutlined, RollbackOutlined } from '@ant-design/icons';
import EnterprisePageHeader from '../components/common/EnterprisePageHeader';
import ChemicalList from '../components/chemicals/ChemicalList';
import ArchivedChemicalsList from '../components/chemicals/ArchivedChemicalsList';
import BulkImportChemicals from '../components/chemicals/BulkImportChemicals';
import ChemicalReturnModal from '../components/chemicals/ChemicalReturnModal';
import useHotkeys from '../hooks/useHotkeys';
import { fetchChemicals, fetchArchivedChemicals } from '../store/chemicalsSlice';

const ChemicalsManagement = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);
  const isAuthorized = user?.is_admin || user?.department === 'Materials';
  const [activeTab, setActiveTab] = useState('active');
  const [showReturnModal, setShowReturnModal] = useState(false);

  // Page-specific hotkeys
  useHotkeys(
    {
      n: () => {
        if (isAuthorized) {
          navigate('/chemicals/new');
        }
      },
    },
    {
      enabled: isAuthorized,
      deps: [navigate, isAuthorized],
    }
  );

  // Fetch data based on active tab
  useEffect(() => {
    if (activeTab === 'active') {
      dispatch(fetchChemicals());
    } else if (activeTab === 'archived') {
      dispatch(fetchArchivedChemicals());
    }
  }, [dispatch, activeTab]);

  // Redirect if user doesn't have permission
  if (!isAuthorized) {
    return <Navigate to="/tools" replace />;
  }

  const pageActions = [
    {
      label: 'Return Chemical',
      icon: <RollbackOutlined />,
      onClick: () => setShowReturnModal(true),
    },
    {
      label: 'Add New Chemical',
      icon: <PlusCircleOutlined />,
      type: 'primary',
      onClick: () => navigate('/chemicals/new'),
    },
  ];

  return (
    <div className="enterprise-chemicals-management">
      <EnterprisePageHeader
        title="Chemical Inventory Management"
        subtitle="Track, issue, and manage chemical inventory with safety compliance"
        icon={<ExperimentOutlined />}
        breadcrumbs={[{ title: 'Chemicals' }]}
        actions={pageActions}
      />

      {user?.is_admin && (
        <div style={{ marginBottom: 16 }}>
          <BulkImportChemicals />
        </div>
      )}

      <div className="enterprise-card">
        <Tabs activeKey={activeTab} onSelect={(k) => setActiveTab(k)} className="mb-4">
          <Tab eventKey="active" title="Active Chemicals">
            <ChemicalList />
          </Tab>
          <Tab eventKey="archived" title="Archived Chemicals">
            <ArchivedChemicalsList />
          </Tab>
        </Tabs>
      </div>

      <ChemicalReturnModal show={showReturnModal} onHide={() => setShowReturnModal(false)} />
    </div>
  );
};

export default ChemicalsManagement;
