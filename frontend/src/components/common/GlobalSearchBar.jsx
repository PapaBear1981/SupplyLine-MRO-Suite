import { useState, useEffect, useRef } from 'react';
import { Form, InputGroup, Dropdown, Spinner, Badge } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import api from '../../services/api';
import './GlobalSearchBar.css';

const GlobalSearchBar = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState({
    users: [],
    tools: [],
    chemicals: [],
    kits: []
  });
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const searchRef = useRef(null);
  const navigate = useNavigate();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Perform search with debouncing
  useEffect(() => {
    if (!searchQuery.trim()) {
      setResults({ users: [], tools: [], chemicals: [], kits: [] });
      setShowResults(false);
      return;
    }

    setLoading(true);
    const timeoutId = setTimeout(async () => {
      try {
        const query = encodeURIComponent(searchQuery);

        // Search across multiple entity types in parallel
        const [usersRes, toolsRes, chemicalsRes, kitsRes] = await Promise.allSettled([
          api.get(`/users?q=${query}&limit=5`),
          api.get(`/tools?search=${query}&limit=5`),
          api.get(`/chemicals?search=${query}&limit=5`),
          api.get(`/kits?search=${query}&limit=5`)
        ]);

        setResults({
          users: usersRes.status === 'fulfilled' ? usersRes.value.data.slice(0, 5) : [],
          tools: toolsRes.status === 'fulfilled' ? (Array.isArray(toolsRes.value.data) ? toolsRes.value.data.slice(0, 5) : toolsRes.value.data.tools?.slice(0, 5) || []) : [],
          chemicals: chemicalsRes.status === 'fulfilled' ? (Array.isArray(chemicalsRes.value.data) ? chemicalsRes.value.data.slice(0, 5) : chemicalsRes.value.data.chemicals?.slice(0, 5) || []) : [],
          kits: kitsRes.status === 'fulfilled' ? (Array.isArray(kitsRes.value.data) ? kitsRes.value.data.slice(0, 5) : kitsRes.value.data.kits?.slice(0, 5) || []) : []
        });
        setShowResults(true);
      } catch (error) {
        console.error('Search error:', error);
        toast.error('Search failed. Please try again.');
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  const handleResultClick = (type, id) => {
    setShowResults(false);
    setSearchQuery('');

    switch (type) {
      case 'user':
        navigate('/directory');
        break;
      case 'tool':
        navigate(`/tools/${id}`);
        break;
      case 'chemical':
        navigate(`/chemicals/${id}`);
        break;
      case 'kit':
        navigate(`/kits/${id}`);
        break;
      default:
        break;
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      setShowResults(false);
      setSearchQuery('');
    }
  };

  const hasResults = results.users.length > 0 ||
                     results.tools.length > 0 ||
                     results.chemicals.length > 0 ||
                     results.kits.length > 0;

  return (
    <div className="global-search-bar" ref={searchRef}>
      <InputGroup className="global-search-input-group">
        <InputGroup.Text className="border-end-0 bg-white">
          <i className="bi bi-search text-muted"></i>
        </InputGroup.Text>
        <Form.Control
          type="text"
          placeholder="Search users, tools, chemicals, kits..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onFocus={() => searchQuery && setShowResults(true)}
          onKeyDown={handleKeyDown}
          className="border-start-0 global-search-input"
          aria-label="Global search"
        />
        {loading && (
          <InputGroup.Text className="border-start-0 bg-white">
            <Spinner animation="border" size="sm" />
          </InputGroup.Text>
        )}
      </InputGroup>

      {showResults && searchQuery && (
        <div className="global-search-results">
          {!loading && !hasResults && (
            <div className="global-search-no-results">
              <i className="bi bi-search text-muted mb-2"></i>
              <p className="mb-0">No results found for "{searchQuery}"</p>
            </div>
          )}

          {results.users.length > 0 && (
            <div className="global-search-section">
              <div className="global-search-section-title">
                <i className="bi bi-people me-2"></i>
                Users
              </div>
              {results.users.map((user) => (
                <div
                  key={`user-${user.id}`}
                  className="global-search-item"
                  onClick={() => handleResultClick('user', user.id)}
                >
                  <div className="d-flex align-items-center">
                    <div className="global-search-item-icon">
                      {user.avatar ? (
                        <img src={user.avatar} alt={user.name} />
                      ) : (
                        <div className="avatar-placeholder">
                          {user.name?.charAt(0) || 'U'}
                        </div>
                      )}
                    </div>
                    <div>
                      <div className="global-search-item-title">{user.name}</div>
                      <div className="global-search-item-subtitle">
                        {user.badge_id && `Badge: ${user.badge_id}`}
                        {user.department && ` • ${user.department}`}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {results.tools.length > 0 && (
            <div className="global-search-section">
              <div className="global-search-section-title">
                <i className="bi bi-tools me-2"></i>
                Tools
              </div>
              {results.tools.map((tool) => (
                <div
                  key={`tool-${tool.id}`}
                  className="global-search-item"
                  onClick={() => handleResultClick('tool', tool.id)}
                >
                  <div>
                    <div className="global-search-item-title">
                      {tool.name || tool.description}
                      {tool.asset_tag && (
                        <Badge bg="secondary" className="ms-2">
                          {tool.asset_tag}
                        </Badge>
                      )}
                    </div>
                    <div className="global-search-item-subtitle">
                      {tool.manufacturer && `${tool.manufacturer}`}
                      {tool.model_number && ` • ${tool.model_number}`}
                      {tool.serial_number && ` • SN: ${tool.serial_number}`}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {results.chemicals.length > 0 && (
            <div className="global-search-section">
              <div className="global-search-section-title">
                <i className="bi bi-droplet me-2"></i>
                Chemicals
              </div>
              {results.chemicals.map((chemical) => (
                <div
                  key={`chemical-${chemical.id}`}
                  className="global-search-item"
                  onClick={() => handleResultClick('chemical', chemical.id)}
                >
                  <div>
                    <div className="global-search-item-title">{chemical.name}</div>
                    <div className="global-search-item-subtitle">
                      {chemical.cas_number && `CAS: ${chemical.cas_number}`}
                      {chemical.manufacturer && ` • ${chemical.manufacturer}`}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {results.kits.length > 0 && (
            <div className="global-search-section">
              <div className="global-search-section-title">
                <i className="bi bi-briefcase me-2"></i>
                Kits
              </div>
              {results.kits.map((kit) => (
                <div
                  key={`kit-${kit.id}`}
                  className="global-search-item"
                  onClick={() => handleResultClick('kit', kit.id)}
                >
                  <div>
                    <div className="global-search-item-title">{kit.name}</div>
                    <div className="global-search-item-subtitle">
                      {kit.kit_id && `ID: ${kit.kit_id}`}
                      {kit.type && ` • ${kit.type}`}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default GlobalSearchBar;
