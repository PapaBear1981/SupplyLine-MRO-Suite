import React, { useState, useEffect } from 'react';
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Table,
  Badge,
  Modal,
  Alert,
  ProgressBar,
  Spinner,
} from 'react-bootstrap';
import {
  FaDatabase,
  FaDownload,
  FaTrash,
  FaUndo,
  FaPlus,
  FaSync,
  FaCheckCircle,
  FaExclamationTriangle,
} from 'react-icons/fa';
import { formatDistanceToNow } from 'date-fns';

const DatabaseManagement = () => {
  const [backups, setBackups] = useState([]);
  const [loading, setLoading] = useState(false);
  const [healthData, setHealthData] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [restoreDialog, setRestoreDialog] = useState({ show: false, backup: null });
  const [deleteDialog, setDeleteDialog] = useState({ show: false, backup: null });

  useEffect(() => {
    loadBackups();
    checkHealth();
  }, []);

  const loadBackups = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/admin/database/backups', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) throw new Error('Failed to load backups');

      const data = await response.json();
      setBackups(data.backups || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const checkHealth = async () => {
    try {
      const response = await fetch('/api/admin/database/health', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) throw new Error('Failed to check database health');

      const data = await response.json();
      setHealthData(data);
    } catch (err) {
      console.error('Health check failed:', err);
    }
  };

  const createBackup = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch('/api/admin/database/backup', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ compress: true }),
      });

      const data = await response.json();

      if (!response.ok) throw new Error(data.message || 'Failed to create backup');

      setSuccess('Backup created successfully!');
      loadBackups();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRestore = async () => {
    if (!restoreDialog.backup) return;

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch('/api/admin/database/restore', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          backup_filename: restoreDialog.backup.filename,
          create_backup_before_restore: true,
        }),
      });

      const data = await response.json();

      if (!response.ok) throw new Error(data.message || 'Failed to restore backup');

      setSuccess('Database restored successfully! Please refresh the page.');
      setRestoreDialog({ show: false, backup: null });
      loadBackups();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteDialog.backup) return;

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`/api/admin/database/backup/${deleteDialog.backup.filename}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      const data = await response.json();

      if (!response.ok) throw new Error(data.message || 'Failed to delete backup');

      setSuccess('Backup deleted successfully!');
      setDeleteDialog({ show: false, backup: null });
      loadBackups();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (backup) => {
    const token = localStorage.getItem('token');
    const url = `/api/admin/database/backup/${backup.filename}/download`;
    
    // Create a temporary link with authorization header
    fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })
      .then(response => response.blob())
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = backup.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      })
      .catch(() => setError('Failed to download backup'));
  };

  return (
    <Container fluid>
      <Row className="mb-4">
        <Col>
          <h3><FaDatabase className="me-2" />Database Management</h3>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Database Health Card */}
      <Card className="mb-4">
        <Card.Header className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Database Health</h5>
          <Button variant="outline-primary" size="sm" onClick={checkHealth}>
            <FaSync className="me-1" /> Refresh
          </Button>
        </Card.Header>
        <Card.Body>
          {healthData && (
            <Row>
              <Col md={3} className="text-center">
                {healthData.healthy ? (
                  <FaCheckCircle size={48} className="text-success mb-2" />
                ) : (
                  <FaExclamationTriangle size={48} className="text-danger mb-2" />
                )}
                <p className="text-muted mb-0">
                  Status: {healthData.healthy ? 'Healthy' : 'Issues Detected'}
                </p>
              </Col>
              <Col md={3} className="text-center">
                <h2>{healthData.details?.size_mb || 0} MB</h2>
                <p className="text-muted mb-0">Database Size</p>
              </Col>
              <Col md={3} className="text-center">
                <h2>{healthData.details?.table_count || 0}</h2>
                <p className="text-muted mb-0">Tables</p>
              </Col>
              <Col md={3} className="text-center">
                <h2>{backups.length}</h2>
                <p className="text-muted mb-0">Backups</p>
              </Col>
            </Row>
          )}
        </Card.Body>
      </Card>

      {/* Backup Actions */}
      <Card className="mb-4">
        <Card.Body className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Backup Management</h5>
          <div>
            <Button
              variant="primary"
              className="me-2"
              onClick={createBackup}
              disabled={loading}
            >
              <FaPlus className="me-1" /> Create Backup
            </Button>
            <Button
              variant="outline-secondary"
              onClick={loadBackups}
              disabled={loading}
            >
              <FaSync className="me-1" /> Refresh List
            </Button>
          </div>
        </Card.Body>
      </Card>

      {/* Backups Table */}
      <Card>
        <Card.Header>
          <h5 className="mb-0">Available Backups</h5>
        </Card.Header>
        <Card.Body>
          {loading && <ProgressBar animated now={100} className="mb-3" />}

          <Table striped bordered hover responsive>
            <thead>
              <tr>
                <th>Filename</th>
                <th>Size</th>
                <th>Created</th>
                <th>Type</th>
                <th className="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              {backups.length === 0 ? (
                <tr>
                  <td colSpan={5} className="text-center text-muted">
                    No backups available
                  </td>
                </tr>
              ) : (
                backups.map((backup) => (
                  <tr key={backup.filename}>
                    <td>{backup.filename}</td>
                    <td>{backup.size_mb} MB</td>
                    <td>
                      {formatDistanceToNow(new Date(backup.created_at), { addSuffix: true })}
                    </td>
                    <td>
                      <Badge bg={backup.compressed ? 'primary' : 'secondary'}>
                        {backup.compressed ? 'Compressed' : 'Uncompressed'}
                      </Badge>
                    </td>
                    <td className="text-end">
                      <Button
                        variant="outline-primary"
                        size="sm"
                        className="me-1"
                        onClick={() => handleDownload(backup)}
                        title="Download"
                      >
                        <FaDownload />
                      </Button>
                      <Button
                        variant="outline-success"
                        size="sm"
                        className="me-1"
                        onClick={() => setRestoreDialog({ show: true, backup })}
                        title="Restore"
                      >
                        <FaUndo />
                      </Button>
                      <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={() => setDeleteDialog({ show: true, backup })}
                        title="Delete"
                      >
                        <FaTrash />
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </Table>
        </Card.Body>
      </Card>

      {/* Restore Confirmation Modal */}
      <Modal show={restoreDialog.show} onHide={() => setRestoreDialog({ show: false, backup: null })}>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Restore</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Alert variant="warning">
            This will replace the current database with the backup. A safety backup will be created first.
          </Alert>
          <p>
            Are you sure you want to restore from <strong>{restoreDialog.backup?.filename}</strong>?
          </p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setRestoreDialog({ show: false, backup: null })}>
            Cancel
          </Button>
          <Button variant="warning" onClick={handleRestore} disabled={loading}>
            {loading ? <Spinner animation="border" size="sm" /> : 'Restore'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal show={deleteDialog.show} onHide={() => setDeleteDialog({ show: false, backup: null })}>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Delete</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>
            Are you sure you want to delete <strong>{deleteDialog.backup?.filename}</strong>?
          </p>
          <p className="text-muted">This action cannot be undone.</p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setDeleteDialog({ show: false, backup: null })}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDelete} disabled={loading}>
            {loading ? <Spinner animation="border" size="sm" /> : 'Delete'}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default DatabaseManagement;

