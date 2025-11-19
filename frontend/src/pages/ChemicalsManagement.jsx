import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Button, Tabs, Tab } from 'react-bootstrap';
import { Navigate } from 'react-router-dom';
import ChemicalList from '../components/chemicals/ChemicalList';
import ArchivedChemicalsList from '../components/chemicals/ArchivedChemicalsList';
import BulkImportChemicals from '../components/chemicals/BulkImportChemicals';
import ChemicalReturnModal from '../components/chemicals/ChemicalReturnModal';
import ChemicalWorkflowDashboard from '../components/chemicals/ChemicalWorkflowDashboard';
import ActivityFeed from '../components/chemicals/ActivityFeed';
import TransactionResearchCenter from '../components/chemicals/TransactionResearchCenter';
import useHotkeys from '../hooks/useHotkeys';
import {
  fetchChemicals,
  fetchArchivedChemicals
} from '../store/chemicalsSlice';

const ChemicalsManagement = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);
  const isAuthorized = user?.is_admin || user?.department === 'Materials';
  const [activeTab, setActiveTab] = useState('workflow');
  const [showReturnModal, setShowReturnModal] = useState(false);

  // Page-specific hotkeys
  useHotkeys({
    'n': () => {
      if (isAuthorized) {
        navigate('/chemicals/new');
      }
    }
  }, {
    enabled: isAuthorized,
    deps: [navigate, isAuthorized]
  });

  // Fetch data based on active tab
  useEffect(() => {
    if (activeTab === 'active') {
      dispatch(fetchChemicals());
    } else if (activeTab === 'archived') {
      dispatch(fetchArchivedChemicals());
    }
    // Workflow tab loads its own data via ChemicalWorkflowDashboard
  }, [dispatch, activeTab]);

  // Redirect if user doesn't have permission
  if (!isAuthorized) {
    return <Navigate to="/tools" replace />;
  }

  return (
    <div className="w-100">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
        <h1 className="mb-0">Chemical Inventory</h1>
        <div className="d-flex gap-2">
          {user?.is_admin && <BulkImportChemicals />}
          <Button
            onClick={() => setShowReturnModal(true)}
            variant="warning"
            size="lg"
          >
            <i className="bi bi-arrow-return-left me-2"></i>
            Return Chemical
          </Button>
          <Button onClick={() => navigate('/chemicals/new')} variant="success" size="lg">
            <i className="bi bi-plus-circle me-2"></i>
            Add New Chemical
          </Button>
        </div>
      </div>

      <Tabs
        activeKey={activeTab}
        onSelect={(k) => setActiveTab(k)}
        className="mb-4"
      >
        <Tab eventKey="workflow" title={<><i className="bi bi-kanban me-2"></i>Workflow Dashboard</>}>
          <ChemicalWorkflowDashboard />
          <div className="mt-4">
            <ActivityFeed limit={20} />
          </div>
        </Tab>
        <Tab eventKey="active" title={<><i className="bi bi-list-ul me-2"></i>All Chemicals</>}>
          <ChemicalList />
        </Tab>
        <Tab eventKey="transactions" title={<><i className="bi bi-search me-2"></i>Transaction Research</>}>
          <TransactionResearchCenter />
        </Tab>
        <Tab eventKey="archived" title={<><i className="bi bi-archive me-2"></i>Archived</>}>
          <ArchivedChemicalsList />
        </Tab>
      </Tabs>

      <ChemicalReturnModal
        show={showReturnModal}
        onHide={() => setShowReturnModal(false)}
      />
    </div>
  );
};

export default ChemicalsManagement;
