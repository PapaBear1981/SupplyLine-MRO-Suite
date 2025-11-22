import { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Wrench, AlertCircle } from 'lucide-react';
import LoginForm from '../components/auth/LoginForm';
import ForcedPasswordChangeModal from '../components/auth/ForcedPasswordChangeModal';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { clearPasswordChangeRequired } from '../store/authSlice';

const LoginPageNew = () => {
  const { isAuthenticated, user, passwordChangeRequired, passwordChangeData } = useSelector((state) => state.auth);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const [showPasswordChangeModal, setShowPasswordChangeModal] = useState(false);
  const [sessionTimeoutMessage, setSessionTimeoutMessage] = useState('');

  // Get the redirect path from location state or default to dashboard
  const from = location.state?.from?.pathname || '/';

  // Handle password change required state
  useEffect(() => {
    if (passwordChangeRequired && passwordChangeData) {
      setShowPasswordChangeModal(true);
    }
  }, [passwordChangeRequired, passwordChangeData]);

  useEffect(() => {
    // Only redirect if user is authenticated AND we have user data
    // This prevents redirect loops during initial auth check
    if (isAuthenticated && user) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, user, navigate, from]);

  useEffect(() => {
    if (location.state?.sessionTimeoutMessage) {
      setSessionTimeoutMessage(location.state.sessionTimeoutMessage);
    } else {
      setSessionTimeoutMessage('');
    }
  }, [location.state]);

  const handlePasswordChanged = () => {
    // Password was successfully changed
    // The backend returns user data and sets cookies
    setShowPasswordChangeModal(false);
    dispatch(clearPasswordChangeRequired());

    // Redirect to dashboard
    navigate('/dashboard', { replace: true });
  };

  return (
    <>
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-4">
        <div className="w-full max-w-md">
          <Card className="shadow-2xl border-2">
            <CardHeader className="space-y-4 text-center pb-6">
              <div className="mx-auto w-16 h-16 rounded-full bg-primary/10 dark:bg-primary/20 flex items-center justify-center">
                <Wrench className="w-8 h-8 text-primary" />
              </div>
              <div>
                <CardTitle className="text-3xl font-bold tracking-tight">
                  SupplyLine MRO Suite
                </CardTitle>
                <CardDescription className="text-base mt-2">
                  Tool Inventory Management System
                </CardDescription>
              </div>
            </CardHeader>

            <CardContent className="space-y-6">
              {sessionTimeoutMessage && (
                <Alert variant="warning" className="border-yellow-200 dark:border-yellow-800">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{sessionTimeoutMessage}</AlertDescription>
                </Alert>
              )}

              <LoginForm />

              <div className="text-center text-sm text-muted-foreground">
                Don't have an account?{' '}
                <Link
                  to="/register"
                  className="font-medium text-primary hover:underline underline-offset-4 transition-colors"
                >
                  Register here
                </Link>
              </div>
            </CardContent>
          </Card>

          {/* Footer */}
          <p className="mt-6 text-center text-xs text-muted-foreground">
            © {new Date().getFullYear()} SupplyLine MRO Suite. All rights reserved.
          </p>
        </div>
      </div>

      {/* Forced Password Change Modal */}
      {passwordChangeData && (
        <ForcedPasswordChangeModal
          show={showPasswordChangeModal}
          employeeNumber={passwordChangeData.employeeNumber}
          currentPassword={passwordChangeData.password}
          onPasswordChanged={handlePasswordChanged}
        />
      )}
    </>
  );
};

export default LoginPageNew;
