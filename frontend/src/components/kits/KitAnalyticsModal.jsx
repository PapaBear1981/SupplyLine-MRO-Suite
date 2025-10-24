import { useEffect, useMemo, useState } from 'react';
import {
  Modal,
  Button,
  Spinner,
  Alert,
  Row,
  Col,
  Card,
  Badge,
  ButtonGroup,
  ProgressBar
} from 'react-bootstrap';
import Fade from 'react-bootstrap/Fade';
import {
  FaChartBar,
  FaRedo,
  FaExchangeAlt,
  FaArrowUp,
  FaBoxOpen
} from 'react-icons/fa';

const TIME_RANGE_OPTIONS = [7, 30, 90];

const KitAnalyticsModal = ({
  show,
  onHide,
  kitName,
  days = 30,
  data,
  loading,
  error,
  onChangeDays,
  onRefresh
}) => {
  const [activeDays, setActiveDays] = useState(days);

  useEffect(() => {
    setActiveDays(days);
  }, [days]);

  const safeNumber = (value) =>
    typeof value === 'number' && Number.isFinite(value) ? value : 0;

  const transfers = useMemo(() => {
    const incoming = safeNumber(data?.transfers?.incoming);
    const outgoing = safeNumber(data?.transfers?.outgoing);
    const net = safeNumber(data?.transfers?.net);
    const total = Math.max(incoming + outgoing, 1);

    return {
      incoming,
      outgoing,
      net,
      incomingPercent: Math.round((incoming / total) * 100),
      outgoingPercent: Math.round((outgoing / total) * 100)
    };
  }, [data]);

  const stockBadgeVariant =
    data?.inventory?.stock_health === 'good'
      ? 'success'
      : data?.inventory?.stock_health === 'warning'
      ? 'warning'
      : 'danger';

  const handleSelectDays = (value) => {
    if (value === activeDays) {
      return;
    }
    setActiveDays(value);
    onChangeDays?.(value);
  };

  return (
    <Modal
      show={show}
      onHide={onHide}
      size="xl"
      centered
      backdrop="static"
      className="kit-analytics-modal"
    >
      <Modal.Header closeButton className="py-3">
        <Modal.Title className="d-flex align-items-center gap-2">
          <FaChartBar />
          Kit Analytics
        </Modal.Title>
      </Modal.Header>

      <Modal.Body>
        <div className="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
          <div>
            <h4 className="mb-1">{kitName || 'Selected Kit'}</h4>
            <small className="text-muted">
              Insight summary for the last {activeDays} days
            </small>
          </div>

          <div className="d-flex flex-wrap gap-2 align-items-center">
            <ButtonGroup>
              {TIME_RANGE_OPTIONS.map((option) => (
                <Button
                  key={option}
                  variant={option === activeDays ? 'primary' : 'outline-primary'}
                  onClick={() => handleSelectDays(option)}
                >
                  {option}d
                </Button>
              ))}
            </ButtonGroup>
            <Button
              variant="outline-primary"
              onClick={onRefresh}
              disabled={loading}
            >
              <FaRedo className="me-2" />
              Refresh
            </Button>
          </div>
        </div>

        {loading && (
          <div className="text-center py-5">
            <Spinner animation="border" role="status" />
            <div className="mt-3 text-muted">Loading analytics…</div>
          </div>
        )}

        {!loading && error && (
          <Alert variant="danger">
            {error.message || 'Unable to load kit analytics at this time.'}
          </Alert>
        )}

        {!loading && !error && !data && (
          <Alert variant="info">
            Analytics are not yet available for this kit. Try a shorter window or
            check back after new activity.
          </Alert>
        )}

        <Fade in={!loading && !error && !!data} mountOnEnter unmountOnExit>
          <div>
            <Row className="g-3 mb-4">
              <Col lg={3} md={6}>
                <Card className="shadow-sm h-100 border-0">
                  <Card.Body>
                    <div className="text-uppercase text-muted small">
                      Total Issuances
                    </div>
                    <h2 className="fw-bold mb-1">
                      {safeNumber(data?.issuances?.total)}
                    </h2>
                    <div className="text-muted">
                      Avg {safeNumber(data?.issuances?.average_per_day)} / day
                    </div>
                  </Card.Body>
                </Card>
              </Col>

              <Col lg={3} md={6}>
                <Card className="shadow-sm h-100 border-0">
                  <Card.Body>
                    <div className="text-uppercase text-muted small">
                      Transfers In
                    </div>
                    <h2 className="fw-bold text-success mb-1">
                      {transfers.incoming}
                    </h2>
                    <div className="text-muted">
                      {transfers.incomingPercent}% of total transfers
                    </div>
                  </Card.Body>
                </Card>
              </Col>

              <Col lg={3} md={6}>
                <Card className="shadow-sm h-100 border-0">
                  <Card.Body>
                    <div className="text-uppercase text-muted small">
                      Transfers Out
                    </div>
                    <h2 className="fw-bold text-danger mb-1">
                      {transfers.outgoing}
                    </h2>
                    <div className="text-muted">
                      {transfers.outgoingPercent}% of total transfers
                    </div>
                  </Card.Body>
                </Card>
              </Col>

              <Col lg={3} md={6}>
                <Card className="shadow-sm h-100 border-0">
                  <Card.Body>
                    <div className="text-uppercase text-muted small">
                      Stock Health
                    </div>
                    <div className="d-flex align-items-center gap-2 mb-2">
                      <Badge bg={stockBadgeVariant} className="px-3 py-2">
                        {data?.inventory?.stock_health || 'unknown'}
                      </Badge>
                      <FaArrowUp className="text-primary" />
                    </div>
                    <div className="text-muted">
                      {safeNumber(data?.inventory?.low_stock_items)} items at or
                      below minimum
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            </Row>

            <Row className="g-3">
              <Col lg={6}>
                <Card className="shadow-sm h-100 border-0">
                  <Card.Header>
                    <FaExchangeAlt className="me-2 text-primary" />
                    Transfer Flow
                  </Card.Header>
                  <Card.Body>
                    <div className="mb-3">
                      <div className="d-flex justify-content-between">
                        <span>Incoming</span>
                        <Badge bg="success">{transfers.incoming}</Badge>
                      </div>
                      <ProgressBar
                        now={transfers.incomingPercent}
                        variant="success"
                        className="mt-2"
                      />
                    </div>
                    <div className="mb-3">
                      <div className="d-flex justify-content-between">
                        <span>Outgoing</span>
                        <Badge bg="danger">{transfers.outgoing}</Badge>
                      </div>
                      <ProgressBar
                        now={transfers.outgoingPercent}
                        variant="danger"
                        className="mt-2"
                      />
                    </div>
                    <div className="d-flex justify-content-between align-items-center">
                      <span>Net Movement</span>
                      <Badge
                        bg={transfers.net >= 0 ? 'success' : 'danger'}
                        className="px-3"
                      >
                        {transfers.net >= 0 ? '+' : ''}
                        {transfers.net}
                      </Badge>
                    </div>
                  </Card.Body>
                </Card>
              </Col>

              <Col lg={6}>
                <Card className="shadow-sm h-100 border-0">
                  <Card.Header>
                    <FaBoxOpen className="me-2 text-warning" />
                    Inventory & Reorders
                  </Card.Header>
                  <Card.Body>
                    <div className="mb-3">
                      <div className="d-flex justify-content-between">
                        <span>Total Items</span>
                        <Badge bg="secondary">
                          {safeNumber(data?.inventory?.total_items)}
                        </Badge>
                      </div>
                    </div>

                    <div className="mb-3">
                      <div className="d-flex justify-content-between">
                        <span>Low Stock Items</span>
                        <Badge bg="warning">
                          {safeNumber(data?.inventory?.low_stock_items)}
                        </Badge>
                      </div>
                    </div>

                    <hr />

                    <div className="d-flex justify-content-between align-items-center mb-2">
                      <span>Pending Reorders</span>
                      <Badge bg="warning">
                        {safeNumber(data?.reorders?.pending)}
                      </Badge>
                    </div>

                    <div className="d-flex justify-content-between align-items-center">
                      <span>Fulfilled Reorders</span>
                      <Badge bg="success">
                        {safeNumber(data?.reorders?.fulfilled)}
                      </Badge>
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          </div>
        </Fade>
      </Modal.Body>
    </Modal>
  );
};

export default KitAnalyticsModal;