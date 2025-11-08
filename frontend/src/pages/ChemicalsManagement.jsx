import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Button, Tabs, Tab } from 'react-bootstrap';
import { Navigate } from 'react-router-dom';
import ChemicalList from '../components/chemicals/ChemicalList';
import ArchivedChemicalsList from '../components/chemicals/ArchivedChemicalsList';
import BulkImportChemicals from '../components/chemicals/BulkImportChemicals';
import ChemicalReturnModal from '../components/chemicals/ChemicalReturnModal';
import {
  fetchChemicals,
  fetchArchivedChemicals
} from '../store/chemicalsSlice';

const ChemicalsManagement = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);
  const isAuthorized = user?.is_admin || user?.department === 'Materials';
  const [activeTab, setActiveTab] = useState('active');
  const [showReturnModal, setShowReturnModal] = useState(false);

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
        <Tab eventKey="active" title="Active Chemicals">
          <ChemicalList />
        </Tab>
        <Tab eventKey="archived" title="Archived Chemicals">
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
