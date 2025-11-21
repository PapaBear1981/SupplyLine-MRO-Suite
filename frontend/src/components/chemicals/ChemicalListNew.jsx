import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Filter,
  X,
  ArrowUpDown,
  ShoppingCart,
  ArrowLeftRight,
  ScanLine,
  Eye,
  FlaskConical
} from 'lucide-react';

import { fetchChemicals } from '../../store/chemicalsSlice';
import api from '../../services/api';

// UI Components
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '../ui/pagination';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '../ui/collapsible';
import { Alert, AlertDescription } from '../ui/alert';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui/tooltip';

// Custom Components (Legacy)
import LoadingSpinner from '../common/LoadingSpinner';
import ChemicalBarcode from './ChemicalBarcode';
import ItemTransferModal from '../common/ItemTransferModal';
import ChemicalReorderModal from './ChemicalReorderModal';
import HelpIcon from '../common/HelpIcon';
import HelpContent from '../common/HelpContent';
import { useHelp } from '../../context/HelpContext';

const ChemicalListNew = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { chemicals, loading, error } = useSelector((state) => state.chemicals);
  const { showTooltips, showHelp } = useHelp();
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredChemicals, setFilteredChemicals] = useState([]);
  const [categoryFilter, setCategoryFilter] = useState('all');
  // Default to showing Available and Low Stock items (exclude Out Of Stock)
  const [statusFilter, setStatusFilter] = useState('available,low_stock');
  const [warehouseFilter, setWarehouseFilter] = useState('all');
  const [warehouses, setWarehouses] = useState([]);
  const [showBarcodeModal, setShowBarcodeModal] = useState(false);
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [showReorderModal, setShowReorderModal] = useState(false);
  const [selectedChemical, setSelectedChemical] = useState(null);
  const [showFilters, setShowFilters] = useState(false);

  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(30);

  // Sorting state
  const [sortConfig, setSortConfig] = useState({ key: 'part_number', direction: 'ascending' });

  // Fetch chemicals and warehouses on component mount
  useEffect(() => {
    dispatch(fetchChemicals());

    const fetchWarehouses = async () => {
      try {
        const response = await api.get('/warehouses');
        const warehousesData = response.data.warehouses || response.data;
        setWarehouses(Array.isArray(warehousesData) ? warehousesData : []);
      } catch (err) {
        console.error('Failed to fetch warehouses:', err);
      }
    };
    fetchWarehouses();
  }, [dispatch]);

  // Update filtered chemicals when chemicals, search term, or filters change
  useEffect(() => {
    if (!chemicals) return;

    let filtered = [...chemicals];

    // Apply search filter
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(
        (chemical) =>
          chemical.part_number.toLowerCase().includes(search) ||
          chemical.lot_number.toLowerCase().includes(search) ||
          (chemical.description && chemical.description.toLowerCase().includes(search)) ||
          (chemical.manufacturer && chemical.manufacturer.toLowerCase().includes(search))
      );
    }

    // Apply category filter
    if (categoryFilter && categoryFilter !== 'all') {
      filtered = filtered.filter((chemical) => chemical.category === categoryFilter);
    }

    // Apply status filter (supports multiple statuses separated by comma)
    if (statusFilter) {
      const allowedStatuses = statusFilter.split(',').map(s => s.trim());
      filtered = filtered.filter((chemical) => allowedStatuses.includes(chemical.status));
    }

    // Apply warehouse filter
    if (warehouseFilter && warehouseFilter !== 'all') {
      if (warehouseFilter === 'kits') {
        // Show only chemicals in kits (warehouse_id is null and kit_id is not null)
        filtered = filtered.filter((chemical) => chemical.warehouse_id === null && chemical.kit_id !== null);
      } else {
        // Show only chemicals in the selected warehouse
        filtered = filtered.filter((chemical) => chemical.warehouse_id === parseInt(warehouseFilter));
      }
    }

    // Apply sorting
    const sorted = [...filtered].sort((a, b) => {
      let aValue = a[sortConfig.key];
      let bValue = b[sortConfig.key];

      // Handle special cases for sorting
      if (sortConfig.key === 'quantity') {
        // Numeric sort for quantity
        aValue = parseFloat(aValue) || 0;
        bValue = parseFloat(bValue) || 0;
      } else if (sortConfig.key === 'expiration_date') {
        // Date sort with N/A values at the end
        if (!aValue || aValue === 'N/A') return 1;
        if (!bValue || bValue === 'N/A') return -1;
        aValue = new Date(aValue).getTime();
        bValue = new Date(bValue).getTime();
      } else if (sortConfig.key === 'warehouse_name') {
        // Sort by warehouse/kit name
        aValue = a.warehouse_id
          ? (warehouses.find(w => w.id === a.warehouse_id)?.name || '')
          : (a.kit_name || '');
        bValue = b.warehouse_id
          ? (warehouses.find(w => w.id === b.warehouse_id)?.name || '')
          : (b.kit_name || '');
      } else {
        // String sort (case-insensitive)
        aValue = (aValue || '').toString().toLowerCase();
        bValue = (bValue || '').toString().toLowerCase();
      }

      if (aValue < bValue) {
        return sortConfig.direction === 'ascending' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'ascending' ? 1 : -1;
      }
      return 0;
    });

    setFilteredChemicals(sorted);
    // Reset to page 1 when filters or sorting change
    setCurrentPage(1);
  }, [chemicals, searchTerm, categoryFilter, statusFilter, warehouseFilter, sortConfig, warehouses]);

  // Get unique categories for filter dropdown
  const categories = chemicals
    ? [...new Set(chemicals.map((chemical) => chemical.category))]
    : [];

  // Get unique statuses for filter dropdown
  const statuses = chemicals
    ? [...new Set(chemicals.map((chemical) => chemical.status))]
    : [];

  // Handle search
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  // Reset all filters to defaults
  const resetFilters = () => {
    setSearchTerm('');
    setCategoryFilter('all');
    setStatusFilter('available,low_stock'); // Reset to default (exclude Out Of Stock)
    setWarehouseFilter('all');
    setCurrentPage(1);
  };

  // Sorting handlers
  const handleSort = (key) => {
    setSortConfig({
      key,
      direction:
        sortConfig.key === key && sortConfig.direction === 'ascending'
          ? 'descending'
          : 'ascending',
    });
  };

  const getSortIcon = (key) => {
    if (sortConfig.key !== key) return null;
    return sortConfig.direction === 'ascending' ? '↑' : '↓';
  };

  // Calculate pagination
  const totalPages = Math.ceil(filteredChemicals.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedChemicals = filteredChemicals.slice(startIndex, endIndex);

  // Pagination handlers
  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Get status badge variant
  const getStatusBadgeVariant = (status) => {
    switch (status) {
      case 'available':
        return 'default'; // Green
      case 'low_stock':
        return 'secondary'; // Yellow
      case 'out_of_stock':
        return 'destructive'; // Red
      case 'expired':
        return 'outline'; // Dark/outlined
      default:
        return 'secondary';
    }
  };

  // Format status for display
  const formatStatus = (status) => {
    return status
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Handle barcode button click
  const handleBarcodeClick = (chemical) => {
    setSelectedChemical(chemical);
    setShowBarcodeModal(true);
  };

  // Handle transfer button click
  const handleTransferClick = (chemical) => {
    setSelectedChemical(chemical);
    setShowTransferModal(true);
  };

  // Handle reorder button click
  const handleReorderClick = (chemical) => {
    setSelectedChemical(chemical);
    setShowReorderModal(true);
  };

  if (loading && !chemicals.length) {
    return <LoadingSpinner />;
  }

  return (
    <TooltipProvider>
      {showHelp && (
        <HelpContent title="Chemical Inventory" initialOpen={false}>
          <p>This page displays all active chemicals in the inventory. You can search, filter, sort, and manage chemicals from this view.</p>
          <ul>
            <li><strong>Search:</strong> Use the search box to find chemicals by part number, lot number, description, or manufacturer.</li>
            <li><strong>Filters:</strong> Filter chemicals by category or status using the dropdown menus.</li>
            <li><strong>Sort:</strong> Click on any column header to sort the table by that column.</li>
            <li><strong>View:</strong> Click the "View" button to see detailed information about a chemical.</li>
            <li><strong>Issue:</strong> Click the "Issue" button to issue a chemical to a user or department.</li>
            <li><strong>Barcode:</strong> Click the barcode icon to generate and print a barcode for the chemical.</li>
            <li><strong>Status:</strong> Chemical status is color-coded:
              <ul>
                <li>Green: Available</li>
                <li>Yellow: Low Stock</li>
                <li>Red: Out of Stock</li>
                <li>Dark: Expired</li>
              </ul>
            </li>
          </ul>
        </HelpContent>
      )}

      <Card className="shadow-sm border-border">
        <CardHeader className="bg-muted/50 dark:bg-muted/20">
          <div className="flex flex-wrap justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <FlaskConical className="h-6 w-6 text-primary" />
              <CardTitle className="text-2xl">Chemical Inventory</CardTitle>
              {showHelp && (
                <HelpIcon
                  title="Chemical Inventory"
                  content={
                    <>
                      <p>This table shows all active chemicals in the inventory.</p>
                      <p>Use the search, filter, and sort options to find specific chemicals.</p>
                      <ul>
                        <li>Search for chemicals by part number, lot number, description, or manufacturer</li>
                        <li>Filter chemicals by category, status, or location</li>
                        <li>Sort the table by clicking on column headers</li>
                        <li>View chemical details, issue chemicals, or generate barcodes using the action buttons</li>
                      </ul>
                    </>
                  }
                  size="sm"
                />
              )}
            </div>
            <div className="flex gap-2">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="outline" onClick={resetFilters} size="sm">
                    <X className="h-4 w-4 mr-1" />
                    Reset Filters
                  </Button>
                </TooltipTrigger>
                {showTooltips && (
                  <TooltipContent>Clear all search filters</TooltipContent>
                )}
              </Tooltip>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertDescription>{error.message}</AlertDescription>
            </Alert>
          )}

          {/* Search and Filters */}
          <div className="mb-6 space-y-4">
            {/* Search Bar */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
              <Input
                placeholder="Search by part number, lot number, description, or manufacturer..."
                value={searchTerm}
                onChange={handleSearch}
                className="pl-10"
              />
            </div>

            {/* Advanced Filters Toggle */}
            <Collapsible open={showFilters} onOpenChange={setShowFilters}>
              <CollapsibleTrigger asChild>
                <Button variant="outline" size="sm" className="w-full sm:w-auto">
                  <Filter className="h-4 w-4 mr-2" />
                  {showFilters ? 'Hide Filters' : 'Show Filters'}
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="mt-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  {/* Category Filter */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Category</label>
                    <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                      <SelectTrigger>
                        <SelectValue placeholder="All Categories" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Categories</SelectItem>
                        {categories.map((category) => (
                          <SelectItem key={category} value={category}>
                            {category}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Status Filter */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Status</label>
                    <Select value={statusFilter} onValueChange={setStatusFilter}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="available,low_stock">Available & Low Stock</SelectItem>
                        <SelectItem value="">All Statuses</SelectItem>
                        {statuses.map((status) => (
                          <SelectItem key={status} value={status}>
                            {formatStatus(status)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Warehouse Filter */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Location</label>
                    <Select value={warehouseFilter} onValueChange={setWarehouseFilter}>
                      <SelectTrigger>
                        <SelectValue placeholder="All Locations" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Locations</SelectItem>
                        <SelectItem value="kits">In Kits</SelectItem>
                        {warehouses.map((warehouse) => (
                          <SelectItem key={warehouse.id} value={warehouse.id.toString()}>
                            {warehouse.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CollapsibleContent>
            </Collapsible>
          </div>

          {/* Results Count */}
          <div className="mb-4 text-sm text-muted-foreground">
            Showing {startIndex + 1}-{Math.min(endIndex, filteredChemicals.length)} of {filteredChemicals.length} chemicals
          </div>

          {filteredChemicals.length === 0 ? (
            <Alert>
              <AlertDescription>
                No chemicals found. {searchTerm || categoryFilter !== 'all' || statusFilter || warehouseFilter !== 'all' ? 'Try adjusting your filters.' : ''}
              </AlertDescription>
            </Alert>
          ) : (
            <div className="rounded-md border overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="bg-muted/50 hover:bg-muted/50">
                    <TableHead
                      onClick={() => handleSort('part_number')}
                      className="cursor-pointer hover:bg-muted/80 transition-colors"
                    >
                      <div className="flex items-center gap-1">
                        Part Number
                        <ArrowUpDown className="h-4 w-4" />
                        {getSortIcon('part_number') && <span className="ml-1">{getSortIcon('part_number')}</span>}
                      </div>
                    </TableHead>
                    <TableHead
                      onClick={() => handleSort('lot_number')}
                      className="cursor-pointer hover:bg-muted/80 transition-colors"
                    >
                      <div className="flex items-center gap-1">
                        Lot Number
                        <ArrowUpDown className="h-4 w-4" />
                        {getSortIcon('lot_number') && <span className="ml-1">{getSortIcon('lot_number')}</span>}
                      </div>
                    </TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead
                      onClick={() => handleSort('manufacturer')}
                      className="cursor-pointer hover:bg-muted/80 transition-colors"
                    >
                      <div className="flex items-center gap-1">
                        Manufacturer
                        <ArrowUpDown className="h-4 w-4" />
                        {getSortIcon('manufacturer') && <span className="ml-1">{getSortIcon('manufacturer')}</span>}
                      </div>
                    </TableHead>
                    <TableHead
                      onClick={() => handleSort('quantity')}
                      className="cursor-pointer hover:bg-muted/80 transition-colors"
                    >
                      <div className="flex items-center gap-1">
                        Quantity
                        <ArrowUpDown className="h-4 w-4" />
                        {getSortIcon('quantity') && <span className="ml-1">{getSortIcon('quantity')}</span>}
                      </div>
                    </TableHead>
                    <TableHead
                      onClick={() => handleSort('location')}
                      className="cursor-pointer hover:bg-muted/80 transition-colors"
                    >
                      <div className="flex items-center gap-1">
                        Location
                        <ArrowUpDown className="h-4 w-4" />
                        {getSortIcon('location') && <span className="ml-1">{getSortIcon('location')}</span>}
                      </div>
                    </TableHead>
                    <TableHead
                      onClick={() => handleSort('warehouse_name')}
                      className="cursor-pointer hover:bg-muted/80 transition-colors"
                    >
                      <div className="flex items-center gap-1">
                        Warehouse
                        <ArrowUpDown className="h-4 w-4" />
                        {getSortIcon('warehouse_name') && <span className="ml-1">{getSortIcon('warehouse_name')}</span>}
                      </div>
                    </TableHead>
                    <TableHead
                      onClick={() => handleSort('expiration_date')}
                      className="cursor-pointer hover:bg-muted/80 transition-colors"
                    >
                      <div className="flex items-center gap-1">
                        Expiration Date
                        <ArrowUpDown className="h-4 w-4" />
                        {getSortIcon('expiration_date') && <span className="ml-1">{getSortIcon('expiration_date')}</span>}
                      </div>
                    </TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {paginatedChemicals.map((chemical) => (
                    <TableRow key={chemical.id} className="hover:bg-muted/50 transition-colors">
                      <TableCell className="font-medium">{chemical.part_number}</TableCell>
                      <TableCell>{chemical.lot_number}</TableCell>
                      <TableCell className="max-w-xs truncate">{chemical.description}</TableCell>
                      <TableCell>{chemical.manufacturer}</TableCell>
                      <TableCell>
                        {chemical.quantity} {chemical.unit}
                      </TableCell>
                      <TableCell>
                        {chemical.warehouse_id ? (
                          chemical.location || 'N/A'
                        ) : chemical.box_number ? (
                          <Badge variant="secondary">{chemical.box_number}</Badge>
                        ) : (
                          'N/A'
                        )}
                      </TableCell>
                      <TableCell>
                        {chemical.warehouse_id ? (
                          <Badge variant="outline" className="bg-blue-50 dark:bg-blue-950">
                            {warehouses.find(w => w.id === chemical.warehouse_id)?.name || `Warehouse ${chemical.warehouse_id}`}
                          </Badge>
                        ) : chemical.kit_name ? (
                          <Badge variant="secondary">{chemical.kit_name}</Badge>
                        ) : (
                          <Badge variant="secondary">Unknown</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        {chemical.expiration_date
                          ? new Date(chemical.expiration_date).toLocaleDateString()
                          : 'N/A'}
                      </TableCell>
                      <TableCell>
                        <Badge variant={getStatusBadgeVariant(chemical.status)}>
                          {formatStatus(chemical.status)}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1 justify-end">
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button
                                onClick={() => navigate(`/chemicals/${chemical.id}`)}
                                variant="outline"
                                size="sm"
                              >
                                <Eye className="h-4 w-4" />
                              </Button>
                            </TooltipTrigger>
                            {showTooltips && (
                              <TooltipContent>View chemical details</TooltipContent>
                            )}
                          </Tooltip>
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button
                                onClick={() => navigate(`/chemicals/${chemical.id}/issue`)}
                                variant="default"
                                size="sm"
                                disabled={chemical.status === 'out_of_stock' || chemical.status === 'expired'}
                              >
                                <FlaskConical className="h-4 w-4" />
                              </Button>
                            </TooltipTrigger>
                            {showTooltips && (
                              <TooltipContent>
                                {chemical.status === 'out_of_stock' || chemical.status === 'expired' ?
                                  "Cannot issue chemicals that are out of stock or expired" :
                                  "Issue this chemical to a user or department"}
                              </TooltipContent>
                            )}
                          </Tooltip>
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleTransferClick(chemical)}
                              >
                                <ArrowLeftRight className="h-4 w-4" />
                              </Button>
                            </TooltipTrigger>
                            {showTooltips && (
                              <TooltipContent>Transfer this chemical to another location</TooltipContent>
                            )}
                          </Tooltip>
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleReorderClick(chemical)}
                              >
                                <ShoppingCart className="h-4 w-4" />
                              </Button>
                            </TooltipTrigger>
                            {showTooltips && (
                              <TooltipContent>Reorder this chemical</TooltipContent>
                            )}
                          </Tooltip>
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleBarcodeClick(chemical)}
                              >
                                <ScanLine className="h-4 w-4" />
                              </Button>
                            </TooltipTrigger>
                            {showTooltips && (
                              <TooltipContent>Generate barcode for this chemical</TooltipContent>
                            )}
                          </Tooltip>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="mt-4 flex justify-center">
              <Pagination>
                <PaginationContent>
                  <PaginationItem>
                    <PaginationPrevious
                      onClick={() => currentPage > 1 && handlePageChange(currentPage - 1)}
                      className={currentPage === 1 ? 'pointer-events-none opacity-50' : 'cursor-pointer'}
                    />
                  </PaginationItem>

                  {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
                    // Show first page, last page, current page, and pages around current
                    if (
                      page === 1 ||
                      page === totalPages ||
                      (page >= currentPage - 1 && page <= currentPage + 1)
                    ) {
                      return (
                        <PaginationItem key={page}>
                          <PaginationLink
                            onClick={() => handlePageChange(page)}
                            isActive={page === currentPage}
                            className="cursor-pointer"
                          >
                            {page}
                          </PaginationLink>
                        </PaginationItem>
                      );
                    } else if (page === currentPage - 2 || page === currentPage + 2) {
                      return (
                        <PaginationItem key={page}>
                          <PaginationEllipsis />
                        </PaginationItem>
                      );
                    }
                    return null;
                  })}

                  <PaginationItem>
                    <PaginationNext
                      onClick={() => currentPage < totalPages && handlePageChange(currentPage + 1)}
                      className={currentPage === totalPages ? 'pointer-events-none opacity-50' : 'cursor-pointer'}
                    />
                  </PaginationItem>
                </PaginationContent>
              </Pagination>
            </div>
          )}
        </CardContent>
      </Card>

      {showBarcodeModal && (
        <ChemicalBarcode
          show={showBarcodeModal}
          onHide={() => setShowBarcodeModal(false)}
          chemical={selectedChemical}
        />
      )}

      {/* Transfer Modal */}
      {selectedChemical && (
        <ItemTransferModal
          show={showTransferModal}
          onHide={() => setShowTransferModal(false)}
          item={selectedChemical}
          itemType="chemical"
          onTransferComplete={() => {
            dispatch(fetchChemicals());
          }}
        />
      )}

      {/* Reorder Modal */}
      {selectedChemical && (
        <ChemicalReorderModal
          show={showReorderModal}
          onHide={() => setShowReorderModal(false)}
          chemical={selectedChemical}
        />
      )}
    </TooltipProvider>
  );
};

export default ChemicalListNew;
