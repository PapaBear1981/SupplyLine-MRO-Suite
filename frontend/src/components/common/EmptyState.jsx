import React from 'react';
import { Card, Button, Alert } from 'react-bootstrap';
import { FaBox, FaFlask, FaExclamationCircle, FaSearch, FaPlus, FaEnvelope, FaTools } from 'react-icons/fa';
import PropTypes from 'prop-types';

/**
 * Standardized EmptyState component for consistent UX across the application
 * Follows WCAG 2.1 AA guidelines with proper semantic HTML and ARIA attributes
 */
const EmptyState = ({
  icon: IconComponent,
  title,
  message,
  actionButton,
  variant = 'card', // 'card' or 'alert'
  size = 'md', // 'sm', 'md', 'lg'
  className = ''
}) => {
  // Icon size mapping
  const iconSizes = {
    sm: 32,
    md: 48,
    lg: 64
  };

  // Padding mapping
  const paddingClasses = {
    sm: 'py-3',
    md: 'py-5',
    lg: 'py-6'
  };

  const iconSize = iconSizes[size] || iconSizes.md;
  const paddingClass = paddingClasses[size] || paddingClasses.md;

  // Card variant (default)
  if (variant === 'card') {
    return (
      <Card className={`text-center ${paddingClass} ${className}`}>
        <Card.Body>
          {IconComponent && (
            <div className="mb-3" aria-hidden="true">
              <IconComponent size={iconSize} className="text-muted" />
            </div>
          )}
          <h5 className="mb-2">{title}</h5>
          {message && (
            <p className="text-muted mb-3">{message}</p>
          )}
          {actionButton && (
            <div className="mt-3">
              {actionButton}
            </div>
          )}
        </Card.Body>
      </Card>
    );
  }

  // Alert variant
  return (
    <Alert variant="info" className={`text-center ${className}`}>
      <div className={paddingClass}>
        {IconComponent && (
          <div className="mb-3" aria-hidden="true">
            <IconComponent size={iconSize} className="text-info" />
          </div>
        )}
        <Alert.Heading as="h5">{title}</Alert.Heading>
        {message && <p className="mb-0">{message}</p>}
        {actionButton && (
          <div className="mt-3">
            {actionButton}
          </div>
        )}
      </div>
    </Alert>
  );
};

EmptyState.propTypes = {
  icon: PropTypes.elementType,
  title: PropTypes.string.isRequired,
  message: PropTypes.string,
  actionButton: PropTypes.node,
  variant: PropTypes.oneOf(['card', 'alert']),
  size: PropTypes.oneOf(['sm', 'md', 'lg']),
  className: PropTypes.string
};

// Pre-configured empty state variants for common scenarios
export const NoKitsFound = ({ searchTerm, selectedFilter, onCreateKit }) => (
  <EmptyState
    icon={FaBox}
    title="No kits found"
    message={
      searchTerm || selectedFilter
        ? 'Try adjusting your filters or search term'
        : 'Create your first kit to get started'
    }
    actionButton={
      !searchTerm && !selectedFilter && onCreateKit ? (
        <Button variant="primary" onClick={onCreateKit}>
          <FaPlus className="me-2" />
          Create Kit
        </Button>
      ) : null
    }
    variant="card"
  />
);

NoKitsFound.propTypes = {
  searchTerm: PropTypes.string,
  selectedFilter: PropTypes.string,
  onCreateKit: PropTypes.func
};

export const NoChemicalsFound = ({ searchTerm, hasFilters, onAddChemical }) => (
  <EmptyState
    icon={FaFlask}
    title="No chemicals found"
    message={
      searchTerm || hasFilters
        ? 'Try adjusting your filters or search term'
        : 'Add your first chemical to get started'
    }
    actionButton={
      !searchTerm && !hasFilters && onAddChemical ? (
        <Button variant="primary" onClick={onAddChemical}>
          <FaPlus className="me-2" />
          Add Chemical
        </Button>
      ) : null
    }
    variant="alert"
  />
);

NoChemicalsFound.propTypes = {
  searchTerm: PropTypes.string,
  hasFilters: PropTypes.bool,
  onAddChemical: PropTypes.func
};

export const NoToolsFound = ({ searchTerm, hasFilters, onAddTool }) => (
  <EmptyState
    icon={FaTools}
    title="No tools found"
    message={
      searchTerm || hasFilters
        ? 'Try adjusting your filters or search term'
        : 'Add your first tool to get started'
    }
    actionButton={
      !searchTerm && !hasFilters && onAddTool ? (
        <Button variant="primary" onClick={onAddTool}>
          <FaPlus className="me-2" />
          Add Tool
        </Button>
      ) : null
    }
    variant="alert"
  />
);

NoToolsFound.propTypes = {
  searchTerm: PropTypes.string,
  hasFilters: PropTypes.bool,
  onAddTool: PropTypes.func
};

export const NoItemsFound = ({ itemType = 'items' }) => (
  <EmptyState
    icon={FaBox}
    title={`No ${itemType} found`}
    message="This list is currently empty"
    variant="card"
    size="sm"
  />
);

NoItemsFound.propTypes = {
  itemType: PropTypes.string
};

export const NoMessagesFound = () => (
  <EmptyState
    icon={FaEnvelope}
    title="No messages"
    message="Your inbox is empty"
    variant="card"
    size="sm"
  />
);

export const NoSearchResults = ({ searchTerm }) => (
  <EmptyState
    icon={FaSearch}
    title="No results found"
    message={`No results match "${searchTerm}". Try a different search term.`}
    variant="alert"
    size="sm"
  />
);

NoSearchResults.propTypes = {
  searchTerm: PropTypes.string.isRequired
};

export const NoDataAvailable = ({ dataType = 'data' }) => (
  <EmptyState
    icon={FaExclamationCircle}
    title={`No ${dataType} available`}
    message="There is currently no data to display"
    variant="alert"
    size="sm"
  />
);

NoDataAvailable.propTypes = {
  dataType: PropTypes.string
};

export default EmptyState;

