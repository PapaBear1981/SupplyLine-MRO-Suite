import { Breadcrumb, Button, Space, Typography } from 'antd';
import { Link } from 'react-router-dom';
import { HomeOutlined } from '@ant-design/icons';
import PropTypes from 'prop-types';

const { Title, Text } = Typography;

const EnterprisePageHeader = ({
  title,
  subtitle,
  icon,
  breadcrumbs = [],
  actions = [],
  meta = [],
  className = '',
}) => {
  const breadcrumbItems = [
    {
      key: 'home',
      title: (
        <Link to="/dashboard">
          <HomeOutlined />
        </Link>
      ),
    },
    ...breadcrumbs.map((item, index) => ({
      key: index,
      title: item.path ? <Link to={item.path}>{item.title}</Link> : item.title,
    })),
  ];

  return (
    <div className={`enterprise-page-header ${className}`}>
      <Breadcrumb items={breadcrumbItems} className="enterprise-breadcrumb" />

      <div className="enterprise-page-header-top">
        <div className="enterprise-page-header-title">
          {icon && <span>{icon}</span>}
          <Title level={2} style={{ margin: 0, fontSize: 20, fontWeight: 600 }}>
            {title}
          </Title>
        </div>

        {actions.length > 0 && (
          <Space className="enterprise-page-header-actions">
            {actions.map((action, index) => (
              <Button
                key={index}
                type={action.type || 'default'}
                icon={action.icon}
                onClick={action.onClick}
                danger={action.danger}
                disabled={action.disabled}
                loading={action.loading}
                size={action.size || 'middle'}
              >
                {action.label}
              </Button>
            ))}
          </Space>
        )}
      </div>

      {(subtitle || meta.length > 0) && (
        <div style={{ marginTop: 8 }}>
          {subtitle && (
            <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>
              {subtitle}
            </Text>
          )}

          {meta.length > 0 && (
            <div className="enterprise-page-header-meta">
              {meta.map((item, index) => (
                <span key={index} className="enterprise-page-header-meta-item">
                  {item.icon && <span>{item.icon}</span>}
                  <span>{item.label}: {item.value}</span>
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

EnterprisePageHeader.propTypes = {
  title: PropTypes.string.isRequired,
  subtitle: PropTypes.string,
  icon: PropTypes.node,
  breadcrumbs: PropTypes.arrayOf(
    PropTypes.shape({
      title: PropTypes.string.isRequired,
      path: PropTypes.string,
    })
  ),
  actions: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      icon: PropTypes.node,
      onClick: PropTypes.func,
      type: PropTypes.string,
      danger: PropTypes.bool,
      disabled: PropTypes.bool,
      loading: PropTypes.bool,
      size: PropTypes.string,
    })
  ),
  meta: PropTypes.arrayOf(
    PropTypes.shape({
      icon: PropTypes.node,
      label: PropTypes.string.isRequired,
      value: PropTypes.node.isRequired,
    })
  ),
  className: PropTypes.string,
};

export default EnterprisePageHeader;
