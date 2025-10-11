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
import ProtectedRoute, { AdminRoute } from './components/auth/ProtectedRoute';

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
import AdminDashboardPage from './pages/AdminDashboardPage';
import CalibrationManagement from './pages/CalibrationManagement';
import ToolCalibrationForm from './pages/ToolCalibrationForm';
import CalibrationStandardForm from './pages/CalibrationStandardForm';
import CalibrationDetailPage from './pages/CalibrationDetailPage';

// Component to handle root route - show landing page for unauthenticated, dashboard for authenticated
const RootRoute = () => {
  const { isAuthenticated } = useSelector((state) => state.auth);

  if (isAuthenticated) {
    return (
      <ProtectedRoute>
        <MainLayout>
          <UserDashboardPage />
        </MainLayout>
      </ProtectedRoute>
    );
  }

  return <LandingPage />;
};

function App() {
  const dispatch = useDispatch();
  const { theme } = useSelector((state) => state.theme);

  useEffect(() => {
    // Try to fetch current user on app load
    dispatch(fetchCurrentUser());
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
          <ProtectedRoute>
            <MainLayout>
              <ToolsManagement />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/tools/new" element={
          <ProtectedRoute>
            <MainLayout>
              <NewToolPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/tools/:id" element={
          <ProtectedRoute>
            <MainLayout>
              <ToolDetailPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/tools/:id/edit" element={
          <ProtectedRoute>
            <MainLayout>
              <EditToolPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/checkout/:id" element={
          <ProtectedRoute>
            <MainLayout>
              <CheckoutPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/checkouts" element={
          <ProtectedRoute>
            <MainLayout>
              <CheckoutsPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/my-checkouts" element={
          <ProtectedRoute>
            <MainLayout>
              <UserCheckoutsPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/checkouts/all" element={
          <ProtectedRoute>
            <MainLayout>
              <AllCheckoutsPage />
            </MainLayout>
          </ProtectedRoute>
        } />


        <Route path="/reports" element={
          <ProtectedRoute>
            <MainLayout>
              <ReportingPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/admin/dashboard" element={
          <AdminRoute>
            <MainLayout>
              <AdminDashboardPage />
            </MainLayout>
          </AdminRoute>
        } />

        <Route path="/profile" element={
          <ProtectedRoute>
            <ProfilePageNew />
          </ProtectedRoute>
        } />

        {/* Chemical routes */}
        <Route path="/chemicals" element={
          <ProtectedRoute>
            <MainLayout>
              <ChemicalsManagement />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/chemicals/new" element={
          <ProtectedRoute>
            <MainLayout>
              <NewChemicalPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/chemicals/:id" element={
          <ProtectedRoute>
            <MainLayout>
              <ChemicalDetailPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/chemicals/:id/edit" element={
          <ProtectedRoute>
            <MainLayout>
              <EditChemicalPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/chemicals/:id/issue" element={
          <ProtectedRoute>
            <MainLayout>
              <ChemicalIssuePage />
            </MainLayout>
          </ProtectedRoute>
        } />

        {/* Calibration routes */}
        <Route path="/calibrations" element={
          <ProtectedRoute>
            <MainLayout>
              <CalibrationManagement />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/tools/:id/calibrations/new" element={
          <ProtectedRoute>
            <MainLayout>
              <ToolCalibrationForm />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/tools/:id/calibrations/:calibrationId" element={
          <ProtectedRoute>
            <MainLayout>
              <CalibrationDetailPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/calibration-standards" element={
          <ProtectedRoute>
            <MainLayout>
              <CalibrationManagement />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/calibration-standards/new" element={
          <ProtectedRoute>
            <MainLayout>
              <CalibrationStandardForm />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/calibration-standards/:id" element={
          <ProtectedRoute>
            <MainLayout>
              <CalibrationManagement />
            </MainLayout>
          </ProtectedRoute>
        } />

        <Route path="/calibration-standards/:id/edit" element={
          <ProtectedRoute>
            <MainLayout>
              <CalibrationStandardForm />
            </MainLayout>
          </ProtectedRoute>
        } />

        {/* Scanner route */}
        <Route path="/scanner" element={
          <ProtectedRoute>
            <MainLayout>
              <ScannerPage />
            </MainLayout>
          </ProtectedRoute>
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
