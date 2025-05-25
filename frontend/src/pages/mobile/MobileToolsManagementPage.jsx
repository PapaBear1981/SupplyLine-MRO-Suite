import { useState, useEffect, useMemo } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useSearchParams } from 'react-router-dom';
import { fetchTools } from '../../store/toolsSlice';
import MobileToolList from '../../components/mobile/MobileToolList';

const MobileToolsManagementPage = () => {
  const dispatch = useDispatch();
  const [searchParams] = useSearchParams();
  const { tools, loading, error } = useSelector((state) => state.tools);

  useEffect(() => {
    dispatch(fetchTools());
  }, [dispatch]);

  const handleRefresh = () => {
    dispatch(fetchTools());
  };

  // Apply search filter from URL params with memoization
  const searchQuery = searchParams.get('search') || '';
  const filteredTools = useMemo(() => {
    if (!searchQuery) return tools;
    const lowerSearchQuery = searchQuery.toLowerCase();
    return tools.filter(tool =>
      tool.description?.toLowerCase().includes(lowerSearchQuery) ||
      tool.tool_number?.toLowerCase().includes(lowerSearchQuery) ||
      tool.serial_number?.toLowerCase().includes(lowerSearchQuery)
    );
  }, [tools, searchQuery]);

  // Handle error state
  if (error) {
    return (
      <div className="error-message p-3 text-center">
        <div className="alert alert-danger">
          <h5>Error loading tools</h5>
          <p>{error.message || error}</p>
          <button className="btn btn-primary" onClick={handleRefresh}>
            <i className="bi bi-arrow-clockwise me-2"></i>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <MobileToolList
      tools={filteredTools}
      loading={loading}
      error={error}
      onRefresh={handleRefresh}
      enablePullToRefresh={false}
    />
  );
};

export default MobileToolsManagementPage;
