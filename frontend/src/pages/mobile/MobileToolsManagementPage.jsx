import { useState, useEffect } from 'react';
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

  // Apply search filter from URL params
  const searchQuery = searchParams.get('search') || '';
  const filteredTools = searchQuery
    ? tools.filter(tool =>
        tool.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tool.part_number?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : tools;

  return (
    <MobileToolList
      tools={filteredTools}
      loading={loading}
      onRefresh={handleRefresh}
      enablePullToRefresh={false}
    />
  );
};

export default MobileToolsManagementPage;
