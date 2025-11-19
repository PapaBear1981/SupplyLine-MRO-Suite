import React, { useState, useEffect } from 'react';
import { Modal, Button, Tab, Tabs, Row, Col, Card, Badge, Table, Spinner, Form, Alert, InputGroup } from 'react-bootstrap';
import { toast } from 'react-toastify';
import api from '../../services/api';
import { useSelector } from 'react-redux';

const UserProfileModal = ({ show, onHide, userId, onUserUpdated, initialTab = 'overview' }) => {
    const [activeTab, setActiveTab] = useState(initialTab);
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [checkouts, setCheckouts] = useState([]);
    const [history, setHistory] = useState([]);
    const [roles, setRoles] = useState([]);
    const [allRoles, setAllRoles] = useState([]);

    // Admin form state
    const [formData, setFormData] = useState({
        name: '',
        department: '',
        email: '',
        is_active: true,
        is_admin: false,
        password: ''
    });

    // Get current user from Redux to check permissions
    const { user: currentUser } = useSelector((state) => state.auth);
    const isAdmin = currentUser?.is_admin;
    const canManageUsers = isAdmin || (currentUser?.permissions || []).includes('user.manage');

    useEffect(() => {
        if (show && userId) {
            fetchUserData();
            setActiveTab(initialTab);
        }
    }, [show, userId, initialTab]);

    const fetchUserData = async () => {
        setLoading(true);
        try {
            // Fetch basic user details
            const userRes = await api.get(`/users/${userId}`);
            setUser(userRes.data);
            setFormData({
                name: userRes.data.name,
                department: userRes.data.department || '',
                email: userRes.data.email || '',
                is_active: userRes.data.is_active,
                is_admin: userRes.data.is_admin,
                password: ''
            });

            // Fetch roles if admin
            if (canManageUsers) {
                const [rolesRes, allRolesRes] = await Promise.all([
                    api.get(`/users/${userId}/roles`),
                    api.get('/roles')
                ]);
                setRoles(rolesRes.data);
                setAllRoles(allRolesRes.data);
            }

            // Fetch active checkouts (mock endpoint for now if not exists, or filter from main checkouts)
            try {
                const checkoutsRes = await api.get('/checkouts');
                const userCheckouts = checkoutsRes.data.filter(c => c.user_id === userId && !c.return_date);
                setCheckouts(userCheckouts);

                const userHistory = checkoutsRes.data.filter(c => c.user_id === userId && c.return_date);
                setHistory(userHistory);
            } catch (err) {
                console.warn("Could not fetch checkouts:", err);
            }

        } catch (error) {
            console.error('Error fetching user details:', error);
            toast.error('Failed to load user profile.');
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateUser = async (e) => {
        e.preventDefault();
        try {
            const updateData = { ...formData };
            if (!updateData.password) delete updateData.password;

            const response = await api.put(`/users/${userId}`, updateData);
            setUser(response.data);
            if (onUserUpdated) onUserUpdated(response.data);
            toast.success('User profile updated successfully');
        } catch (error) {
            console.error('Error updating user:', error);
            toast.error(error.response?.data?.error || 'Failed to update user');
        }
    };

    const handleRoleChange = async (roleId, checked) => {
        try {
            const newRoles = checked
                ? [...roles.map(r => r.id), roleId]
                : roles.filter(r => r.id !== roleId).map(r => r.id);

            const response = await api.put(`/users/${userId}/roles`, { roles: newRoles });
            setRoles(response.data);
            toast.success('User roles updated');
        } catch (error) {
            console.error('Error updating roles:', error);
            toast.error('Failed to update roles');
        }
    };

    const handlePasswordReset = async () => {
        if (!formData.password) {
            toast.error("Please enter a new password");
            return;
        }
        await handleUpdateUser({ preventDefault: () => { } });
        setFormData({ ...formData, password: '' });
    }

    if (!show) return null;

    return (
        <Modal show={show} onHide={onHide} size="lg" centered>
            <Modal.Header closeButton className="border-0 pb-0">
                <Modal.Title>User Profile</Modal.Title>
            </Modal.Header>
            <Modal.Body className="pt-0">
                {loading ? (
                    <div className="text-center p-5">
                        <Spinner animation="border" />
                    </div>
                ) : user ? (
                    <>
                        <div className="d-flex align-items-center mb-4 mt-3">
                            <div
                                className="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center me-3 shadow-sm"
                                style={{ width: '64px', height: '64px', fontSize: '1.75rem' }}
                            >
                                {user.name.charAt(0).toUpperCase()}
                            </div>
                            <div>
                                <h4 className="mb-0">{user.name}</h4>
                                <div className="text-muted mb-1">
                                    <span className="font-monospace me-2">{user.employee_number}</span>
                                    <Badge bg="light" text="dark" className="border">{user.department || 'No Dept'}</Badge>
                                </div>
                                <div>
                                    {user.is_active ? (
                                        <Badge bg="success">Active</Badge>
                                    ) : (
                                        <Badge bg="secondary">Inactive</Badge>
                                    )}
                                    {user.is_admin && <Badge bg="primary" className="ms-1">Admin</Badge>}
                                </div>
                            </div>
                        </div>

                        <Tabs
                            activeKey={activeTab}
                            onSelect={(k) => setActiveTab(k)}
                            className="mb-3"
                        >
                            <Tab eventKey="overview" title="Overview">
                                <h6 className="mb-3">Active Checkouts ({checkouts.length})</h6>
                                {checkouts.length === 0 ? (
                                    <Alert variant="light" className="text-center text-muted border">
                                        No active checkouts.
                                    </Alert>
                                ) : (
                                    <Table size="sm" hover responsive>
                                        <thead>
                                            <tr>
                                                <th>Tool</th>
                                                <th>Checked Out</th>
                                                <th>Due</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {checkouts.map(c => (
                                                <tr key={c.id}>
                                                    <td>
                                                        <div className="fw-bold">{c.tool_number}</div>
                                                        <div className="small text-muted">{c.description}</div>
                                                    </td>
                                                    <td>{new Date(c.checkout_date).toLocaleDateString()}</td>
                                                    <td>
                                                        {c.expected_return_date ? (
                                                            <span className={new Date(c.expected_return_date) < new Date() ? 'text-danger fw-bold' : ''}>
                                                                {new Date(c.expected_return_date).toLocaleDateString()}
                                                            </span>
                                                        ) : '-'}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </Table>
                                )}
                            </Tab>

                            <Tab eventKey="history" title="History">
                                <h6 className="mb-3">Transaction History</h6>
                                {history.length === 0 ? (
                                    <Alert variant="light" className="text-center text-muted border">
                                        No history found.
                                    </Alert>
                                ) : (
                                    <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                                        <Table size="sm" hover>
                                            <thead>
                                                <tr>
                                                    <th>Tool</th>
                                                    <th>Checked Out</th>
                                                    <th>Returned</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {history.map(c => (
                                                    <tr key={c.id}>
                                                        <td>
                                                            <div>{c.tool_number}</div>
                                                            <div className="small text-muted">{c.description}</div>
                                                        </td>
                                                        <td>{new Date(c.checkout_date).toLocaleDateString()}</td>
                                                        <td>{new Date(c.return_date).toLocaleDateString()}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </Table>
                                    </div>
                                )}
                            </Tab>

                            {canManageUsers && (
                                <Tab eventKey="admin" title="Admin Controls">
                                    <Row>
                                        <Col md={6}>
                                            <Card className="mb-3 h-100">
                                                <Card.Header>Account Details</Card.Header>
                                                <Card.Body>
                                                    <Form onSubmit={handleUpdateUser}>
                                                        <Form.Group className="mb-3">
                                                            <Form.Label>Full Name</Form.Label>
                                                            <Form.Control
                                                                type="text"
                                                                value={formData.name}
                                                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                                                required
                                                            />
                                                        </Form.Group>
                                                        <Form.Group className="mb-3">
                                                            <Form.Label>Department</Form.Label>
                                                            <Form.Control
                                                                type="text"
                                                                value={formData.department}
                                                                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                                                            />
                                                        </Form.Group>
                                                        <Form.Group className="mb-3">
                                                            <Form.Label>Email</Form.Label>
                                                            <Form.Control
                                                                type="email"
                                                                value={formData.email}
                                                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                                            />
                                                        </Form.Group>
                                                        <Form.Check
                                                            type="switch"
                                                            id="active-switch"
                                                            label="Account Active"
                                                            checked={formData.is_active}
                                                            onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                                                            className="mb-3"
                                                        />
                                                        <Form.Check
                                                            type="switch"
                                                            id="admin-switch"
                                                            label="Administrator Access"
                                                            checked={formData.is_admin}
                                                            onChange={(e) => setFormData({ ...formData, is_admin: e.target.checked })}
                                                            className="mb-3"
                                                        />
                                                        <Button type="submit" variant="primary" size="sm">Save Changes</Button>
                                                    </Form>
                                                </Card.Body>
                                            </Card>
                                        </Col>
                                        <Col md={6}>
                                            <Card className="mb-3">
                                                <Card.Header>Roles & Permissions</Card.Header>
                                                <Card.Body>
                                                    <div className="d-flex flex-column gap-2">
                                                        {allRoles.map(role => (
                                                            <Form.Check
                                                                key={role.id}
                                                                type="checkbox"
                                                                label={role.name}
                                                                checked={roles.some(r => r.id === role.id)}
                                                                onChange={(e) => handleRoleChange(role.id, e.target.checked)}
                                                            />
                                                        ))}
                                                    </div>
                                                </Card.Body>
                                            </Card>

                                            <Card className="mb-3 border-danger">
                                                <Card.Header className="bg-danger text-white">Security</Card.Header>
                                                <Card.Body>
                                                    <Form.Group className="mb-3">
                                                        <Form.Label>Reset Password</Form.Label>
                                                        <InputGroup>
                                                            <Form.Control
                                                                type="password"
                                                                placeholder="New password"
                                                                value={formData.password}
                                                                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                                            />
                                                            <Button variant="outline-danger" onClick={handlePasswordReset}>
                                                                Reset
                                                            </Button>
                                                        </InputGroup>
                                                    </Form.Group>

                                                    {user.account_locked && (
                                                        <div className="d-grid mt-3">
                                                            <Button variant="warning" onClick={async () => {
                                                                try {
                                                                    await api.post(`/users/${userId}/unlock`);
                                                                    toast.success('Account unlocked');
                                                                    fetchUserData();
                                                                } catch (e) {
                                                                    toast.error('Failed to unlock account');
                                                                }
                                                            }}>
                                                                <i className="bi bi-unlock me-2"></i>Unlock Account
                                                            </Button>
                                                        </div>
                                                    )}
                                                </Card.Body>
                                            </Card>
                                        </Col>
                                    </Row>
                                </Tab>
                            )}
                        </Tabs>
                    </>
                ) : (
                    <Alert variant="danger">User not found</Alert>
                )}
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={onHide}>Close</Button>
            </Modal.Footer>
        </Modal>
    );
};

export default UserProfileModal;
