import React, { useState, useEffect, useRef } from 'react';
import { Form, InputGroup, ListGroup, Spinner, Badge } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { FaSearch, FaTools, FaUser, FaTimes, FaFlask } from 'react-icons/fa';
import ToolService from '../../services/toolService';
import UserService from '../../services/userService';
import ChemicalService from '../../services/chemicalService';

const GlobalSearch = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState({ tools: [], users: [], chemicals: [] });
    const [loading, setLoading] = useState(false);
    const [showResults, setShowResults] = useState(false);
    const searchRef = useRef(null);
    const navigate = useNavigate();

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (searchRef.current && !searchRef.current.contains(event.target)) {
                setShowResults(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    useEffect(() => {
        const search = async () => {
            if (query.length < 2) {
                setResults({ tools: [], users: [], chemicals: [] });
                return;
            }

            setLoading(true);
            try {
                // Parallel execution for better performance
                const [toolsData, usersData, chemicalsData] = await Promise.allSettled([
                    ToolService.searchTools(query),
                    UserService.searchUsersByEmployeeNumber(query),
                    ChemicalService.searchChemicals(query)
                ]);

                const tools = toolsData.status === 'fulfilled'
                    ? (toolsData.value.tools || toolsData.value || [])
                    : [];

                const users = usersData.status === 'fulfilled'
                    ? (usersData.value.users || usersData.value || [])
                    : [];

                const chemicals = chemicalsData.status === 'fulfilled'
                    ? (chemicalsData.value.chemicals || chemicalsData.value || [])
                    : [];

                setResults({ tools, users, chemicals });
                setShowResults(true);
            } catch (error) {
                console.error('Global search error:', error);
            } finally {
                setLoading(false);
            }
        };

        const debounceTimer = setTimeout(search, 500);
        return () => clearTimeout(debounceTimer);
    }, [query]);

    const handleNavigate = (path) => {
        navigate(path);
        setShowResults(false);
        setQuery('');
    };

    return (
        <div className="global-search position-relative mb-4" ref={searchRef}>
            <InputGroup>
                <InputGroup.Text className="bg-body border-end-0">
                    <FaSearch className="text-muted" />
                </InputGroup.Text>
                <Form.Control
                    type="text"
                    placeholder="Search tools, chemicals, users..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onFocus={() => query.length >= 2 && setShowResults(true)}
                    className="border-start-0 shadow-none bg-body text-body"
                />
                {query && (
                    <InputGroup.Text
                        className="bg-body border-start-0 cursor-pointer"
                        onClick={() => {
                            setQuery('');
                            setResults({ tools: [], users: [], chemicals: [] });
                            setShowResults(false);
                        }}
                        style={{ cursor: 'pointer' }}
                    >
                        <FaTimes className="text-muted" />
                    </InputGroup.Text>
                )}
            </InputGroup>

            {showResults && (query.length >= 2) && (
                <div className="position-absolute w-100 mt-1 shadow-lg bg-body rounded border" style={{ zIndex: 1000, maxHeight: '400px', overflowY: 'auto' }}>
                    {loading ? (
                        <div className="p-3 text-center text-muted">
                            <Spinner animation="border" size="sm" className="me-2" />
                            Searching...
                        </div>
                    ) : (
                        <>
                            {results.tools.length === 0 && results.users.length === 0 && results.chemicals.length === 0 ? (
                                <div className="p-3 text-center text-muted">No results found</div>
                            ) : (
                                <ListGroup variant="flush">
                                    {results.tools.length > 0 && (
                                        <>
                                            <ListGroup.Item variant="light" className="fw-bold small text-uppercase text-muted bg-body-tertiary">
                                                <FaTools className="me-2" /> Tools ({results.tools.length})
                                            </ListGroup.Item>
                                            {results.tools.slice(0, 5).map(tool => (
                                                <ListGroup.Item
                                                    key={`tool-${tool.id}`}
                                                    action
                                                    onClick={() => handleNavigate(`/tools/${tool.id}`)}
                                                    className="d-flex justify-content-between align-items-center bg-body text-body border-bottom"
                                                >
                                                    <div>
                                                        <div className="fw-bold">{tool.tool_number} - {tool.description}</div>
                                                        <small className="text-muted">SN: {tool.serial_number || 'N/A'}</small>
                                                    </div>
                                                    <Badge bg={tool.status === 'available' ? 'success' : 'warning'}>
                                                        {tool.status}
                                                    </Badge>
                                                </ListGroup.Item>
                                            ))}
                                        </>
                                    )}

                                    {results.chemicals.length > 0 && (
                                        <>
                                            <ListGroup.Item variant="light" className="fw-bold small text-uppercase text-muted bg-body-tertiary">
                                                <FaFlask className="me-2" /> Chemicals ({results.chemicals.length})
                                            </ListGroup.Item>
                                            {results.chemicals.slice(0, 5).map(chem => (
                                                <ListGroup.Item
                                                    key={`chem-${chem.id}`}
                                                    action
                                                    onClick={() => handleNavigate(`/chemicals/${chem.id}`)}
                                                    className="d-flex justify-content-between align-items-center bg-body text-body border-bottom"
                                                >
                                                    <div>
                                                        <div className="fw-bold">{chem.part_number}</div>
                                                        <small className="text-muted">{chem.description}</small>
                                                    </div>
                                                    <Badge bg={chem.status === 'available' ? 'success' : 'warning'}>
                                                        {chem.status}
                                                    </Badge>
                                                </ListGroup.Item>
                                            ))}
                                        </>
                                    )}

                                    {results.users.length > 0 && (
                                        <>
                                            <ListGroup.Item variant="light" className="fw-bold small text-uppercase text-muted bg-body-tertiary">
                                                <FaUser className="me-2" /> Users ({results.users.length})
                                            </ListGroup.Item>
                                            {results.users.slice(0, 5).map(user => (
                                                <ListGroup.Item
                                                    key={`user-${user.id}`}
                                                    action
                                                    onClick={() => handleNavigate(`/directory?userId=${user.id}`)}
                                                    className="bg-body text-body border-bottom"
                                                >
                                                    <div className="fw-bold">{user.name}</div>
                                                    <small className="text-muted">{user.employee_number || user.email}</small>
                                                </ListGroup.Item>
                                            ))}
                                        </>
                                    )}
                                </ListGroup>
                            )}
                        </>
                    )}
                </div>
            )}
        </div>
    );
};

export default GlobalSearch;
