import { useState, useEffect, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Navigate } from 'react-router-dom';
import { Container, Row, Col, Card, Form, Button, Alert, Tabs, Tab, ListGroup } from 'react-bootstrap';
import { updateProfile, updateAvatar, changePassword, fetchUserActivity } from '../store/authSlice';
import MainLayout from '../components/common/MainLayout';
import LoadingSpinner from '../components/common/LoadingSpinner';
import PasswordStrengthMeter from '../components/common/PasswordStrengthMeter';

const ProfilePage = () => {
  const dispatch = useDispatch();
  const { user, loading, error, activityLogs } = useSelector((state) => state.auth);
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

  // Redirect if not authenticated
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  useEffect(() => {
    // Initialize form with user data
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

  useEffect(() => {
    // Fetch user activity logs when the activity tab is active
    if (activeTab === 'activity' && user) {
      dispatch(fetchUserActivity());
    }
  }, [activeTab, dispatch, user]);

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
      setAvatarFile(file);

      // Create a preview URL
      const previewUrl = URL.createObjectURL(file);
      setAvatarPreview(previewUrl);
    }
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setSuccessMessage('');

    try {
      await dispatch(updateProfile(formData)).unwrap();
      setSuccessMessage('Profile updated successfully!');

      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);
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
      setSuccessMessage('Avatar updated successfully!');
      setAvatarFile(null);

      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);
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

      setSuccessMessage('Password changed successfully!');
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });
      setPasswordValid(false);

      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);
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
                  {user?.is_admin
                    ? 'Administrator'
                    : user?.department === 'Materials'
                      ? 'Materials (Tool Manager)'
                      : user?.department || 'Regular User'}
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
              <Card.Header className="bg-light">
                <Tabs
                  activeKey={activeTab}
                  onSelect={(k) => setActiveTab(k)}
                  className="mb-0"
                >
                  <Tab eventKey="profile" title="Profile Information">
                    {/* Profile tab content is rendered below */}
                  </Tab>
                  <Tab eventKey="password" title="Change Password">
                    {/* Password tab content is rendered below */}
                  </Tab>
                  <Tab eventKey="activity" title="Activity Log">
                    {/* Activity tab content is rendered below */}
                  </Tab>
                </Tabs>
              </Card.Header>

              <Card.Body>
                {activeTab === 'profile' && (
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
                )}

                {activeTab === 'password' && (
                  <Form onSubmit={handlePasswordSubmit}>
                    {passwordError && (
                      <Alert variant="danger" className="mb-3">
                        {passwordError}
                      </Alert>
                    )}

                    <Form.Group className="mb-3">
                      <Form.Label>Current Password</Form.Label>
                      <Form.Control
                        type="password"
                        name="currentPassword"
                        value={passwordData.currentPassword}
                        onChange={handlePasswordChange}
                        required
                      />
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>New Password</Form.Label>
                      <Form.Control
                        type="password"
                        name="newPassword"
                        value={passwordData.newPassword}
                        onChange={handlePasswordChange}
                        required
                      />
                      <PasswordStrengthMeter
                        password={passwordData.newPassword}
                        onValidationChange={handlePasswordValidationChange}
                      />
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>Confirm New Password</Form.Label>
                      <Form.Control
                        type="password"
                        name="confirmPassword"
                        value={passwordData.confirmPassword}
                        onChange={handlePasswordChange}
                        required
                      />
                    </Form.Group>

                    <div className="d-grid">
                      <Button
                        type="submit"
                        variant="primary"
                        disabled={loading}
                      >
                        {loading ? 'Changing...' : 'Change Password'}
                      </Button>
                    </div>
                  </Form>
                )}

                {activeTab === 'activity' && (
                  <>
                    {loading ? (
                      <LoadingSpinner />
                    ) : activityLogs && activityLogs.length > 0 ? (
                      <ListGroup variant="flush">
                        {activityLogs.map((log) => (
                          <ListGroup.Item key={log.id} className="py-3">
                            <div className="d-flex justify-content-between align-items-center">
                              <div>
                                <h6 className="mb-1">{log.activity_type.replace('_', ' ')}</h6>
                                <p className="text-muted mb-0 small">{log.description}</p>
                              </div>
                              <small className="text-muted">
                                {new Date(log.timestamp).toLocaleString()}
                              </small>
                            </div>
                          </ListGroup.Item>
                        ))}
                      </ListGroup>
                    ) : (
                      <p className="text-center py-4">No activity logs found.</p>
                    )}
                  </>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </MainLayout>
  );
};

export default ProfilePage;
