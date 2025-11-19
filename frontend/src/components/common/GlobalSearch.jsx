import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, InputGroup, ListGroup, Spinner } from 'react-bootstrap';
import { toast } from 'react-toastify';
import api from '../../services/api';
import './GlobalSearch.css';

const GlobalSearch = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const searchRef = useRef(null);
  const inputRef = useRef(null);
  const navigate = useNavigate();

  // Debounce search
  useEffect(() => {
    if (query.length < 2) {
      setResults(null);
      setShowResults(false);
      return;
    }

    const timeoutId = setTimeout(() => {
      performSearch(query);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query]);

  const performSearch = async (searchQuery) => {
    setLoading(true);
    try {
      const response = await api.get('/api/search/global', {
        params: { q: searchQuery }
      });
      setResults(response.data);
      setShowResults(true);
      setSelectedIndex(-1);
    } catch (err) {
      console.error('Search error:', err);
      toast.error('Search failed. Please try again.');
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  // Click outside to close
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ctrl+K or Cmd+K to focus search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }

      // Escape to close results
      if (e.key === 'Escape') {
        setShowResults(false);
        inputRef.current?.blur();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleNavigate = useCallback((item) => {
    let path = '';
    switch (item.type) {
      case 'tool':
        path = `/tools/${item.id}`;
        break;
      case 'kit':
        path = `/kits/${item.id}`;
        break;
      case 'chemical':
        path = `/chemicals/${item.id}`;
        break;
      case 'user':
        path = `/directory?user=${item.id}`;
        break;
      default:
        return;
    }
    navigate(path);
    setQuery('');
    setShowResults(false);
    inputRef.current?.blur();
  }, [navigate]);

  // Keyboard navigation in results
  const handleKeyDown = (e) => {
    if (!showResults || !results) return;

    const allResults = [
      ...(results.tools || []),
      ...(results.kits || []),
      ...(results.chemicals || []),
      ...(results.users || [])
    ];

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) =>
        prev < allResults.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1));
    } else if (e.key === 'Enter' && selectedIndex >= 0) {
      e.preventDefault();
      handleNavigate(allResults[selectedIndex]);
    }
  };

  const renderResultItem = (item, index) => {
    const isSelected = index === selectedIndex;
    let icon = '';
    let primaryText = '';
    let secondaryText = '';

    switch (item.type) {
      case 'tool':
        icon = 'tools';
        primaryText = item.tool_number;
        secondaryText = item.description;
        break;
      case 'kit':
        icon = 'box';
        primaryText = item.kit_number;
        secondaryText = item.description;
        break;
      case 'chemical':
        icon = 'flask';
        primaryText = item.name;
        secondaryText = `CAS: ${item.cas_number || 'N/A'} | Part: ${item.part_number || 'N/A'}`;
        break;
      case 'user':
        icon = 'person';
        primaryText = item.name;
        secondaryText = `${item.email} | ${item.department || 'N/A'}`;
        break;
      default:
        return null;
    }

    return (
      <ListGroup.Item
        key={`${item.type}-${item.id}`}
        action
        active={isSelected}
        onClick={() => handleNavigate(item)}
        className="global-search-result-item"
      >
        <div className="d-flex align-items-center">
          <i className={`bi bi-${icon} me-3 fs-5`}></i>
          <div className="flex-grow-1">
            <div className="fw-bold">{primaryText}</div>
            <small className="text-muted">{secondaryText}</small>
          </div>
          <span className={`badge bg-${getTypeBadgeColor(item.type)}`}>
            {item.type}
          </span>
        </div>
      </ListGroup.Item>
    );
  };

  const getTypeBadgeColor = (type) => {
    switch (type) {
      case 'tool': return 'primary';
      case 'kit': return 'success';
      case 'chemical': return 'warning';
      case 'user': return 'info';
      default: return 'secondary';
    }
  };

  const renderResults = () => {
    if (!results) return null;

    const { tools = [], kits = [], chemicals = [], users = [], totalResults = 0 } = results;

    if (totalResults === 0) {
      return (
        <div className="global-search-results">
          <div className="p-3 text-center text-muted">
            <i className="bi bi-search fs-3"></i>
            <p className="mb-0 mt-2">No results found for "{query}"</p>
          </div>
        </div>
      );
    }

    let currentIndex = 0;

    return (
      <div className="global-search-results">
        <div className="p-2 bg-light border-bottom">
          <small className="text-muted">
            Found {totalResults} result{totalResults !== 1 ? 's' : ''}
          </small>
        </div>
        <ListGroup variant="flush" className="global-search-list">
          {tools.length > 0 && (
            <>
              <ListGroup.Item className="bg-light text-muted small fw-bold">
                <i className="bi bi-tools me-2"></i>Tools ({tools.length})
              </ListGroup.Item>
              {tools.map((tool) => renderResultItem(tool, currentIndex++))}
            </>
          )}
          {kits.length > 0 && (
            <>
              <ListGroup.Item className="bg-light text-muted small fw-bold">
                <i className="bi bi-box me-2"></i>Kits ({kits.length})
              </ListGroup.Item>
              {kits.map((kit) => renderResultItem(kit, currentIndex++))}
            </>
          )}
          {chemicals.length > 0 && (
            <>
              <ListGroup.Item className="bg-light text-muted small fw-bold">
                <i className="bi bi-flask me-2"></i>Chemicals ({chemicals.length})
              </ListGroup.Item>
              {chemicals.map((chemical) => renderResultItem(chemical, currentIndex++))}
            </>
          )}
          {users.length > 0 && (
            <>
              <ListGroup.Item className="bg-light text-muted small fw-bold">
                <i className="bi bi-person me-2"></i>Users ({users.length})
              </ListGroup.Item>
              {users.map((user) => renderResultItem(user, currentIndex++))}
            </>
          )}
        </ListGroup>
      </div>
    );
  };

  return (
    <div className="global-search-container" ref={searchRef}>
      <InputGroup className="global-search-input">
        <InputGroup.Text className="bg-white border-end-0">
          <i className="bi bi-search text-muted"></i>
        </InputGroup.Text>
        <Form.Control
          ref={inputRef}
          type="text"
          placeholder="Search tools, kits, chemicals, users... (Ctrl+K)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => query.length >= 2 && setShowResults(true)}
          className="border-start-0"
        />
        {loading && (
          <InputGroup.Text className="bg-white border-start-0">
            <Spinner animation="border" size="sm" variant="primary" />
          </InputGroup.Text>
        )}
        {query && !loading && (
          <InputGroup.Text
            className="bg-white border-start-0 cursor-pointer"
            onClick={() => setQuery('')}
            role="button"
            aria-label="Clear search"
          >
            <i className="bi bi-x-circle text-muted"></i>
          </InputGroup.Text>
        )}
      </InputGroup>
      {showResults && renderResults()}
    </div>
  );
};

export default GlobalSearch;
