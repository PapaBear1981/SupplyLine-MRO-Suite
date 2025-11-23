import { useMemo, useState } from 'react';
import { useSelector } from 'react-redux';
import {
  Button,
  Alert,
  Badge,
  Tabs,
  Tab,
  Row,
  Col,
  Card,
  Table,
  Modal
} from 'react-bootstrap';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import ToolList from '../components/tools/ToolList';
import BulkImportTools from '../components/tools/BulkImportTools';
import useHotkeys from '../hooks/useHotkeys';

const ToolsManagement = () => {
  const { user } = useSelector((state) => state.auth);
  const { tools } = useSelector((state) => state.tools);
  const location = useLocation();
  const navigate = useNavigate();
  const isAdmin = user?.is_admin || user?.department === 'Materials';
  const unauthorized = location.state?.unauthorized;
  const [activeWorkflow, setActiveWorkflow] = useState(null);

  // Page-specific hotkeys
  useHotkeys({
    'n': () => {
      if (isAdmin) {
        navigate('/tools/new');
      }
    }
  }, {
    enabled: isAdmin,
    deps: [navigate, isAdmin]
  });

  const statusBreakdown = useMemo(() => {
    const base = {
      available: 0,
      checked_out: 0,
      maintenance: 0,
      retired: 0
    };

    tools.forEach((tool) => {
      if (tool.status && base[tool.status] !== undefined) {
        base[tool.status] += 1;
      }
    });

    return base;
  }, [tools]);

  const topCategories = useMemo(() => {
    const categories = tools.reduce((acc, tool) => {
      const category = tool.category || 'General';
      acc[category] = (acc[category] || 0) + 1;
      return acc;
    }, {});

    return Object.entries(categories)
      .sort(([, countA], [, countB]) => countB - countA)
      .slice(0, 4);
  }, [tools]);

  const workflows = [
    {
      key: 'checkout',
      title: 'Issue tools to a technician',
      badge: 'Operations',
      summary: 'Capture chain of custody and print a barcode if needed.',
      steps: [
        'Search the inventory for the tool you want to issue.',
        'Open the action menu for that tool and select "Checkout".',
        'Confirm who is receiving the tool and set the due date.'
      ],
      ctaLabel: 'Open Inventory',
      ctaAction: () => {
        document.getElementById('tools-tabs')?.scrollIntoView({ behavior: 'smooth' });
      }
    },
    {
      key: 'calibration',
      title: 'Schedule calibration and compliance',
      badge: 'Quality',
      summary: 'Route equipment to Calibration Management and review due dates.',
      steps: [
        'Filter the inventory by status or category to find regulated tools.',
        'Use the Calibration column to view current status.',
        'Open Calibration Management to bulk schedule or update completions.'
      ],
      ctaLabel: 'Go to Calibration',
      ctaAction: () => navigate('/calibrations')
    },
    {
      key: 'bulk',
      title: 'Bulk import or update tooling data',
      badge: 'Admin',
      summary: 'Upload spreadsheets or sync changes for a new facility rollout.',
      steps: [
        'Download the import template from the bulk import modal.',
        'Fill in serial numbers, descriptions, and warehouse placements.',
        'Upload the file and review the preview before committing changes.'
      ],
      ctaLabel: 'Open Bulk Import',
      ctaAction: () => setActiveWorkflow({
        key: 'bulk-import',
        title: 'Bulk import tools',
        badge: 'Admin',
        summary: 'Use the Bulk Importer to upload CSV data for a new wave of tools.',
        steps: [
          'Open the Bulk Importer from the action bar.',
          'Download the template and populate required columns.',
          'Upload the completed file and confirm the preview before saving.'
        ],
        ctaLabel: 'Launch Bulk Importer',
        ctaAction: () => document.getElementById('bulk-import-launch')?.click()
      })
    }
  ];

  const totalTools = tools.length;

  const renderWorkflowModal = () => {
    if (!activeWorkflow) return null;

    return (
      <Modal
        show={Boolean(activeWorkflow)}
        onHide={() => setActiveWorkflow(null)}
        centered
        size="lg"
      >
        <Modal.Header closeButton>
          <div className="d-flex align-items-center gap-2">
            <Badge bg="secondary">{activeWorkflow.badge}</Badge>
            <Modal.Title>{activeWorkflow.title}</Modal.Title>
          </div>
        </Modal.Header>
        <Modal.Body>
          <p className="text-muted mb-3">{activeWorkflow.summary}</p>
          <ol className="ps-3">
            {activeWorkflow.steps?.map((step) => (
              <li key={step} className="mb-2">{step}</li>
            ))}
          </ol>
        </Modal.Body>
        <Modal.Footer className="d-flex justify-content-between">
          <Button variant="outline-secondary" onClick={() => setActiveWorkflow(null)}>
            Close
          </Button>
          {activeWorkflow.ctaAction && (
            <Button
              variant="primary"
              onClick={() => {
                activeWorkflow.ctaAction();
                setActiveWorkflow(null);
              }}
            >
              {activeWorkflow.ctaLabel || 'Continue'}
            </Button>
          )}
        </Modal.Footer>
      </Modal>
    );
  };

  return (
    <div className="w-100">
      {/* Show unauthorized message if redirected from admin page */}
      {unauthorized && (
        <Alert variant="danger" className="mb-4">
          <Alert.Heading>Access Denied</Alert.Heading>
          <p>
            You do not have permission to access the Admin Dashboard. This area is restricted to administrators only.
          </p>
        </Alert>
      )}

      <div className="d-flex flex-wrap justify-content-between align-items-center mb-3 gap-3">
        <div>
          <h1 className="mb-1">Tooling</h1>
          <div className="text-muted">Track custody, calibration, and onboarding in one place.</div>
        </div>
        <div className="d-flex gap-2 align-items-center flex-wrap">
          {isAdmin && (
            <Button as={Link} to="/tools/new" variant="success">
              <i className="bi bi-plus-circle me-2"></i>
              Add New Tool
            </Button>
          )}
          {isAdmin && <BulkImportTools triggerId="bulk-import-launch" />}
          {isAdmin && (
            <Button as={Link} to="/calibrations" variant="outline-primary">
              <i className="bi bi-tools me-2"></i>
              Calibration Management
            </Button>
          )}
        </div>
      </div>

      <Row className="g-3 mb-4">
        <Col md={4}>
          <Card className="h-100 shadow-sm">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <div className="text-muted">Total tools</div>
                  <h4 className="mb-0">{totalTools}</h4>
                </div>
                <i className="bi bi-box-seam text-primary fs-3"></i>
              </div>
              <div className="mt-2 small text-muted">Includes active and retired inventory across all warehouses.</div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="h-100 shadow-sm">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <div className="text-muted">Available now</div>
                  <h4 className="mb-0">{statusBreakdown.available}</h4>
                </div>
                <i className="bi bi-check2-circle text-success fs-3"></i>
              </div>
              <div className="mt-2 small text-muted">Ready to issue without maintenance holds.</div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="h-100 shadow-sm">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <div className="text-muted">Needs attention</div>
                  <h4 className="mb-0">{statusBreakdown.maintenance + statusBreakdown.retired}</h4>
                </div>
                <i className="bi bi-exclamation-triangle text-warning fs-3"></i>
              </div>
              <div className="mt-2 small text-muted">Maintenance or retired items that should not be issued.</div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Tabs defaultActiveKey="inventory" id="tools-tabs" className="mb-4">
        <Tab eventKey="inventory" title="Inventory" tabClassName="fw-semibold" href="#inventory">
          <div className="mb-3">
            <div className="d-flex justify-content-between align-items-center">
              <div className="fw-semibold">Inventory workflow</div>
              <Button variant="link" className="p-0" onClick={() => setActiveWorkflow(workflows[0])}>
                How do I check out a tool?
              </Button>
            </div>
            <div className="text-muted">Search, filter, and take action on every tool record.</div>
          </div>
          <ToolList />
        </Tab>

        <Tab eventKey="workflows" title="Workflows" tabClassName="fw-semibold">
          <Row className="g-3 mb-3">
            {workflows.map((workflow) => (
              <Col md={4} key={workflow.key}>
                <Card className="h-100 shadow-sm">
                  <Card.Body className="d-flex flex-column gap-2">
                    <div className="d-flex justify-content-between align-items-center">
                      <Badge bg="light" text="dark">{workflow.badge}</Badge>
                      <Button
                        variant="outline-secondary"
                        size="sm"
                        onClick={() => setActiveWorkflow(workflow)}
                      >
                        View steps
                      </Button>
                    </div>
                    <h5 className="mb-1">{workflow.title}</h5>
                    <div className="text-muted flex-grow-1">{workflow.summary}</div>
                    <Button
                      variant="primary"
                      onClick={() => setActiveWorkflow(workflow)}
                    >
                      {workflow.ctaLabel}
                    </Button>
                  </Card.Body>
                </Card>
              </Col>
            ))}
          </Row>

          <Card className="shadow-sm">
            <Card.Header>
              <div className="fw-semibold">Workflow checklist</div>
              <div className="text-muted">Use these guided steps to keep the process consistent.</div>
            </Card.Header>
            <Card.Body className="p-0">
              <Table hover responsive className="mb-0">
                <thead className="bg-light">
                  <tr>
                    <th>Workflow</th>
                    <th>Outcome</th>
                    <th>Next action</th>
                  </tr>
                </thead>
                <tbody>
                  {workflows.map((workflow) => (
                    <tr key={`${workflow.key}-table`}>
                      <td className="fw-semibold">{workflow.title}</td>
                      <td>{workflow.summary}</td>
                      <td>
                        <div className="d-flex flex-wrap gap-2">
                          <Button
                            variant="outline-primary"
                            size="sm"
                            onClick={() => setActiveWorkflow(workflow)}
                          >
                            View steps
                          </Button>
                          {workflow.ctaAction && (
                            <Button
                              variant="primary"
                              size="sm"
                              onClick={() => setActiveWorkflow(workflow)}
                            >
                              {workflow.ctaLabel}
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Tab>

        <Tab eventKey="reference" title="Reference" tabClassName="fw-semibold">
          <Row className="g-3">
            <Col md={6}>
              <Card className="shadow-sm h-100">
                <Card.Header className="fw-semibold">Status overview</Card.Header>
                <Card.Body className="p-0">
                  <Table responsive hover className="mb-0">
                    <thead className="bg-light">
                      <tr>
                        <th>Status</th>
                        <th className="text-end">Count</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[['Available', statusBreakdown.available], ['Checked Out', statusBreakdown.checked_out], ['Maintenance', statusBreakdown.maintenance], ['Retired', statusBreakdown.retired]].map(([label, value]) => (
                        <tr key={label}>
                          <td>{label}</td>
                          <td className="text-end fw-semibold">{value}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </Card.Body>
              </Card>
            </Col>
            <Col md={6}>
              <Card className="shadow-sm h-100">
                <Card.Header className="fw-semibold">Top categories</Card.Header>
                <Card.Body className="p-0">
                  <Table responsive hover className="mb-0">
                    <thead className="bg-light">
                      <tr>
                        <th>Category</th>
                        <th className="text-end">Count</th>
                      </tr>
                    </thead>
                    <tbody>
                      {topCategories.map(([category, count]) => (
                        <tr key={category}>
                          <td>{category}</td>
                          <td className="text-end fw-semibold">{count}</td>
                        </tr>
                      ))}
                      {topCategories.length === 0 && (
                        <tr>
                          <td colSpan={2} className="text-center text-muted py-3">No category data yet.</td>
                        </tr>
                      )}
                    </tbody>
                  </Table>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Tab>
      </Tabs>

      {renderWorkflowModal()}
    </div>
  );
};

export default ToolsManagement;
