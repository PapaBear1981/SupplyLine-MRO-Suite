import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { fetchCurrentUser } from './store/authSlice';

// Import Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css';

// Import Help Provider
import { HelpProvider } from './context/HelpContext';

// Import components
import MainLayout from './components/common/MainLayout';
import ProtectedRoute, { AdminRoute, PermissionRoute } from './components/auth/ProtectedRoute';

// Import pages
import LandingPage from './pages/LandingPage';
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
import ErrorHandlingTestPage from './pages/ErrorHandlingTestPage';
// CYCLE COUNT SYSTEM - TEMPORARILY DISABLED
// =========================================
// The cycle count system imports have been disabled due to production issues.
//
// REASON FOR DISABLING:
// - GitHub Issue #366: Cycle count system completely non-functional
// - Backend API endpoints missing/broken causing frontend errors
// - Users experiencing "Unable to Load Cycle Count System" messages
// - System instability affecting overall application performance
//
// WHAT WAS DISABLED:
// - All cycle count page imports
// - All cycle count component imports
// - All cycle count routing (see routes section below)
// - Navigation menu items (see MainLayout.jsx)
//
// TO RE-ENABLE IN THE FUTURE:
// 1. Uncomment all imports below
// 2. Uncomment all cycle count routes in the Routes section
// 3. Ensure backend cycle count routes are enabled (see backend/routes.py)
// 4. Verify cycle count database tables exist and are properly structured
// 5. Test all cycle count functionality end-to-end
// 6. Update navigation menu (see MainLayout.jsx)
//
// DISABLED DATE: 2025-06-22
// GITHUB ISSUE: #366
// RELATED BACKEND FILE: backend/routes.py (register_cycle_count_routes disabled)
//
// import CycleCountDashboardPage from './pages/CycleCountDashboardPage';
// import CycleCountScheduleForm from './components/cycleCount/CycleCountScheduleForm';
// import CycleCountBatchForm from './components/cycleCount/CycleCountBatchForm';
// import CycleCountScheduleDetailPage from './pages/CycleCountScheduleDetailPage';
// import CycleCountBatchDetailPage from './pages/CycleCountBatchDetailPage';
// import CycleCountDiscrepancyDetailPage from './pages/CycleCountDiscrepancyDetailPage';
// import CycleCountItemCountPage from './pages/CycleCountItemCountPage';
// import CycleCountMobilePage from './pages/CycleCountMobilePage';

import ReportingPage from './pages/ReportingPage';
import ChemicalsManagement from './pages/ChemicalsManagement';
import ChemicalDetailPage from './pages/ChemicalDetailPage';
import NewChemicalPage from './pages/NewChemicalPage';
import EditChemicalPage from './pages/EditChemicalPage';
import ChemicalIssuePage from './pages/ChemicalIssuePage';
import ChemicalReturnPage from './pages/ChemicalReturnPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import CalibrationManagement from './pages/CalibrationManagement';
import ToolCalibrationForm from './pages/ToolCalibrationForm';
import CalibrationStandardForm from './pages/CalibrationStandardForm';
import CalibrationDetailPage from './pages/CalibrationDetailPage';
import KitsManagement from './pages/KitsManagement';
import KitWizard from './components/kits/KitWizard';
import KitDetailPage from './pages/KitDetailPage';
import EditKitPage from './pages/EditKitPage';
import KitMobileInterface from './pages/KitMobileInterface';
import AircraftTypeManagement from './components/admin/AircraftTypeManagement';
import WarehousesManagement from './pages/WarehousesManagement';
import ItemHistoryPage from './pages/ItemHistoryPage';

// Component to handle root route - show landing page for unauthenticated, dashboard for authenticated
const RootRoute = () => {
  const { isAuthenticated, user } = useSelector((state) => state.auth);

  // If authenticated and we have user data, redirect to dashboard
  if (isAuthenticated && user) {
    return <Navigate to="/dashboard" replace />;
  }

  // Otherwise show landing page
  return <LandingPage />;
};

function App() {
  const dispatch = useDispatch();
  const { theme } = useSelector((state) => state.theme);

  useEffect(() => {
    // Always try to fetch current user on app load to check for existing session
    // This will silently fail if no valid session exists (user not logged in)
    dispatch(fetchCurrentUser()).catch(() => {
      // Silently ignore - user is not authenticated
    });
  }, [dispatch]);

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute('data-bs-theme', theme);
  }, [theme]);

  return (
    <HelpProvider>
      <Router>
        <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Root route - Landing page for unauthenticated, Dashboard for authenticated */}
        <Route path="/" element={<RootRoute />} />

        <Route path="/dashboard" element={
          <ProtectedRoute>
            <MainLayout>
              <UserDashboardPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/tools" element={
          <PermissionRoute permission="page.tools">
            <MainLayout>
              <ToolsManagement />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/tools/new" element={
          <PermissionRoute permission="page.tools">
            <MainLayout>
              <NewToolPage />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/tools/:id" element={
          <PermissionRoute permission="page.tools">
            <MainLayout>
              <ToolDetailPage />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/tools/:id/edit" element={
          <PermissionRoute permission="page.tools">
            <MainLayout>
              <EditToolPage />
            </MainLayout>
          </PermissionRoute>
        } />

        {/* NOTE: /checkouts route MUST come before /checkout/:id to avoid matching issues */}
        <Route path="/checkouts" element={
          <PermissionRoute permission="page.my_checkouts">
            <MainLayout>
              <CheckoutsPage />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/checkout/:id" element={
          <PermissionRoute permission="page.checkouts">
            <MainLayout>
              <CheckoutPage />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/my-checkouts" element={
          <PermissionRoute permission="page.my_checkouts">
            <MainLayout>
              <UserCheckoutsPage />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/checkouts/all" element={
          <PermissionRoute permission="page.checkouts" fallbackPath="/checkouts">
            <MainLayout>
              <AllCheckoutsPage />
            </MainLayout>
          </PermissionRoute>
        } />


        <Route path="/reports" element={
          <ProtectedRoute requirePermission={null}>
            <MainLayout>
              <ReportingPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/admin/dashboard" element={
          <PermissionRoute permission="page.admin_dashboard">
            <MainLayout>
              <AdminDashboardPage />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/admin/aircraft-types" element={
          <PermissionRoute permission="page.aircraft_types">
            <MainLayout>
              <AircraftTypeManagement />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/warehouses" element={
          <PermissionRoute permission="page.warehouses">
            <MainLayout>
              <WarehousesManagement />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/profile" element={
          <PermissionRoute permission="page.profile">
            <ProfilePageNew />
          </PermissionRoute>
        } />

        {/* Item History Lookup */}
        <Route path="/history" element={
          <ProtectedRoute>
            <MainLayout>
              <ItemHistoryPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        {/* Chemical routes */}
        <Route path="/chemicals" element={
          <PermissionRoute permission="page.chemicals">
            <MainLayout>
              <ChemicalsManagement />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/chemicals/new" element={
          <PermissionRoute permission="page.chemicals">
            <MainLayout>
              <NewChemicalPage />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/chemicals/:id" element={
          <PermissionRoute permission="page.chemicals">
            <MainLayout>
              <ChemicalDetailPage />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/chemicals/:id/edit" element={
          <PermissionRoute permission="page.chemicals">
            <MainLayout>
              <EditChemicalPage />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/chemicals/:id/issue" element={
          <PermissionRoute permission="page.chemicals">
            <MainLayout>
              <ChemicalIssuePage />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/chemicals/:id/return" element={
          <PermissionRoute permission="page.chemicals">
            <MainLayout>
              <ChemicalReturnPage />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/chemicals/return" element={
          <PermissionRoute permission="page.chemicals">
            <MainLayout>
              <ChemicalReturnPage />
            </MainLayout>
          </PermissionRoute>
        } />

        {/* Calibration routes */}
        <Route path="/calibrations" element={
          <PermissionRoute permission="page.calibrations">
            <MainLayout>
              <CalibrationManagement />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/tools/:id/calibrations/new" element={
          <PermissionRoute permission="page.calibrations">
            <MainLayout>
              <ToolCalibrationForm />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/tools/:id/calibrations/:calibrationId" element={
          <PermissionRoute permission="page.calibrations">
            <MainLayout>
              <CalibrationDetailPage />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/calibration-standards" element={
          <PermissionRoute permission="page.calibrations">
            <MainLayout>
              <CalibrationManagement />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/calibration-standards/new" element={
          <PermissionRoute permission="page.calibrations">
            <MainLayout>
              <CalibrationStandardForm />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/calibration-standards/:id" element={
          <PermissionRoute permission="page.calibrations">
            <MainLayout>
              <CalibrationManagement />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/calibration-standards/:id/edit" element={
          <PermissionRoute permission="page.calibrations">
            <MainLayout>
              <CalibrationStandardForm />
            </MainLayout>
          </PermissionRoute>
        } />

        {/* Scanner route */}
        <Route path="/scanner" element={
          <PermissionRoute permission="page.scanner">
            <MainLayout>
              <ScannerPage />
            </MainLayout>
          </PermissionRoute>
        } />

        {/* Kit routes */}
        <Route path="/kits" element={
          <PermissionRoute permission="page.kits">
            <MainLayout>
              <KitsManagement />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/kits/new" element={
          <PermissionRoute permission="page.kits">
            <MainLayout>
              <KitWizard />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/kits/:id/edit" element={
          <PermissionRoute permission="page.kits">
            <MainLayout>
              <EditKitPage />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/kits/:id" element={
          <PermissionRoute permission="page.kits">
            <MainLayout>
              <KitDetailPage />
            </MainLayout>
          </PermissionRoute>
        } />

        <Route path="/kits/mobile" element={
          <PermissionRoute permission="page.kits">
            <KitMobileInterface />
          </PermissionRoute>
        } />

        {/* CYCLE COUNT ROUTES - TEMPORARILY DISABLED */}
        {/* ========================================== */}
        {/* All cycle count routes have been disabled due to GitHub Issue #366 */}
        {/* */}
        {/* REASON FOR DISABLING: */}
        {/* - Backend cycle count API endpoints are non-functional */}
        {/* - Missing database tables causing system errors */}
        {/* - Users experiencing "Resource not found" errors */}
        {/* - Production stability issues */}
        {/* */}
        {/* ROUTES DISABLED: */}
        {/* - /cycle-counts/schedules/new - Create new schedule */}
        {/* - /cycle-counts/schedules/:id/edit - Edit schedule */}
        {/* - /cycle-counts/schedules/:id - View schedule details */}
        {/* - /cycle-counts/batches/new - Create new batch */}
        {/* - /cycle-counts/batches/:id/edit - Edit batch */}
        {/* - /cycle-counts/batches/:id - View batch details */}
        {/* - /cycle-counts/items/:id/count - Count items */}
        {/* - /cycle-counts/discrepancies/:id - View discrepancies */}
        {/* - /cycle-counts/schedules - Schedules dashboard */}
        {/* - /cycle-counts/batches - Batches dashboard */}
        {/* - /cycle-counts/discrepancies - Discrepancies dashboard */}
        {/* - /cycle-counts - Main cycle count dashboard */}
        {/* - /cycle-counts/mobile - Mobile cycle count interface */}
        {/* */}
        {/* TO RE-ENABLE: */}
        {/* 1. Uncomment all route definitions below */}
        {/* 2. Uncomment cycle count imports at top of file */}
        {/* 3. Enable backend routes in backend/routes.py */}
        {/* 4. Ensure database tables are created */}
        {/* 5. Test all functionality thoroughly */}
        {/* */}
        {/* DISABLED DATE: 2025-06-22 */}
        {/* GITHUB ISSUE: #366 */}
        {/* */}
        {/* Cycle Count Form Routes - More specific routes first */}
        {/* <Route path="/cycle-counts/schedules/new" element={
          <ProtectedRoute>
            <MainLayout>
              <CycleCountScheduleForm />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/cycle-counts/schedules/:id/edit" element={
          <ProtectedRoute>
            <MainLayout>
              <CycleCountScheduleForm />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/cycle-counts/schedules/:id" element={
          <ProtectedRoute>
            <MainLayout>
              <CycleCountScheduleDetailPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/cycle-counts/batches/new" element={
          <ProtectedRoute>
            <MainLayout>
              <CycleCountBatchForm />
            </MainLayout>
          </ProtectedRoute>
        } /> */}

        {/* <Route path="/cycle-counts/batches/:id/edit" element={
          <ProtectedRoute>
            <MainLayout>
              <CycleCountBatchForm />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/cycle-counts/batches/:id" element={
          <ProtectedRoute>
            <MainLayout>
              <CycleCountBatchDetailPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/cycle-counts/items/:id/count" element={
          <ProtectedRoute>
            <MainLayout>
              <CycleCountItemCountPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/cycle-counts/discrepancies/:id" element={
          <ProtectedRoute>
            <MainLayout>
              <CycleCountDiscrepancyDetailPage />
            </MainLayout>
          </ProtectedRoute>
        } /> */}

        {/* General Cycle Count routes */}
        {/* <Route path="/cycle-counts/schedules" element={
          <ProtectedRoute>
            <MainLayout>
              <CycleCountDashboardPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/cycle-counts/batches" element={
          <ProtectedRoute>
            <MainLayout>
              <CycleCountDashboardPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/cycle-counts/discrepancies" element={
          <ProtectedRoute>
            <MainLayout>
              <CycleCountDashboardPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/cycle-counts" element={
          <ProtectedRoute>
            <MainLayout>
              <CycleCountDashboardPage />
            </MainLayout>
          </ProtectedRoute>
        } /> */}

        {/* Mobile Cycle Count route */}
        {/* <Route path="/cycle-counts/mobile" element={
          <ProtectedRoute>
            <CycleCountMobilePage />
          </ProtectedRoute>
        } /> */}

        {/* Redirect any unknown routes to dashboard */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      </Router>
    </HelpProvider>
  );
}

export default App;
