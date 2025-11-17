import { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Card, Typography, Alert, ConfigProvider, theme as antTheme } from 'antd';
import { ToolOutlined, SafetyCertificateOutlined } from '@ant-design/icons';
import LoginForm from '../components/auth/LoginForm';
import ForcedPasswordChangeModal from '../components/auth/ForcedPasswordChangeModal';
import { clearPasswordChangeRequired } from '../store/authSlice';
import { enterpriseTheme, enterpriseDarkTheme } from '../theme/enterpriseTheme';
import { APP_VERSION } from '../utils/version';

const { Title, Text, Paragraph } = Typography;

const LoginPage = () => {
  const { isAuthenticated, user, passwordChangeRequired, passwordChangeData } = useSelector((state) => state.auth);
  const { theme: currentTheme } = useSelector((state) => state.theme);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const [showPasswordChangeModal, setShowPasswordChangeModal] = useState(false);
  const [sessionTimeoutMessage, setSessionTimeoutMessage] = useState('');

  const from = location.state?.from?.pathname || '/';

  useEffect(() => {
    if (passwordChangeRequired && passwordChangeData) {
      setShowPasswordChangeModal(true);
    }
  }, [passwordChangeRequired, passwordChangeData]);

  useEffect(() => {
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
    setShowPasswordChangeModal(false);
    dispatch(clearPasswordChangeRequired());
    navigate('/dashboard', { replace: true });
  };

  const isDarkMode = currentTheme === 'dark';
  const selectedTheme = isDarkMode ? enterpriseDarkTheme : enterpriseTheme;

  return (
    <ConfigProvider
      theme={{
        ...selectedTheme,
        algorithm: isDarkMode ? antTheme.darkAlgorithm : antTheme.defaultAlgorithm,
      }}
    >
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: isDarkMode
            ? 'linear-gradient(135deg, #0d1b2a 0%, #16325c 100%)'
            : 'linear-gradient(135deg, #16325c 0%, #0d2240 100%)',
          padding: 24,
        }}
      >
        <div style={{ width: '100%', maxWidth: 440 }}>
          <Card
            style={{
              borderRadius: 8,
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
              border: 'none',
            }}
          >
            <div style={{ textAlign: 'center', marginBottom: 32 }}>
              <div
                style={{
                  width: 72,
                  height: 72,
                  margin: '0 auto 16px',
                  background: 'linear-gradient(135deg, #0070d2 0%, #0062b3 100%)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 4px 12px rgba(0, 112, 210, 0.4)',
                }}
              >
                <ToolOutlined style={{ fontSize: 36, color: '#ffffff' }} />
              </div>
              <Title level={2} style={{ margin: 0, color: '#16325c', fontWeight: 700 }}>
                SupplyLine MRO Suite
              </Title>
              <Text type="secondary" style={{ fontSize: 14 }}>
                Enterprise Asset Management System
              </Text>
            </div>

            {sessionTimeoutMessage && (
              <Alert
                message="Session Expired"
                description={sessionTimeoutMessage}
                type="warning"
                showIcon
                style={{ marginBottom: 24 }}
              />
            )}

            <LoginForm />

            <div style={{ textAlign: 'center', marginTop: 24 }}>
              <Paragraph style={{ marginBottom: 8 }}>
                <Text type="secondary">Don&apos;t have an account? </Text>
                <Link to="/register" style={{ color: '#0070d2', fontWeight: 500 }}>
                  Request Access
                </Link>
              </Paragraph>
            </div>
          </Card>

          <div style={{ textAlign: 'center', marginTop: 24 }}>
            <Text style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: 12 }}>
              <SafetyCertificateOutlined style={{ marginRight: 4 }} />
              Secured Enterprise Application
            </Text>
            <br />
            <Text style={{ color: 'rgba(255, 255, 255, 0.4)', fontSize: 11 }}>
              Version {APP_VERSION}
            </Text>
          </div>
        </div>
      </div>

      {passwordChangeData && (
        <ForcedPasswordChangeModal
          show={showPasswordChangeModal}
          employeeNumber={passwordChangeData.employeeNumber}
          currentPassword={passwordChangeData.password}
          onPasswordChanged={handlePasswordChanged}
        />
      )}
    </ConfigProvider>
  );
};

export default LoginPage;
