import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import {
    Search,
    Filter,
    X,
    ArrowUpDown,
    MoreHorizontal,
    CheckCircle,
    User,
    Wrench,
    Archive,
    ArrowLeftRight,
    ScanLine,
    Trash2,
    Eye,
    RotateCcw,
    AlertTriangle
} from 'lucide-react';

import { fetchTools } from '../../store/toolsSlice';
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
import { Switch } from '../ui/switch';
import { Label } from '../ui/label';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui/tooltip';

// Custom Components (Legacy or New)
import LoadingSpinner from '../common/LoadingSpinner'; // Need to check if this is migrated or usable
import CheckoutModal from '../checkouts/CheckoutModal'; // Legacy
import ReturnToolModal from '../checkouts/ReturnToolModal'; // Legacy
import ReturnToServiceModal from './ReturnToServiceModal'; // Legacy
import ToolBarcode from './ToolBarcode'; // Legacy
import DeleteToolModal from './DeleteToolModal'; // Legacy
import CalibrationStatusIndicator from './CalibrationStatusIndicator'; // Legacy
import ItemTransferModal from '../common/ItemTransferModal'; // Legacy
import HelpIcon from '../common/HelpIcon'; // Legacy

const ToolListNew = ({ workflowFilter = 'all' }) => {
    const dispatch = useDispatch();
    const { tools, loading } = useSelector((state) => state.tools);
    const { user } = useSelector((state) => state.auth);

    const [searchQuery, setSearchQuery] = useState('');
    const [filteredTools, setFilteredTools] = useState([]);
    const [sortConfig, setSortConfig] = useState({ key: 'tool_number', direction: 'ascending' });

    // Modal States
    const [showCheckoutModal, setShowCheckoutModal] = useState(false);
    const [showBarcodeModal, setShowBarcodeModal] = useState(false);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [showTransferModal, setShowTransferModal] = useState(false);
    const [showReturnModal, setShowReturnModal] = useState(false);
    const [showServiceModal, setShowServiceModal] = useState(false);
    const [selectedTool, setSelectedTool] = useState(null);

    // Filter states
    const [showFilters, setShowFilters] = useState(false);
    const [categoryFilter, setCategoryFilter] = useState('all');
    const [locationFilter, setLocationFilter] = useState('all');
    const [warehouseFilter, setWarehouseFilter] = useState('all');

    // Pagination states
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage] = useState(30);

    // Data for filters
    const [availableCategories, setAvailableCategories] = useState([]);
    const [availableLocations, setAvailableLocations] = useState([]);
    const [warehouses, setWarehouses] = useState([]);

    const isAdmin = user?.is_admin || user?.department === 'Materials';

    useEffect(() => {
        dispatch(fetchTools());

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

    useEffect(() => {
        if (tools && tools.length > 0) {
            const categories = [...new Set(tools.map(tool => tool.category || 'General').filter(Boolean))];
            setAvailableCategories(categories.sort());

            const locations = [...new Set(tools.map(tool => tool.location).filter(Boolean))];
            setAvailableLocations(locations.sort());
        }
    }, [tools]);

    useEffect(() => {
        let toolsToDisplay = [...tools];

        // Apply workflow filter based on tab
        if (workflowFilter === 'available') {
            toolsToDisplay = toolsToDisplay.filter(tool => tool.status === 'available');
        } else if (workflowFilter === 'in_use') {
            toolsToDisplay = toolsToDisplay.filter(tool => tool.status === 'checked_out');
        } else if (workflowFilter === 'maintenance') {
            toolsToDisplay = toolsToDisplay.filter(tool => tool.status === 'maintenance');
        } else if (workflowFilter === 'calibration') {
            toolsToDisplay = toolsToDisplay.filter(tool =>
                tool.requires_calibration &&
                tool.calibration_status &&
                (tool.calibration_status === 'due_soon' || tool.calibration_status === 'overdue')
            );
        } else if (workflowFilter === 'retired') {
            toolsToDisplay = toolsToDisplay.filter(tool => tool.status === 'retired');
        }
        // 'all' shows everything

        // Apply search query
        if (searchQuery.trim()) {
            const query = searchQuery.toLowerCase();
            toolsToDisplay = toolsToDisplay.filter(tool =>
                tool.tool_number.toLowerCase().includes(query) ||
                tool.serial_number.toLowerCase().includes(query) ||
                (tool.description && tool.description.toLowerCase().includes(query)) ||
                (tool.location && tool.location.toLowerCase().includes(query))
            );
        }

        // Apply category filter
        if (categoryFilter && categoryFilter !== 'all') {
            toolsToDisplay = toolsToDisplay.filter(tool => (tool.category || 'General') === categoryFilter);
        }

        // Apply location filter
        if (locationFilter && locationFilter !== 'all') {
            toolsToDisplay = toolsToDisplay.filter(tool => tool.location === locationFilter);
        }

        // Apply warehouse filter
        if (warehouseFilter && warehouseFilter !== 'all') {
            if (warehouseFilter === 'in_kit') {
                toolsToDisplay = toolsToDisplay.filter(tool => tool.warehouse_id === null || tool.warehouse_id === undefined);
            } else {
                toolsToDisplay = toolsToDisplay.filter(tool => tool.warehouse_id === parseInt(warehouseFilter));
            }
        }

        // Sort tools
        const sortedTools = [...toolsToDisplay].sort((a, b) => {
            if (a[sortConfig.key] < b[sortConfig.key]) {
                return sortConfig.direction === 'ascending' ? -1 : 1;
            }
            if (a[sortConfig.key] > b[sortConfig.key]) {
                return sortConfig.direction === 'ascending' ? 1 : -1;
            }
            return 0;
        });

        setFilteredTools(sortedTools);
        setCurrentPage(1);
    }, [tools, searchQuery, sortConfig, workflowFilter, categoryFilter, locationFilter, warehouseFilter]);

    const handleSort = (key) => {
        setSortConfig({
            key,
            direction:
                sortConfig.key === key && sortConfig.direction === 'ascending'
                    ? 'descending'
                    : 'ascending',
        });
    };

    // Pagination Logic
    const totalPages = Math.ceil(filteredTools.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedTools = filteredTools.slice(startIndex, endIndex);

    const handlePageChange = (page) => {
        setCurrentPage(page);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    // Modal Handlers
    const handleCheckoutClick = (tool) => {
        setSelectedTool(tool);
        setShowCheckoutModal(true);
    };

    const handleBarcodeClick = (tool) => {
        setSelectedTool(tool);
        setShowBarcodeModal(true);
    };

    const handleTransferClick = (tool) => {
        setSelectedTool(tool);
        setShowTransferModal(true);
    };

    const handleDeleteClick = (tool) => {
        setSelectedTool(tool);
        setShowDeleteModal(true);
    };

    const handleReturnClick = (tool) => {
        setSelectedTool(tool);
        setShowReturnModal(true);
    };

    const handleServiceClick = (tool) => {
        setSelectedTool(tool);
        setShowServiceModal(true);
    };

    const handleToolDelete = () => {
        dispatch(fetchTools());
    };

    const handleToolRetire = () => {
        dispatch(fetchTools());
    };

    const resetFilters = () => {
        setCategoryFilter('all');
        setLocationFilter('all');
        setWarehouseFilter('all');
        setSearchQuery('');
    };

    const activeFilterCount = [
        categoryFilter !== 'all',
        locationFilter !== 'all',
        warehouseFilter !== 'all',
        searchQuery.trim() !== ''
    ].filter(Boolean).length;

    // Get workflow description based on current filter
    const getWorkflowDescription = () => {
        switch (workflowFilter) {
            case 'available':
                return 'Tools ready for checkout';
            case 'in_use':
                return 'Tools currently checked out to users';
            case 'maintenance':
                return 'Tools removed from service for maintenance or repair';
            case 'calibration':
                return 'Tools requiring calibration attention';
            case 'retired':
                return 'Tools retired from active service';
            case 'all':
                return 'All tools in inventory';
            default:
                return '';
        }
    };

    if (loading && !filteredTools.length) {
        return <LoadingSpinner />;
    }

    return (
        <div className="space-y-4">
            <Card>
                <CardHeader className="pb-3">
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                        <div className="flex flex-col gap-1">
                            <div className="flex items-center gap-2">
                                <CardTitle>{getWorkflowDescription()}</CardTitle>
                                <Badge variant="secondary" className="ml-2">
                                    {filteredTools.length} {filteredTools.length === 1 ? 'item' : 'items'}
                                </Badge>
                            </div>
                        </div>

                        <div className="flex flex-col sm:flex-row gap-2 w-full md:w-auto">
                            <div className="relative w-full sm:w-64">
                                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="Search tools..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="pl-8"
                                />
                                {searchQuery && (
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="absolute right-0 top-0 h-9 w-9"
                                        onClick={() => setSearchQuery('')}
                                    >
                                        <X className="h-4 w-4" />
                                    </Button>
                                )}
                            </div>

                            <Collapsible open={showFilters} onOpenChange={setShowFilters}>
                                <CollapsibleTrigger asChild>
                                    <Button variant="outline" className="w-full sm:w-auto gap-2">
                                        <Filter className="h-4 w-4" />
                                        Filters
                                        {activeFilterCount > 0 && (
                                            <Badge variant="secondary" className="ml-1 px-1.5 py-0.5 h-5 min-w-[1.25rem]">
                                                {activeFilterCount}
                                            </Badge>
                                        )}
                                    </Button>
                                </CollapsibleTrigger>
                            </Collapsible>
                        </div>
                    </div>

                    <Collapsible open={showFilters}>
                        <CollapsibleContent className="pt-4 space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                <div className="space-y-2">
                                    <Label>Category</Label>
                                    <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                                        <SelectTrigger>
                                            <SelectValue placeholder="All Categories" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="all">All Categories</SelectItem>
                                            {availableCategories.map(category => (
                                                <SelectItem key={category} value={category}>{category}</SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="space-y-2">
                                    <Label>Location</Label>
                                    <Select value={locationFilter} onValueChange={setLocationFilter}>
                                        <SelectTrigger>
                                            <SelectValue placeholder="All Locations" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="all">All Locations</SelectItem>
                                            {availableLocations.map(location => (
                                                <SelectItem key={location} value={location}>{location}</SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="space-y-2">
                                    <Label>Warehouse</Label>
                                    <Select value={warehouseFilter} onValueChange={setWarehouseFilter}>
                                        <SelectTrigger>
                                            <SelectValue placeholder="All Warehouses" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="all">All Warehouses</SelectItem>
                                            <SelectItem value="in_kit">In Kit</SelectItem>
                                            {warehouses.map(warehouse => (
                                                <SelectItem key={warehouse.id} value={warehouse.id.toString()}>
                                                    {warehouse.name}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>

                            <div className="flex justify-end pt-2 border-t">
                                <Button variant="ghost" onClick={resetFilters} size="sm">
                                    Reset Filters
                                </Button>
                            </div>
                        </CollapsibleContent>
                    </Collapsible>
                </CardHeader>
                <CardContent className="p-0">
                    <div className="rounded-md border">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead className="cursor-pointer" onClick={() => handleSort('tool_number')}>
                                        Tool Number <ArrowUpDown className="ml-2 h-4 w-4 inline" />
                                    </TableHead>
                                    <TableHead className="cursor-pointer" onClick={() => handleSort('serial_number')}>
                                        Serial <ArrowUpDown className="ml-2 h-4 w-4 inline" />
                                    </TableHead>
                                    <TableHead className="cursor-pointer" onClick={() => handleSort('description')}>
                                        Description <ArrowUpDown className="ml-2 h-4 w-4 inline" />
                                    </TableHead>
                                    <TableHead className="hidden md:table-cell cursor-pointer" onClick={() => handleSort('category')}>
                                        Category <ArrowUpDown className="ml-2 h-4 w-4 inline" />
                                    </TableHead>
                                    <TableHead className="hidden md:table-cell cursor-pointer" onClick={() => handleSort('location')}>
                                        Location <ArrowUpDown className="ml-2 h-4 w-4 inline" />
                                    </TableHead>
                                    <TableHead className="hidden lg:table-cell">Warehouse</TableHead>
                                    <TableHead className="cursor-pointer" onClick={() => handleSort('status')}>
                                        Status <ArrowUpDown className="ml-2 h-4 w-4 inline" />
                                    </TableHead>
                                    <TableHead className="hidden xl:table-cell">Calibration</TableHead>
                                    <TableHead className="text-right">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {paginatedTools.length > 0 ? (
                                    paginatedTools.map((tool) => (
                                        <TableRow key={tool.id}>
                                            <TableCell className="font-medium">{tool.tool_number}</TableCell>
                                            <TableCell>{tool.serial_number}</TableCell>
                                            <TableCell className="max-w-[200px] truncate" title={tool.description}>
                                                {tool.description || 'N/A'}
                                            </TableCell>
                                            <TableCell className="hidden md:table-cell">{tool.category || 'General'}</TableCell>
                                            <TableCell className="hidden md:table-cell">
                                                {tool.warehouse_id ? (
                                                    tool.location || 'N/A'
                                                ) : tool.box_number ? (
                                                    <Badge variant="outline">{tool.box_number}</Badge>
                                                ) : (
                                                    'N/A'
                                                )}
                                            </TableCell>
                                            <TableCell className="hidden lg:table-cell">
                                                {tool.warehouse_id ? (
                                                    <Badge variant="secondary" className="bg-blue-100 text-blue-800 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-100">
                                                        {warehouses.find(w => w.id === tool.warehouse_id)?.name || `Warehouse ${tool.warehouse_id}`}
                                                    </Badge>
                                                ) : tool.kit_name ? (
                                                    <Badge variant="secondary">{tool.kit_name}</Badge>
                                                ) : (
                                                    <Badge variant="outline" className="text-muted-foreground">Unknown</Badge>
                                                )}
                                            </TableCell>
                                            <TableCell>
                                                <Badge
                                                    variant={
                                                        tool.status === 'available' ? 'success' :
                                                            tool.status === 'checked_out' ? 'default' :
                                                                tool.status === 'maintenance' ? 'warning' :
                                                                    'secondary'
                                                    }
                                                    className="gap-1"
                                                >
                                                    {tool.status === 'available' && <CheckCircle className="h-3 w-3" />}
                                                    {tool.status === 'checked_out' && <User className="h-3 w-3" />}
                                                    {tool.status === 'maintenance' && <Wrench className="h-3 w-3" />}
                                                    {tool.status === 'retired' && <Archive className="h-3 w-3" />}
                                                    <span className="capitalize">{tool.status.replace('_', ' ')}</span>
                                                </Badge>
                                            </TableCell>
                                            <TableCell className="hidden xl:table-cell">
                                                <CalibrationStatusIndicator tool={tool} />
                                            </TableCell>
                                            <TableCell className="text-right">
                                                <div className="flex justify-end gap-1">
                                                    <TooltipProvider>
                                                        <Tooltip>
                                                            <TooltipTrigger asChild>
                                                                <Button variant="ghost" size="icon" asChild className="h-8 w-8">
                                                                    <Link to={`/tools/${tool.id}`}>
                                                                        <Eye className="h-4 w-4" />
                                                                        <span className="sr-only">View</span>
                                                                    </Link>
                                                                </Button>
                                                            </TooltipTrigger>
                                                            <TooltipContent>View Details</TooltipContent>
                                                        </Tooltip>

                                                        {/* Context-aware action buttons */}
                                                        {tool.status === 'available' && (
                                                            <Tooltip>
                                                                <TooltipTrigger asChild>
                                                                    <Button
                                                                        variant="ghost"
                                                                        size="icon"
                                                                        className="h-8 w-8 text-green-600 hover:text-green-700 hover:bg-green-50 dark:hover:bg-green-900/20"
                                                                        onClick={() => handleCheckoutClick(tool)}
                                                                    >
                                                                        <CheckCircle className="h-4 w-4" />
                                                                        <span className="sr-only">Checkout</span>
                                                                    </Button>
                                                                </TooltipTrigger>
                                                                <TooltipContent>Checkout Tool</TooltipContent>
                                                            </Tooltip>
                                                        )}

                                                        {tool.status === 'checked_out' && (
                                                            <Tooltip>
                                                                <TooltipTrigger asChild>
                                                                    <Button
                                                                        variant="ghost"
                                                                        size="icon"
                                                                        className="h-8 w-8 text-blue-600 hover:text-blue-700 hover:bg-blue-50 dark:hover:bg-blue-900/20"
                                                                        onClick={() => handleReturnClick(tool)}
                                                                    >
                                                                        <RotateCcw className="h-4 w-4" />
                                                                        <span className="sr-only">Return</span>
                                                                    </Button>
                                                                </TooltipTrigger>
                                                                <TooltipContent>Return Tool</TooltipContent>
                                                            </Tooltip>
                                                        )}

                                                        {tool.status === 'maintenance' && isAdmin && (
                                                            <Tooltip>
                                                                <TooltipTrigger asChild>
                                                                    <Button
                                                                        variant="ghost"
                                                                        size="icon"
                                                                        className="h-8 w-8 text-green-600 hover:text-green-700 hover:bg-green-50 dark:hover:bg-green-900/20"
                                                                        onClick={() => handleServiceClick(tool)}
                                                                    >
                                                                        <RotateCcw className="h-4 w-4" />
                                                                        <span className="sr-only">Return to Service</span>
                                                                    </Button>
                                                                </TooltipTrigger>
                                                                <TooltipContent>Return to Service</TooltipContent>
                                                            </Tooltip>
                                                        )}

                                                        <Tooltip>
                                                            <TooltipTrigger asChild>
                                                                <Button
                                                                    variant="ghost"
                                                                    size="icon"
                                                                    className="h-8 w-8 text-orange-600 hover:text-orange-700 hover:bg-orange-50 dark:hover:bg-orange-900/20"
                                                                    onClick={() => handleTransferClick(tool)}
                                                                >
                                                                    <ArrowLeftRight className="h-4 w-4" />
                                                                    <span className="sr-only">Transfer</span>
                                                                </Button>
                                                            </TooltipTrigger>
                                                            <TooltipContent>Transfer</TooltipContent>
                                                        </Tooltip>

                                                        <Tooltip>
                                                            <TooltipTrigger asChild>
                                                                <Button
                                                                    variant="ghost"
                                                                    size="icon"
                                                                    className="h-8 w-8"
                                                                    onClick={() => handleBarcodeClick(tool)}
                                                                >
                                                                    <ScanLine className="h-4 w-4" />
                                                                    <span className="sr-only">Barcode</span>
                                                                </Button>
                                                            </TooltipTrigger>
                                                            <TooltipContent>Barcode</TooltipContent>
                                                        </Tooltip>

                                                        {isAdmin && (
                                                            <Tooltip>
                                                                <TooltipTrigger asChild>
                                                                    <Button
                                                                        variant="ghost"
                                                                        size="icon"
                                                                        className="h-8 w-8 text-destructive hover:text-destructive hover:bg-destructive/10"
                                                                        onClick={() => handleDeleteClick(tool)}
                                                                    >
                                                                        <Trash2 className="h-4 w-4" />
                                                                        <span className="sr-only">Delete</span>
                                                                    </Button>
                                                                </TooltipTrigger>
                                                                <TooltipContent>Delete</TooltipContent>
                                                            </Tooltip>
                                                        )}
                                                    </TooltipProvider>
                                                </div>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow>
                                        <TableCell colSpan={9} className="h-24 text-center">
                                            No tools found.
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </div>

                    {totalPages > 1 && (
                        <div className="py-4 border-t">
                            <Pagination>
                                <PaginationContent>
                                    <PaginationItem>
                                        <PaginationPrevious
                                            onClick={() => handlePageChange(Math.max(1, currentPage - 1))}
                                            className={currentPage === 1 ? "pointer-events-none opacity-50" : "cursor-pointer"}
                                        />
                                    </PaginationItem>

                                    {/* Simplified pagination logic for brevity */}
                                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                                        // Logic to show window around current page could be added here
                                        // For now showing first 5 or window around current
                                        let p = i + 1;
                                        if (totalPages > 5) {
                                            if (currentPage > 3) {
                                                p = currentPage - 2 + i;
                                            }
                                            if (p > totalPages) p = totalPages - (4 - i);
                                        }

                                        return (
                                            <PaginationItem key={p}>
                                                <PaginationLink
                                                    isActive={currentPage === p}
                                                    onClick={() => handlePageChange(p)}
                                                    className="cursor-pointer"
                                                >
                                                    {p}
                                                </PaginationLink>
                                            </PaginationItem>
                                        );
                                    })}

                                    <PaginationItem>
                                        <PaginationNext
                                            onClick={() => handlePageChange(Math.min(totalPages, currentPage + 1))}
                                            className={currentPage === totalPages ? "pointer-events-none opacity-50" : "cursor-pointer"}
                                        />
                                    </PaginationItem>
                                </PaginationContent>
                            </Pagination>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Modals - Keeping legacy modals for now as they are complex to migrate all at once */}
            {selectedTool && (
                <>
                    <CheckoutModal
                        show={showCheckoutModal}
                        onHide={() => setShowCheckoutModal(false)}
                        tool={selectedTool}
                    />
                    <ReturnToolModal
                        show={showReturnModal}
                        onHide={() => {
                            setShowReturnModal(false);
                            dispatch(fetchTools());
                        }}
                        checkoutId={selectedTool.current_checkout_id}
                        toolInfo={selectedTool}
                    />
                    <ReturnToServiceModal
                        show={showServiceModal}
                        onHide={() => {
                            setShowServiceModal(false);
                            dispatch(fetchTools());
                        }}
                        tool={selectedTool}
                    />
                    <ToolBarcode
                        show={showBarcodeModal}
                        onHide={() => setShowBarcodeModal(false)}
                        tool={selectedTool}
                    />
                    <ItemTransferModal
                        show={showTransferModal}
                        onHide={() => setShowTransferModal(false)}
                        item={selectedTool}
                        itemType="tool"
                        onTransferComplete={() => dispatch(fetchTools())}
                    />
                    <DeleteToolModal
                        show={showDeleteModal}
                        onHide={() => setShowDeleteModal(false)}
                        tool={selectedTool}
                        onDelete={handleToolDelete}
                        onRetire={handleToolRetire}
                    />
                </>
            )}
        </div>
    );
};

export default ToolListNew;
