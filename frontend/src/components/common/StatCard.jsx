import { Card, Col, Spinner } from 'react-bootstrap';
import PropTypes from 'prop-types';

/**
 * Reusable statistic card component for dashboards
 * Uses static background colors that remain consistent across light/dark themes
 */
const StatCard = ({
  title,
  value,
  icon,
  bgColor,
  textColor = 'text-white',
  loading = false,
  size = 'md'
}) => {
  const colSizes = {
    sm: { xs: 12, sm: 6, md: 4, lg: 3 },
    md: { xs: 12, sm: 6, md: 4, lg: 2 },
    lg: { xs: 12, sm: 6, md: 3 }
  };

  return (
    <Col {...(colSizes[size] || colSizes.md)}>
      <Card className={`${bgColor} ${textColor} shadow-sm h-100`}>
        <Card.Body className="d-flex flex-column justify-content-between">
          <div className="d-flex justify-content-between align-items-start mb-2">
            <div>
              <h6 className="mb-0 text-uppercase small">{title}</h6>
            </div>
            <i className={`bi bi-${icon} fs-3 opacity-50`}></i>
          </div>
          <div>
            <h2 className="mb-0 fw-bold">
              {loading ? (
                <Spinner animation="border" size="sm" />
              ) : (
                value
              )}
            </h2>
          </div>
        </Card.Body>
      </Card>
    </Col>
  );
};

StatCard.propTypes = {
  title: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
  icon: PropTypes.string.isRequired,
  bgColor: PropTypes.string.isRequired,
  textColor: PropTypes.string,
  loading: PropTypes.bool,
  size: PropTypes.oneOf(['sm', 'md', 'lg'])
};

export default StatCard;
