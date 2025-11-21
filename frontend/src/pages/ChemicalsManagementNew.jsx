import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate, Navigate } from 'react-router-dom';
import { Plus, RotateCcw, FlaskConical } from 'lucide-react';

import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import ChemicalListNew from '../components/chemicals/ChemicalListNew';
import ArchivedChemicalsList from '../components/chemicals/ArchivedChemicalsList';
import BulkImportChemicals from '../components/chemicals/BulkImportChemicals';
import ChemicalReturnModal from '../components/chemicals/ChemicalReturnModal';
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
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Chemical Inventory</h1>
          <p className="text-muted-foreground">Manage chemicals, materials, and substances.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {user?.is_admin && <BulkImportChemicals />}
          <Button
            onClick={() => setShowReturnModal(true)}
            variant="outline"
            size="default"
          >
            <RotateCcw className="mr-2 h-4 w-4" />
            Return Chemical
          </Button>
          <Button onClick={() => navigate('/chemicals/new')} variant="default" size="default">
            <Plus className="mr-2 h-4 w-4" />
            Add New Chemical
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="active">
            <FlaskConical className="mr-2 h-4 w-4" />
            Active Chemicals
          </TabsTrigger>
          <TabsTrigger value="archived">
            Archived Chemicals
          </TabsTrigger>
        </TabsList>
        <TabsContent value="active" className="mt-6">
          <ChemicalListNew />
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
