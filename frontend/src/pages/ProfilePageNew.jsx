import { useState, useEffect, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Navigate } from 'react-router-dom';
import { Container, Row, Col, Card, Form, Button, Alert, Nav } from 'react-bootstrap';
import { updateProfile, updateAvatar, changePassword } from '../store/authSlice';
import MainLayout from '../components/common/MainLayout';
import PasswordStrengthMeter from '../components/common/PasswordStrengthMeter';

const ProfilePageNew = () => {
  const dispatch = useDispatch();
  const { user, loading, error } = useSelector((state) => state.auth);
  const [activeTab, setActiveTab] = useState('profile');
  const [formData, setFormData] = useState({
    name: '',
    department: '',
  });
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [avatarFile, setAvatarFile] = useState(null);
  const [avatarPreview, setAvatarPreview] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [passwordValid, setPasswordValid] = useState(false);
  const fileInputRef = useRef(null);

  // Initialize form with user data
  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || '',
        department: user.department || '',
      });

      // Set avatar preview if user has an avatar
      if (user.avatar) {
        setAvatarPreview(user.avatar);
      }
    }
  }, [user]);

  // Clean up object URLs when component unmounts or when avatarPreview changes
  useEffect(() => {
    return () => {
      // Only revoke if it's an object URL (not a server URL)
      if (avatarPreview && avatarPreview.startsWith('blob:')) {
        URL.revokeObjectURL(avatarPreview);
      }
    };
  }, [avatarPreview]);

  // Redirect if not authenticated
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData({
      ...passwordData,
      [name]: value,
    });
  };

  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
      if (!validTypes.includes(file.type)) {
        alert('Please select a valid image file (JPEG, PNG, or GIF)');
        return;
      }

      // Validate file size (max 5MB)
      const maxSize = 5 * 1024 * 1024; // 5MB in bytes
      if (file.size > maxSize) {
        alert('File size exceeds 5MB limit');
        return;
      }

      setAvatarFile(file);

      // Create a preview URL
      const previewUrl = URL.createObjectURL(file);
      setAvatarPreview(previewUrl);
    }
  };

  // Reusable function for showing temporary success messages
  const showTemporarySuccessMessage = (message) => {
    setSuccessMessage(message);
    setTimeout(() => {
      setSuccessMessage('');
    }, 3000);
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setSuccessMessage('');

    try {
      await dispatch(updateProfile(formData)).unwrap();
      showTemporarySuccessMessage('Profile updated successfully!');
    } catch (err) {
      console.error('Failed to update profile:', err);
    }
  };

  const handleAvatarSubmit = async (e) => {
    e.preventDefault();
    setSuccessMessage('');

    if (!avatarFile) {
      return;
    }

    const formData = new FormData();
    formData.append('avatar', avatarFile);

    try {
      await dispatch(updateAvatar(formData)).unwrap();
      showTemporarySuccessMessage('Avatar updated successfully!');
      setAvatarFile(null);
    } catch (err) {
      console.error('Failed to update avatar:', err);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setSuccessMessage('');
    setPasswordError('');

    // Validate passwords match
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setPasswordError('New passwords do not match');
      return;
    }

    // Validate password strength
    if (!passwordValid) {
      setPasswordError('Password does not meet security requirements');
      return;
    }

    try {
      await dispatch(changePassword({
        current_password: passwordData.currentPassword,
        new_password: passwordData.newPassword
      })).unwrap();

      showTemporarySuccessMessage('Password changed successfully!');
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });
      setPasswordValid(false);
    } catch (err) {
      console.error('Failed to change password:', err);
      setPasswordError(err.message || 'Failed to change password');
    }
  };

  const handlePasswordValidationChange = (isValid) => {
    setPasswordValid(isValid);
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  // Render profile tab content
  const renderProfileTab = () => (
    <Form onSubmit={handleProfileSubmit}>
      <Form.Group className="mb-3">
        <Form.Label>Employee Number</Form.Label>
        <Form.Control
          type="text"
          value={user?.employee_number || ''}
          disabled
        />
        <Form.Text className="text-muted">
          Employee number cannot be changed
        </Form.Text>
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label>Name</Form.Label>
        <Form.Control
          type="text"
          name="name"
          value={formData.name}
          onChange={handleInputChange}
          required
        />
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label>Department</Form.Label>
        <Form.Control
          type="text"
          name="department"
          value={formData.department}
          onChange={handleInputChange}
        />
      </Form.Group>

      <div className="d-grid">
        <Button
          type="submit"
          variant="primary"
          disabled={loading}
        >
          {loading ? 'Saving...' : 'Save Changes'}
        </Button>
      </div>
    </Form>
  );

  // Render password tab content
  const renderPasswordTab = () => (
    <Form onSubmit={handlePasswordSubmit}>
      <Alert variant="info" className="mb-4">
        <i className="bi bi-shield-lock me-2"></i>
        <strong>Password Security:</strong> Choose a strong, unique password to protect your account.
      </Alert>

      {passwordError && (
        <Alert variant="danger" className="mb-3">
          <i className="bi bi-exclamation-triangle me-2"></i>
          {passwordError}
        </Alert>
      )}

      <Form.Group className="mb-3">
        <Form.Label>
          <i className="bi bi-key me-2"></i>
          Current Password
        </Form.Label>
        <Form.Control
          type="password"
          name="currentPassword"
          value={passwordData.currentPassword}
          onChange={handlePasswordChange}
          placeholder="Enter your current password"
          required
        />
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label>
          <i className="bi bi-shield-check me-2"></i>
          New Password
        </Form.Label>
        <Form.Control
          type="password"
          name="newPassword"
          value={passwordData.newPassword}
          onChange={handlePasswordChange}
          placeholder="Enter your new password"
          required
        />
        <PasswordStrengthMeter
          password={passwordData.newPassword}
          onValidationChange={handlePasswordValidationChange}
        />
      </Form.Group>

      <Form.Group className="mb-4">
        <Form.Label>
          <i className="bi bi-shield-check me-2"></i>
          Confirm New Password
        </Form.Label>
        <Form.Control
          type="password"
          name="confirmPassword"
          value={passwordData.confirmPassword}
          onChange={handlePasswordChange}
          placeholder="Confirm your new password"
          required
        />
        {passwordData.confirmPassword && passwordData.newPassword !== passwordData.confirmPassword && (
          <Form.Text className="text-danger">
            <i className="bi bi-x-circle me-1"></i>
            Passwords do not match
          </Form.Text>
        )}
        {passwordData.confirmPassword && passwordData.newPassword === passwordData.confirmPassword && passwordData.newPassword && (
          <Form.Text className="text-success">
            <i className="bi bi-check-circle me-1"></i>
            Passwords match
          </Form.Text>
        )}
        <Form.Text className="text-muted d-block mt-2">
          Passwords must meet all requirements above and cannot match your last 5 passwords.
        </Form.Text>
      </Form.Group>

      <div className="d-grid">
        <Button
          type="submit"
          variant="primary"
          size="lg"
          disabled={loading || !passwordValid || passwordData.newPassword !== passwordData.confirmPassword}
        >
          {loading ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Changing Password...
            </>
          ) : (
            <>
              <i className="bi bi-shield-lock-fill me-2"></i>
              Change Password
            </>
          )}
        </Button>
      </div>
    </Form>
  );



  return (
    <MainLayout>
      <Container>
        <h1 className="mb-4">My Profile</h1>

        {error && (
          <Alert variant="danger" className="mb-4">
            {error}
          </Alert>
        )}

        {successMessage && (
          <Alert variant="success" className="mb-4">
            {successMessage}
          </Alert>
        )}

        <Row>
          <Col md={4} className="mb-4">
            <Card className="shadow-sm">
              <Card.Body className="text-center">
                <div className="position-relative mb-4 mx-auto" style={{ width: '150px', height: '150px' }}>
                  {avatarPreview ? (
                    <img
                      src={avatarPreview}
                      alt="User Avatar"
                      className="rounded-circle img-fluid"
                      style={{ width: '150px', height: '150px', objectFit: 'cover' }}
                    />
                  ) : (
                    <div
                      className="rounded-circle bg-primary d-flex align-items-center justify-content-center text-white"
                      style={{ width: '150px', height: '150px', fontSize: '4rem' }}
                    >
                      {user?.name?.charAt(0) || 'U'}
                    </div>
                  )}
                </div>

                <h4 className="mb-1">{user?.name}</h4>
                <p className="text-muted mb-3">
                  {(() => {
                    if (user?.is_admin) return 'Administrator';
                    if (user?.department === 'Materials') return 'Materials (Tool Manager)';
                    return user?.department || 'Regular User';
                  })()}
                </p>

                <Form onSubmit={handleAvatarSubmit}>
                  <Form.Group controlId="avatar" className="mb-3">
                    <Form.Control
                      type="file"
                      ref={fileInputRef}
                      onChange={handleAvatarChange}
                      accept="image/*"
                      className="d-none"
                    />
                    <div className="d-grid gap-2">
                      <Button
                        variant="outline-primary"
                        onClick={triggerFileInput}
                        className="mb-2"
                      >
                        <i className="bi bi-camera me-2"></i>
                        Change Avatar
                      </Button>

                      {avatarFile && (
                        <Button
                          type="submit"
                          variant="primary"
                          disabled={loading}
                        >
                          {loading ? 'Uploading...' : 'Upload Avatar'}
                        </Button>
                      )}
                    </div>
                  </Form.Group>
                </Form>
              </Card.Body>
            </Card>
          </Col>

          <Col md={8}>
            <Card className="shadow-sm">
              <Card.Header>
                <div className="nav nav-tabs card-header-tabs">
                  <button
                    className={`nav-link ${activeTab === 'profile' ? 'active' : ''}`}
                    onClick={() => setActiveTab('profile')}
                  >
                    <i className="bi bi-person me-2"></i>
                    Profile Information
                  </button>
                  <button
                    className={`nav-link ${activeTab === 'password' ? 'active' : ''}`}
                    onClick={() => setActiveTab('password')}
                  >
                    <i className="bi bi-shield-lock me-2"></i>
                    Change Password
                  </button>
                </div>
              </Card.Header>
              <Card.Body>
                {activeTab === 'profile' && renderProfileTab()}
                {activeTab === 'password' && renderPasswordTab()}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </MainLayout>
  );
};

export default ProfilePageNew;
