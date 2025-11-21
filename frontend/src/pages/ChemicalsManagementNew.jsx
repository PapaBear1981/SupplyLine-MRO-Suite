import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Navigate } from 'react-router-dom';
import { Plus, ArrowLeftRight, Upload } from 'lucide-react';
import ChemicalList from '../components/chemicals/ChemicalList';
import ArchivedChemicalsList from '../components/chemicals/ArchivedChemicalsList';
import BulkImportChemicals from '../components/chemicals/BulkImportChemicals';
import ChemicalReturnModal from '../components/chemicals/ChemicalReturnModal';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import useHotkeys from '../hooks/useHotkeys';
import {
  fetchChemicals,
  fetchArchivedChemicals
} from '../store/chemicalsSlice';

const ChemicalsManagementNew = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);
  const isAuthorized = user?.is_admin || user?.department === 'Materials';
  const [activeTab, setActiveTab] = useState('active');
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
  }, [dispatch, activeTab]);

  // Redirect if user doesn't have permission
  if (!isAuthorized) {
    return <Navigate to="/tools" replace />;
  }

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-3xl font-bold tracking-tight">Chemical Inventory</h1>
        <div className="flex flex-wrap gap-2">
          {user?.is_admin && <BulkImportChemicals />}
          <Button
            onClick={() => setShowReturnModal(true)}
            variant="outline"
            size="default"
            className="gap-2"
          >
            <ArrowLeftRight className="h-4 w-4" />
            Return Chemical
          </Button>
          <Button
            onClick={() => navigate('/chemicals/new')}
            size="default"
            className="gap-2"
          >
            <Plus className="h-4 w-4" />
            Add New Chemical
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList>
          <TabsTrigger value="active">Active Chemicals</TabsTrigger>
          <TabsTrigger value="archived">Archived Chemicals</TabsTrigger>
        </TabsList>

        <TabsContent value="active" className="mt-6">
          <ChemicalList />
        </TabsContent>

        <TabsContent value="archived" className="mt-6">
          <ArchivedChemicalsList />
        </TabsContent>
      </Tabs>

      <ChemicalReturnModal
        show={showReturnModal}
        onHide={() => setShowReturnModal(false)}
      />
    </div>
  );
};

export default ChemicalsManagementNew;
