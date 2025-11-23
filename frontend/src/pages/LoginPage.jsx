import { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Wrench, AlertCircle } from 'lucide-react';
import LoginForm from '../components/auth/LoginForm';
import ForcedPasswordChangeModal from '../components/auth/ForcedPasswordChangeModal';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { clearPasswordChangeRequired } from '../store/authSlice';

const LoginPage = () => {
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
      {/* Background Image with Overlay */}
      <div className="fixed inset-0">
        {/* Background Image */}
        <div
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1513002749550-c59d786b8e6c?q=80&w=2574&auto=format&fit=crop')`,
          }}
        />
        {/* Dark Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-slate-950/95 via-slate-900/80 to-transparent" />
      </div>

      {/* Main Container */}
      <div className="min-h-screen flex items-center relative">
        <div className="container mx-auto px-4 lg:px-8">
          <div className="max-w-md animate-fade-in">

            {/* Logo and Nav */}
            <div className="flex items-center justify-between mb-16">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-500 flex items-center justify-center">
                  <Wrench className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-semibold text-white">SupplyLine MRO</span>
              </div>
            </div>

            {/* Main Content Card */}
            <div className="bg-slate-900/60 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl animate-slide-up">

              {/* Title */}
              <div className="mb-8">
                <p className="text-sm text-slate-400 mb-2">START FOR FREE</p>
                <h1 className="text-3xl font-bold text-white mb-2">
                  Sign in to your account
                </h1>
                <p className="text-slate-400">
                  Already a member?{' '}
                  <Link to="/register" className="text-blue-400 hover:text-blue-300 transition-colors">
                    Log in
                  </Link>
                </p>
              </div>

              {/* Session timeout alert */}
              {sessionTimeoutMessage && (
                <Alert variant="warning" className="mb-6 border-yellow-500/20 bg-yellow-500/10">
                  <AlertCircle className="h-4 w-4 text-yellow-500" />
                  <AlertDescription className="text-yellow-200">{sessionTimeoutMessage}</AlertDescription>
                </Alert>
              )}

              {/* Login Form */}
              <LoginForm />

            </div>

            {/* Footer */}
            <p className="mt-6 text-center text-sm text-slate-500">
              Don't have an account?{' '}
              <Link to="/register" className="text-blue-400 hover:text-blue-300 transition-colors">
                Sign up
              </Link>
            </p>
          </div>
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

export default LoginPage;
