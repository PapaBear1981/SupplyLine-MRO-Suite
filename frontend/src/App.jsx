import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { fetchCurrentUser } from './store/authSlice';

// Import Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css';

// Import Help Provider
import { HelpProvider } from './context/HelpContext';

// Import Supabase services
import supabaseService from './services/supabase.js';
import syncService from './services/syncService.js';
import offlineStorage from './utils/offlineStorage.js';
import SupabaseConfig from './components/SupabaseConfig.jsx';

// Import components
import MainLayout from './components/common/MainLayout';
import ResponsiveLayout from './components/common/ResponsiveLayout';
import ProtectedRoute, { AdminRoute } from './components/auth/ProtectedRoute';

// Import pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePageNew from './pages/ProfilePageNew';
import UserDashboardPage from './pages/UserDashboardPage';
import ToolsManagement from './pages/ToolsManagement';
import ToolDetailPage from './pages/ToolDetailPage';
import NewToolPage from './pages/NewToolPage';
import EditToolPage from './pages/EditToolPage';
import CheckoutPage from './pages/CheckoutPage';
import UserCheckoutsPage from './pages/UserCheckoutsPage';
import CheckoutsPage from './pages/CheckoutsPage';
import AllCheckoutsPage from './pages/AllCheckoutsPage';
import ScannerPage from './pages/ScannerPage';
import CycleCountDashboardPage from './pages/CycleCountDashboardPage';
import CycleCountScheduleForm from './components/cycleCount/CycleCountScheduleForm';
import CycleCountBatchForm from './components/cycleCount/CycleCountBatchForm';
import CycleCountScheduleDetailPage from './pages/CycleCountScheduleDetailPage';
import CycleCountBatchDetailPage from './pages/CycleCountBatchDetailPage';
import CycleCountDiscrepancyDetailPage from './pages/CycleCountDiscrepancyDetailPage';
import CycleCountItemCountPage from './pages/CycleCountItemCountPage';
import CycleCountMobilePage from './pages/CycleCountMobilePage';

// Import mobile pages
import MobileUserDashboardPage from './pages/mobile/MobileUserDashboardPage';
import MobileToolsManagementPage from './pages/mobile/MobileToolsManagementPage';

import ReportingPage from './pages/ReportingPage';
import ChemicalsManagement from './pages/ChemicalsManagement';
import ChemicalDetailPage from './pages/ChemicalDetailPage';
import NewChemicalPage from './pages/NewChemicalPage';
import EditChemicalPage from './pages/EditChemicalPage';
import ChemicalIssuePage from './pages/ChemicalIssuePage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import CalibrationManagement from './pages/CalibrationManagement';
import ToolCalibrationForm from './pages/ToolCalibrationForm';
import CalibrationStandardForm from './pages/CalibrationStandardForm';
import CalibrationDetailPage from './pages/CalibrationDetailPage';

function App() {
  const dispatch = useDispatch();
  const { theme } = useSelector((state) => state.theme);
  const [showSupabaseConfig, setShowSupabaseConfig] = useState(false);
  const [supabaseInitialized, setSupabaseInitialized] = useState(false);

  useEffect(() => {
    // Initialize offline storage and Supabase
    const initializeServices = async () => {
      try {
        // Initialize offline storage
        await offlineStorage.initialize();
        console.log('✅ Offline storage initialized');

        // Try to initialize Supabase
        const supabaseReady = await supabaseService.initialize();
        if (supabaseReady) {
          console.log('✅ Supabase initialized');
          await syncService.initialize();
          console.log('✅ Sync service initialized');
          setSupabaseInitialized(true);
        } else {
          console.log('⚠️  Supabase not configured, showing config dialog');
          // Check if running in Electron to show config dialog
          if (window.electronAPI) {
            setShowSupabaseConfig(true);
          }
        }
      } catch (error) {
        console.error('Failed to initialize services:', error);
      }
    };

    initializeServices();

    // Try to fetch current user on app load
    dispatch(fetchCurrentUser());
  }, [dispatch]);

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute('data-bs-theme', theme);
  }, [theme]);

  const handleSupabaseConfigured = () => {
    setSupabaseInitialized(true);
    setShowSupabaseConfig(false);
  };

  return (
    <HelpProvider>
      <Router>
        {/* Supabase Configuration Modal */}
        <SupabaseConfig
          show={showSupabaseConfig}
          onHide={() => setShowSupabaseConfig(false)}
          onConfigured={handleSupabaseConfigured}
        />

        <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected routes - Dashboard as default landing page */}
        <Route path="/" element={
          <ProtectedRoute>
            <ResponsiveLayout mobileComponent={<MobileUserDashboardPage />}>
              <UserDashboardPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/dashboard" element={
          <ProtectedRoute>
            <ResponsiveLayout mobileComponent={<MobileUserDashboardPage />}>
              <UserDashboardPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/tools" element={
          <ProtectedRoute>
            <ResponsiveLayout mobileComponent={<MobileToolsManagementPage />}>
              <ToolsManagement />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/tools/new" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <NewToolPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/tools/:id" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <ToolDetailPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/tools/:id/edit" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <EditToolPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/checkout/:id" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CheckoutPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/checkouts" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CheckoutsPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/my-checkouts" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <UserCheckoutsPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/checkouts/all" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <AllCheckoutsPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />


        <Route path="/reports" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <ReportingPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/admin/dashboard" element={
          <AdminRoute>
            <ResponsiveLayout>
              <AdminDashboardPage />
            </ResponsiveLayout>
          </AdminRoute>
        } />

        <Route path="/profile" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <ProfilePageNew />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        {/* Chemical routes */}
        <Route path="/chemicals" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <ChemicalsManagement />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/chemicals/new" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <NewChemicalPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/chemicals/:id" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <ChemicalDetailPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/chemicals/:id/edit" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <EditChemicalPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/chemicals/:id/issue" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <ChemicalIssuePage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        {/* Calibration routes */}
        <Route path="/calibrations" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CalibrationManagement />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/tools/:id/calibrations/new" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <ToolCalibrationForm />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/tools/:id/calibrations/:calibrationId" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CalibrationDetailPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/calibration-standards" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CalibrationManagement />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/calibration-standards/new" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CalibrationStandardForm />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/calibration-standards/:id" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CalibrationManagement />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/calibration-standards/:id/edit" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CalibrationStandardForm />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        {/* Scanner route */}
        <Route path="/scanner" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <ScannerPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        {/* Cycle Count routes */}
        {/* Cycle Count Form Routes - More specific routes first */}
        <Route path="/cycle-counts/schedules/new" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CycleCountScheduleForm />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/cycle-counts/schedules/:id/edit" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CycleCountScheduleForm />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/cycle-counts/schedules/:id" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CycleCountScheduleDetailPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/cycle-counts/batches/new" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CycleCountBatchForm />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/cycle-counts/batches/:id/edit" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CycleCountBatchForm />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/cycle-counts/batches/:id" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CycleCountBatchDetailPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/cycle-counts/items/:id/count" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CycleCountItemCountPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/cycle-counts/discrepancies/:id" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CycleCountDiscrepancyDetailPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        {/* General Cycle Count routes */}
        <Route path="/cycle-counts/schedules" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CycleCountDashboardPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/cycle-counts/batches" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CycleCountDashboardPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/cycle-counts/discrepancies" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CycleCountDashboardPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        <Route path="/cycle-counts" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CycleCountDashboardPage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        {/* Mobile Cycle Count route */}
        <Route path="/cycle-counts/mobile" element={
          <ProtectedRoute>
            <ResponsiveLayout>
              <CycleCountMobilePage />
            </ResponsiveLayout>
          </ProtectedRoute>
        } />

        {/* Redirect any unknown routes to dashboard */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      </Router>
    </HelpProvider>
  );
}

export default App;
