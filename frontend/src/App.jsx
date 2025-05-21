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

        {/* Protected routes - Dashboard as default landing page */}
        <Route path="/" element={
          <ProtectedRoute>
            <MainLayout>
              <UserDashboardPage />
            </MainLayout>
          </ProtectedRoute>
        } />

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

        {/* Redirect any unknown routes to dashboard */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      </Router>
    </HelpProvider>
  );
}

export default App;
