import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Container, Button, Modal, ListGroup } from 'react-bootstrap';
import DashboardLayout from '../components/dashboard/layout/DashboardLayout';
import {
  fetchDashboardLayout,
  saveDashboardLayout,
  setLayout,
  addWidget,
  removeWidget,
} from '../store/dashboardSlice';

const allWidgets = [
  'Announcements',
  'QuickActions',
  'CalibrationNotifications',
  'KitAlertsSummary',
  'UserCheckoutStatus',
  'MyKits',
  'RecentKitActivity',
  'OverdueChemicals',
  'PastDueTools',
  'RecentActivity',
];

const UserDashboardPage = () => {
  const dispatch = useDispatch();
  const { layout, status } = useSelector((state) => state.dashboard);
  const [showAddWidgetModal, setShowAddWidgetModal] = useState(false);

  useEffect(() => {
    if (status === 'idle') {
      dispatch(fetchDashboardLayout());
    }
  }, [status, dispatch]);

  const handleLayoutChange = (newLayout) => {
    dispatch(setLayout(newLayout));
    dispatch(saveDashboardLayout(newLayout));
  };

  const handleRemoveWidget = (widgetId) => {
    dispatch(removeWidget(widgetId));
    dispatch(saveDashboardLayout(layout.filter((w) => w.i !== widgetId)));
  };

  const handleAddWidget = (widgetId) => {
    const newWidget = {
      i: widgetId,
      x: (layout.length * 4) % 12,
      y: Infinity, // puts it at the bottom
      w: 4,
      h: 6,
    };
    dispatch(addWidget(newWidget));
    dispatch(saveDashboardLayout([...layout, newWidget]));
  };

  const availableWidgets = allWidgets.filter(
    (w) => !layout.some((item) => item.i === w)
  );

  return (
    <div className="w-100" data-testid="dashboard-content">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
        <h1 className="mb-0">Dashboard</h1>
        <Button onClick={() => setShowAddWidgetModal(true)}>Add Widget</Button>
      </div>

      <Container fluid className="p-0">
        {status === 'loading' && <p>Loading...</p>}
        {status !== 'loading' && (
          <DashboardLayout
            layout={layout}
            onLayoutChange={handleLayoutChange}
            onRemoveWidget={handleRemoveWidget}
          />
        )}
      </Container>

      <Modal
        show={showAddWidgetModal}
        onHide={() => setShowAddWidgetModal(false)}
      >
        <Modal.Header closeButton>
          <Modal.Title>Add Widget</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <ListGroup>
            {availableWidgets.map((widgetId) => (
              <ListGroup.Item
                key={widgetId}
                action
                onClick={() => {
                  handleAddWidget(widgetId);
                  setShowAddWidgetModal(false);
                }}
              >
                {widgetId.replace(/([A-Z])/g, ' $1').trim()}
              </ListGroup.Item>
            ))}
            {availableWidgets.length === 0 && (
              <ListGroup.Item>No more widgets to add.</ListGroup.Item>
            )}
          </ListGroup>
        </Modal.Body>
      </Modal>
    </div>
  );
};

export default UserDashboardPage;
