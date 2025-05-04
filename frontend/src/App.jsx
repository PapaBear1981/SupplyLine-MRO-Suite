import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { fetchCurrentUser } from './store/authSlice';

// Import Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css';

// Import components
import MainLayout from './components/common/MainLayout';
import ProtectedRoute from './components/auth/ProtectedRoute';

// Import pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ToolsManagement from './pages/ToolsManagement';
import ToolDetailPage from './pages/ToolDetailPage';
import NewToolPage from './pages/NewToolPage';
import EditToolPage from './pages/EditToolPage';
import CheckoutPage from './pages/CheckoutPage';
import UserCheckoutsPage from './pages/UserCheckoutsPage';
import CheckoutsPage from './pages/CheckoutsPage';
import AllCheckoutsPage from './pages/AllCheckoutsPage';
import UserManagementPage from './pages/UserManagementPage';

function App() {
  const dispatch = useDispatch();

  useEffect(() => {
    // Try to fetch current user on app load
    dispatch(fetchCurrentUser());
  }, [dispatch]);

  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected routes - Redirect from dashboard to tools */}
        <Route path="/" element={<Navigate to="/tools" replace />} />

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

        <Route path="/users" element={
          <ProtectedRoute>
            <MainLayout>
              <UserManagementPage />
            </MainLayout>
          </ProtectedRoute>
        } />

        {/* Redirect any unknown routes to dashboard */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
