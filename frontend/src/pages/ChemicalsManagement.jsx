import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Button, Tabs, Tab } from 'react-bootstrap';
import { Link, Navigate } from 'react-router-dom';
import ChemicalList from '../components/chemicals/ChemicalList';
import ArchivedChemicalsList from '../components/chemicals/ArchivedChemicalsList';
import { fetchChemicals, fetchArchivedChemicals } from '../store/chemicalsSlice';

const ChemicalsManagement = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const isAuthorized = user?.is_admin || user?.department === 'Materials';
  const [activeTab, setActiveTab] = useState('active');

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
        <Button as={Link} to="/chemicals/new" variant="success" size="lg">
          <i className="bi bi-plus-circle me-2"></i>
          Add New Chemical
        </Button>
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
    </div>
  );
};

export default ChemicalsManagement;
