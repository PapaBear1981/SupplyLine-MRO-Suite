import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Navigate } from 'react-router-dom';
import { Plus, ArrowLeft, FlaskConical } from 'lucide-react';

import ChemicalListNew from '../components/chemicals/ChemicalListNew';
import ArchivedChemicalsList from '../components/chemicals/ArchivedChemicalsList';
import BulkImportChemicals from '../components/chemicals/BulkImportChemicals';
import ChemicalReturnModal from '../components/chemicals/ChemicalReturnModal';
import useHotkeys from '../hooks/useHotkeys';
import {
  fetchChemicals,
  fetchArchivedChemicals
} from '../store/chemicalsSlice';

// UI Components
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
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
    <div className="w-full min-h-screen bg-background p-6">
      <div className="max-w-[1600px] mx-auto space-y-6">
        {/* Page Header */}
        <div className="flex flex-wrap justify-between items-center gap-4">
          <div className="flex items-center gap-3">
            <FlaskConical className="h-8 w-8 text-primary" />
            <h1 className="text-3xl font-bold tracking-tight">Chemical Inventory</h1>
          </div>
          <div className="flex gap-2 flex-wrap">
            {user?.is_admin && <BulkImportChemicals />}
            <Button
              onClick={() => setShowReturnModal(true)}
              variant="outline"
              size="lg"
              className="gap-2"
            >
              <ArrowLeft className="h-5 w-5" />
              Return Chemical
            </Button>
            <Button
              onClick={() => navigate('/chemicals/new')}
              size="lg"
              className="gap-2"
            >
              <Plus className="h-5 w-5" />
              Add New Chemical
            </Button>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full max-w-md grid-cols-2">
            <TabsTrigger value="active">Active Chemicals</TabsTrigger>
            <TabsTrigger value="archived">Archived Chemicals</TabsTrigger>
          </TabsList>

          <TabsContent value="active" className="mt-6">
            <ChemicalListNew />
          </TabsContent>

          <TabsContent value="archived" className="mt-6">
            <ArchivedChemicalsList />
          </TabsContent>
        </Tabs>

        {/* Return Modal */}
        <ChemicalReturnModal
          show={showReturnModal}
          onHide={() => setShowReturnModal(false)}
        />
      </div>
    </div>
  );
};

export default ChemicalsManagementNew;
