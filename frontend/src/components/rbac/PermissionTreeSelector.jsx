import { useState } from 'react';
import { Form, Card, Accordion, Badge, Button } from 'react-bootstrap';
import { FaChevronDown, FaChevronRight, FaCheckSquare, FaSquare, FaMinusSquare } from 'react-icons/fa';
import PropTypes from 'prop-types';
import './PermissionTreeSelector.css';

/**
 * PermissionTreeSelector Component
 * 
 * A hierarchical tree view for selecting permissions organized by category.
 * Features:
 * - Expandable/collapsible categories
 * - Select All / Deselect All per category
 * - Visual indication of selected permissions
 * - Displays permission descriptions
 */
const PermissionTreeSelector = ({ permissionsByCategory, selectedPermissions, onChange }) => {
  const [expandedCategories, setExpandedCategories] = useState(
    Object.keys(permissionsByCategory).reduce((acc, category) => {
      acc[category] = true; // Start with all categories expanded
      return acc;
    }, {})
  );

  // Toggle category expansion
  const toggleCategory = (category) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  // Check if a permission is selected
  const isPermissionSelected = (permissionId) => {
    return selectedPermissions.includes(permissionId);
  };

  // Toggle individual permission
  const togglePermission = (permissionId) => {
    if (isPermissionSelected(permissionId)) {
      onChange(selectedPermissions.filter(id => id !== permissionId));
    } else {
      onChange([...selectedPermissions, permissionId]);
    }
  };

  // Get category selection state
  const getCategoryState = (categoryPermissions) => {
    const selectedCount = categoryPermissions.filter(p => 
      isPermissionSelected(p.id)
    ).length;
    
    if (selectedCount === 0) return 'none';
    if (selectedCount === categoryPermissions.length) return 'all';
    return 'partial';
  };

  // Toggle all permissions in a category
  const toggleCategoryPermissions = (categoryPermissions) => {
    const categoryState = getCategoryState(categoryPermissions);
    const categoryPermissionIds = categoryPermissions.map(p => p.id);
    
    if (categoryState === 'all') {
      // Deselect all in this category
      onChange(selectedPermissions.filter(id => !categoryPermissionIds.includes(id)));
    } else {
      // Select all in this category
      const newSelected = [...selectedPermissions];
      categoryPermissionIds.forEach(id => {
        if (!newSelected.includes(id)) {
          newSelected.push(id);
        }
      });
      onChange(newSelected);
    }
  };

  // Get icon for category state
  const getCategoryIcon = (state) => {
    switch (state) {
      case 'all':
        return <FaCheckSquare className="text-success" />;
      case 'partial':
        return <FaMinusSquare className="text-warning" />;
      default:
        return <FaSquare className="text-muted" />;
    }
  };

  return (
    <div className="permission-tree-selector">
      <div className="mb-3">
        <small className="text-muted">
          Select the permissions to assign to this role. Permissions are organized by category.
        </small>
      </div>

      <Accordion defaultActiveKey={Object.keys(permissionsByCategory)}>
        {Object.entries(permissionsByCategory).map(([category, permissions]) => {
          const categoryState = getCategoryState(permissions);
          const isExpanded = expandedCategories[category];

          return (
            <Card key={category} className="mb-2 permission-category-card">
              <Card.Header className="permission-category-header">
                <div className="d-flex align-items-center justify-content-between">
                  <div className="d-flex align-items-center flex-grow-1">
                    <Button
                      variant="link"
                      className="p-0 me-2 text-decoration-none category-toggle"
                      onClick={() => toggleCategory(category)}
                    >
                      {isExpanded ? <FaChevronDown size={20} /> : <FaChevronRight size={20} />}
                    </Button>
                    
                    <div
                      className="category-checkbox-wrapper me-2"
                      onClick={() => toggleCategoryPermissions(permissions)}
                      style={{ cursor: 'pointer' }}
                    >
                      {getCategoryIcon(categoryState)}
                    </div>

                    <div className="flex-grow-1">
                      <strong>{category}</strong>
                      <Badge bg="secondary" className="ms-2">
                        {permissions.filter(p => isPermissionSelected(p.id)).length} / {permissions.length}
                      </Badge>
                    </div>
                  </div>

                  <Button
                    variant="link"
                    size="sm"
                    className="text-decoration-none"
                    onClick={() => toggleCategoryPermissions(permissions)}
                  >
                    {categoryState === 'all' ? 'Deselect All' : 'Select All'}
                  </Button>
                </div>
              </Card.Header>

              {isExpanded && (
                <Card.Body className="permission-list">
                  {permissions.map((permission) => (
                    <div
                      key={permission.id}
                      className={`permission-item ${isPermissionSelected(permission.id) ? 'selected' : ''}`}
                    >
                      <Form.Check
                        type="checkbox"
                        id={`permission-${permission.id}`}
                        checked={isPermissionSelected(permission.id)}
                        onChange={() => togglePermission(permission.id)}
                        label={
                          <div className="permission-details">
                            <div className="permission-name">
                              <code>{permission.name}</code>
                            </div>
                            <div className="permission-description text-muted">
                              {permission.description}
                            </div>
                          </div>
                        }
                      />
                    </div>
                  ))}
                </Card.Body>
              )}
            </Card>
          );
        })}
      </Accordion>

      <div className="mt-3 p-3 bg-light rounded">
        <div className="d-flex justify-content-between align-items-center">
          <div>
            <strong>Total Selected:</strong>{' '}
            <Badge bg="primary" className="ms-2">
              {selectedPermissions.length}
            </Badge>
          </div>
          <div>
            <Button
              variant="outline-secondary"
              size="sm"
              onClick={() => onChange([])}
              disabled={selectedPermissions.length === 0}
            >
              Clear All
            </Button>
            <Button
              variant="outline-primary"
              size="sm"
              className="ms-2"
              onClick={() => {
                const allPermissionIds = Object.values(permissionsByCategory)
                  .flat()
                  .map(p => p.id);
                onChange(allPermissionIds);
              }}
              disabled={selectedPermissions.length === Object.values(permissionsByCategory).flat().length}
            >
              Select All
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

PermissionTreeSelector.propTypes = {
  permissionsByCategory: PropTypes.object.isRequired,
  selectedPermissions: PropTypes.array.isRequired,
  onChange: PropTypes.func.isRequired
};

export default PermissionTreeSelector;

