import { Table, Input, Select, Space, Button, Tag, Tooltip, Dropdown } from 'antd';
import {
  SearchOutlined,
  ReloadOutlined,
  SettingOutlined,
  FilterOutlined,
  DownloadOutlined,
  ColumnHeightOutlined,
} from '@ant-design/icons';
import PropTypes from 'prop-types';
import { useState } from 'react';

const { Search } = Input;

const EnterpriseTable = ({
  columns,
  dataSource,
  loading = false,
  rowKey = 'id',
  pagination = {
    pageSize: 20,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} items`,
    pageSizeOptions: ['10', '20', '50', '100'],
  },
  onSearch,
  onRefresh,
  onExport,
  searchPlaceholder = 'Search...',
  filters = [],
  selectedFilters = {},
  onFilterChange,
  rowSelection,
  expandable,
  scroll = { x: 'max-content' },
  size = 'middle',
  title,
  extra,
  toolbar = true,
  bordered = false,
  sticky = false,
  className = '',
  ...rest
}) => {
  const [searchValue, setSearchValue] = useState('');
  const [tableSize, setTableSize] = useState(size);

  const handleSearch = (value) => {
    setSearchValue(value);
    if (onSearch) {
      onSearch(value);
    }
  };

  const handleSizeChange = ({ key }) => {
    setTableSize(key);
  };

  const sizeMenuItems = [
    { key: 'small', label: 'Compact' },
    { key: 'middle', label: 'Default' },
    { key: 'large', label: 'Comfortable' },
  ];

  return (
    <div className={`enterprise-table ${className}`}>
      {toolbar && (
        <div className="enterprise-toolbar">
          <div className="enterprise-toolbar-left">
            <Search
              placeholder={searchPlaceholder}
              allowClear
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              onSearch={handleSearch}
              style={{ width: 280 }}
              className="enterprise-toolbar-search"
            />

            {filters.length > 0 && (
              <Space className="enterprise-toolbar-filters">
                {filters.map((filter) => (
                  <Select
                    key={filter.key}
                    placeholder={filter.placeholder}
                    value={selectedFilters[filter.key]}
                    onChange={(value) => onFilterChange && onFilterChange(filter.key, value)}
                    style={{ minWidth: 150 }}
                    allowClear
                    options={filter.options}
                  />
                ))}
              </Space>
            )}
          </div>

          <div className="enterprise-toolbar-right">
            {onRefresh && (
              <Tooltip title="Refresh">
                <Button
                  icon={<ReloadOutlined spin={loading} />}
                  onClick={onRefresh}
                  disabled={loading}
                />
              </Tooltip>
            )}

            {onExport && (
              <Tooltip title="Export">
                <Button icon={<DownloadOutlined />} onClick={onExport} />
              </Tooltip>
            )}

            <Tooltip title="Table Size">
              <Dropdown
                menu={{ items: sizeMenuItems, onClick: handleSizeChange }}
                trigger={['click']}
              >
                <Button icon={<ColumnHeightOutlined />} />
              </Dropdown>
            </Tooltip>

            {extra}
          </div>
        </div>
      )}

      <Table
        columns={columns}
        dataSource={dataSource}
        loading={loading}
        rowKey={rowKey}
        pagination={pagination}
        rowSelection={rowSelection}
        expandable={expandable}
        scroll={scroll}
        size={tableSize}
        bordered={bordered}
        sticky={sticky}
        title={title}
        {...rest}
      />
    </div>
  );
};

// Status tag component for common status displays
export const StatusTag = ({ status, statusConfig = {} }) => {
  const defaultConfig = {
    available: { color: 'success', text: 'Available' },
    checked_out: { color: 'warning', text: 'Checked Out' },
    maintenance: { color: 'processing', text: 'Maintenance' },
    retired: { color: 'error', text: 'Retired' },
    active: { color: 'success', text: 'Active' },
    inactive: { color: 'default', text: 'Inactive' },
    pending: { color: 'warning', text: 'Pending' },
    approved: { color: 'success', text: 'Approved' },
    rejected: { color: 'error', text: 'Rejected' },
    completed: { color: 'success', text: 'Completed' },
    cancelled: { color: 'default', text: 'Cancelled' },
    in_progress: { color: 'processing', text: 'In Progress' },
    overdue: { color: 'error', text: 'Overdue' },
    expired: { color: 'error', text: 'Expired' },
    valid: { color: 'success', text: 'Valid' },
    ...statusConfig,
  };

  const config = defaultConfig[status?.toLowerCase()] || {
    color: 'default',
    text: status || 'Unknown',
  };

  return (
    <Tag color={config.color} className="enterprise-status-tag">
      {config.text}
    </Tag>
  );
};

StatusTag.propTypes = {
  status: PropTypes.string,
  statusConfig: PropTypes.object,
};

EnterpriseTable.propTypes = {
  columns: PropTypes.array.isRequired,
  dataSource: PropTypes.array,
  loading: PropTypes.bool,
  rowKey: PropTypes.oneOfType([PropTypes.string, PropTypes.func]),
  pagination: PropTypes.oneOfType([PropTypes.object, PropTypes.bool]),
  onSearch: PropTypes.func,
  onRefresh: PropTypes.func,
  onExport: PropTypes.func,
  searchPlaceholder: PropTypes.string,
  filters: PropTypes.array,
  selectedFilters: PropTypes.object,
  onFilterChange: PropTypes.func,
  rowSelection: PropTypes.object,
  expandable: PropTypes.object,
  scroll: PropTypes.object,
  size: PropTypes.string,
  title: PropTypes.func,
  extra: PropTypes.node,
  toolbar: PropTypes.bool,
  bordered: PropTypes.bool,
  sticky: PropTypes.bool,
  className: PropTypes.string,
};

export default EnterpriseTable;
