import { Card, Statistic, Progress, Space, Typography } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import PropTypes from 'prop-types';

const { Text } = Typography;

const EnterpriseStatCard = ({
  title,
  value,
  prefix,
  suffix,
  precision = 0,
  trend,
  trendValue,
  loading = false,
  color = 'primary',
  icon,
  progress,
  progressColor,
  onClick,
  style = {},
  className = '',
}) => {
  const colorMap = {
    primary: '#0070d2',
    success: '#2e844a',
    warning: '#ff9900',
    error: '#c23934',
    info: '#54698d',
  };

  const borderColor = colorMap[color] || color;

  const getTrendIcon = () => {
    if (trend === 'up') {
      return <ArrowUpOutlined style={{ color: '#2e844a' }} />;
    }
    if (trend === 'down') {
      return <ArrowDownOutlined style={{ color: '#c23934' }} />;
    }
    return null;
  };

  const getTrendColor = () => {
    if (trend === 'up') return '#2e844a';
    if (trend === 'down') return '#c23934';
    return '#54698d';
  };

  return (
    <Card
      className={`enterprise-stat-card ${className}`}
      style={{
        borderLeft: `4px solid ${borderColor}`,
        cursor: onClick ? 'pointer' : 'default',
        ...style,
      }}
      loading={loading}
      onClick={onClick}
      hoverable={!!onClick}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <Text
            type="secondary"
            style={{
              fontSize: 12,
              fontWeight: 500,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              display: 'block',
              marginBottom: 8,
            }}
          >
            {title}
          </Text>

          <Statistic
            value={value}
            prefix={prefix}
            suffix={suffix}
            precision={precision}
            valueStyle={{
              fontSize: 32,
              fontWeight: 700,
              color: '#16325c',
              lineHeight: 1.2,
            }}
          />

          {(trend || trendValue) && (
            <div style={{ marginTop: 8 }}>
              <Space size={4}>
                {getTrendIcon()}
                <Text style={{ color: getTrendColor(), fontSize: 12, fontWeight: 500 }}>
                  {trendValue}
                </Text>
              </Space>
            </div>
          )}

          {progress !== undefined && (
            <div style={{ marginTop: 12 }}>
              <Progress
                percent={progress}
                size="small"
                strokeColor={progressColor || borderColor}
                showInfo={false}
              />
              <Text type="secondary" style={{ fontSize: 11 }}>
                {progress}% complete
              </Text>
            </div>
          )}
        </div>

        {icon && (
          <div
            style={{
              fontSize: 32,
              color: borderColor,
              opacity: 0.8,
            }}
          >
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
};

EnterpriseStatCard.propTypes = {
  title: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
  prefix: PropTypes.node,
  suffix: PropTypes.node,
  precision: PropTypes.number,
  trend: PropTypes.oneOf(['up', 'down', null]),
  trendValue: PropTypes.string,
  loading: PropTypes.bool,
  color: PropTypes.string,
  icon: PropTypes.node,
  progress: PropTypes.number,
  progressColor: PropTypes.string,
  onClick: PropTypes.func,
  style: PropTypes.object,
  className: PropTypes.string,
};

export default EnterpriseStatCard;
