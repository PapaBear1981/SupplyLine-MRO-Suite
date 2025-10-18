import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Tabs, Tab, Alert } from 'react-bootstrap';
import ChemicalsNeedingReorder from './ChemicalsNeedingReorder';
import ChemicalsOnOrder from './ChemicalsOnOrder';
import ChemicalsExpiringSoon from './ChemicalsExpiringSoon';
import LoadingSpinner from '../common/LoadingSpinner';
import { 
  fetchChemicalsNeedingReorder, 
  fetchChemicalsOnOrder, 
  fetchChemicalsExpiringSoon 
} from '../../store/chemicalsSlice';

const ReorderManagement = () => {
  const dispatch = useDispatch();
  const [activeTab, setActiveTab] = useState('needing-reorder');
  const { 
    chemicalsNeedingReorder, 
    chemicalsOnOrder, 
    chemicalsExpiringSoon,
    loading 
  } = useSelector((state) => state.chemicals);

  useEffect(() => {
    // Load data for all tabs
    dispatch(fetchChemicalsNeedingReorder());
    dispatch(fetchChemicalsOnOrder());
    dispatch(fetchChemicalsExpiringSoon());
  }, [dispatch]);

  if (loading && !chemicalsNeedingReorder.length && !chemicalsOnOrder.length && !chemicalsExpiringSoon.length) {
    return <LoadingSpinner />;
  }

  return (
    <Card className="shadow-sm">
      <Card.Header>
        <h5 className="mb-0">Chemical Reorder Management</h5>
      </Card.Header>
      <Card.Body>
        <Tabs
          activeKey={activeTab}
          onSelect={(k) => setActiveTab(k)}
          className="mb-4"
        >
          <Tab eventKey="needing-reorder" title={`Needs Reorder (${chemicalsNeedingReorder.length})`}>
            <ChemicalsNeedingReorder />
          </Tab>
          <Tab eventKey="on-order" title={`On Order (${chemicalsOnOrder.length})`}>
            <ChemicalsOnOrder />
          </Tab>
          <Tab eventKey="expiring-soon" title={`Expiring Soon (${chemicalsExpiringSoon.length})`}>
            <ChemicalsExpiringSoon />
          </Tab>
        </Tabs>
      </Card.Body>
    </Card>
  );
};

export default ReorderManagement;
