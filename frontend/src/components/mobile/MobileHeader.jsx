import { useState } from 'react';
import { useSelector } from 'react-redux';
import { Button, Form, InputGroup } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { useHelp } from '../../context/HelpContext';

const MobileHeader = ({ user, onMenuToggle }) => {
  const navigate = useNavigate();
  const { showHelp } = useHelp();
  const [showSearch, setShowSearch] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // Navigate to tools page with search query
      navigate(`/tools?search=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery('');
      setShowSearch(false);
    }
  };

  return (
    <header className="mobile-header">
      <div className="mobile-header-content">
        <div className="mobile-header-left">
          <Button
            variant="link"
            className="mobile-menu-btn"
            onClick={onMenuToggle}
            aria-label="Open menu"
          >
            <i className="bi bi-list"></i>
          </Button>
          
          {!showSearch && (
            <Link to="/dashboard" className="mobile-brand">
              SupplyLine MRO
            </Link>
          )}
        </div>

        {showSearch ? (
          <Form onSubmit={handleSearch} className="mobile-search-form">
            <InputGroup>
              <Form.Control
                type="text"
                placeholder="Search tools..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                autoFocus
              />
              <Button variant="outline-secondary" type="submit">
                <i className="bi bi-search"></i>
              </Button>
              <Button 
                variant="outline-secondary" 
                onClick={() => setShowSearch(false)}
              >
                <i className="bi bi-x"></i>
              </Button>
            </InputGroup>
          </Form>
        ) : (
          <div className="mobile-header-right">
            <Button
              variant="link"
              className="mobile-search-btn"
              onClick={() => setShowSearch(true)}
              aria-label="Search"
            >
              <i className="bi bi-search"></i>
            </Button>
            
            <Button
              variant="link"
              className="mobile-notifications-btn"
              aria-label="Notifications"
            >
              <i className="bi bi-bell"></i>
              {/* Add notification badge if needed */}
            </Button>
            
            <Link to="/profile" className="mobile-profile-btn">
              {user?.avatar ? (
                <img
                  src={user.avatar}
                  alt="Profile"
                  className="mobile-avatar"
                />
              ) : (
                <div className="mobile-avatar-placeholder">
                  {user?.name?.charAt(0) || 'U'}
                </div>
              )}
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};

export default MobileHeader;
