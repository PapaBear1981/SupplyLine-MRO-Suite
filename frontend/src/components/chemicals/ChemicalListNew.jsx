import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
    Search,
    Filter,
    X,
    ArrowUpDown,
    Eye,
    FlaskConical,
    ArrowLeftRight,
    ScanLine,
    ShoppingCart,
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
import { Label } from '../ui/label';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui/tooltip';

// Custom Components
import LoadingSpinner from '../common/LoadingSpinner';
import ChemicalBarcode from './ChemicalBarcode';
import ItemTransferModal from '../common/ItemTransferModal';
import ChemicalReorderModal from './ChemicalReorderModal';

const ChemicalListNew = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const { chemicals, loading } = useSelector((state) => state.chemicals);

    const [searchTerm, setSearchTerm] = useState('');
    const [filteredChemicals, setFilteredChemicals] = useState([]);
    const [sortConfig, setSortConfig] = useState({ key: 'part_number', direction: 'ascending' });

    // Modal States
    const [showBarcodeModal, setShowBarcodeModal] = useState(false);
    const [showTransferModal, setShowTransferModal] = useState(false);
    const [showReorderModal, setShowReorderModal] = useState(false);
    const [selectedChemical, setSelectedChemical] = useState(null);

    // Filter states
    const [showFilters, setShowFilters] = useState(false);
    const [categoryFilter, setCategoryFilter] = useState('all');
    const [statusFilter, setStatusFilter] = useState('available,low_stock');
    const [warehouseFilter, setWarehouseFilter] = useState('all');

    // Pagination states
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage] = useState(30);

    // Data for filters
    const [availableCategories, setAvailableCategories] = useState([]);
    const [warehouses, setWarehouses] = useState([]);

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

    useEffect(() => {
        if (chemicals && chemicals.length > 0) {
            const categories = [...new Set(chemicals.map(chem => chem.category).filter(Boolean))];
            setAvailableCategories(categories.sort());
        }
    }, [chemicals]);

    useEffect(() => {
        if (!chemicals) return;

        let chemicalsToDisplay = [...chemicals];

        // Apply search query
        if (searchTerm.trim()) {
            const query = searchTerm.toLowerCase();
            chemicalsToDisplay = chemicalsToDisplay.filter(chem =>
                chem.part_number.toLowerCase().includes(query) ||
                chem.lot_number.toLowerCase().includes(query) ||
                (chem.description && chem.description.toLowerCase().includes(query)) ||
                (chem.manufacturer && chem.manufacturer.toLowerCase().includes(query))
            );
        }

        // Apply category filter
        if (categoryFilter && categoryFilter !== 'all') {
            chemicalsToDisplay = chemicalsToDisplay.filter(chem => chem.category === categoryFilter);
        }

        // Apply status filter (supports multiple statuses separated by comma)
        if (statusFilter && statusFilter !== 'all') {
            const allowedStatuses = statusFilter.split(',').map(s => s.trim());
            chemicalsToDisplay = chemicalsToDisplay.filter(chem => allowedStatuses.includes(chem.status));
        }

        // Apply warehouse filter
        if (warehouseFilter && warehouseFilter !== 'all') {
            if (warehouseFilter === 'in_kit') {
                chemicalsToDisplay = chemicalsToDisplay.filter(chem => chem.warehouse_id === null && chem.kit_id !== null);
            } else {
                chemicalsToDisplay = chemicalsToDisplay.filter(chem => chem.warehouse_id === parseInt(warehouseFilter));
            }
        }

        // Sort chemicals
        const sortedChemicals = [...chemicalsToDisplay].sort((a, b) => {
            let aValue = a[sortConfig.key];
            let bValue = b[sortConfig.key];

            // Handle special cases for sorting
            if (sortConfig.key === 'quantity') {
                aValue = parseFloat(aValue) || 0;
                bValue = parseFloat(bValue) || 0;
            } else if (sortConfig.key === 'expiration_date') {
                if (!aValue || aValue === 'N/A') return 1;
                if (!bValue || bValue === 'N/A') return -1;
                aValue = new Date(aValue).getTime();
                bValue = new Date(bValue).getTime();
            } else if (sortConfig.key === 'warehouse_name') {
                aValue = a.warehouse_id
                    ? (warehouses.find(w => w.id === a.warehouse_id)?.name || '')
                    : (a.kit_name || '');
                bValue = b.warehouse_id
                    ? (warehouses.find(w => w.id === b.warehouse_id)?.name || '')
                    : (b.kit_name || '');
            } else {
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

        setFilteredChemicals(sortedChemicals);
        setCurrentPage(1);
    }, [chemicals, searchTerm, sortConfig, categoryFilter, statusFilter, warehouseFilter, warehouses]);

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
    const totalPages = Math.ceil(filteredChemicals.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedChemicals = filteredChemicals.slice(startIndex, endIndex);

    const handlePageChange = (page) => {
        setCurrentPage(page);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    // Modal Handlers
    const handleBarcodeClick = (chemical) => {
        setSelectedChemical(chemical);
        setShowBarcodeModal(true);
    };

    const handleTransferClick = (chemical) => {
        setSelectedChemical(chemical);
        setShowTransferModal(true);
    };

    const handleReorderClick = (chemical) => {
        setSelectedChemical(chemical);
        setShowReorderModal(true);
    };

    const resetFilters = () => {
        setCategoryFilter('all');
        setStatusFilter('available,low_stock');
        setWarehouseFilter('all');
        setSearchTerm('');
    };

    const activeFilterCount = [
        categoryFilter !== 'all',
        statusFilter !== 'available,low_stock',
        warehouseFilter !== 'all',
        searchTerm.trim() !== ''
    ].filter(Boolean).length;

    // Get status badge variant
    const getStatusBadgeVariant = (status) => {
        switch (status) {
            case 'available':
                return 'success';
            case 'low_stock':
                return 'warning';
            case 'out_of_stock':
                return 'destructive';
            case 'expired':
                return 'secondary';
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

    if (loading && !filteredChemicals.length) {
        return <LoadingSpinner />;
    }

    return (
        <div className="space-y-4">
            <Card>
                <CardHeader className="bg-muted/50 pb-3">
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                        <div className="flex flex-col gap-1">
                            <div className="flex items-center gap-2">
                                <CardTitle>Chemical Inventory</CardTitle>
                                <Badge variant="secondary" className="ml-2">
                                    {filteredChemicals.length} {filteredChemicals.length === 1 ? 'item' : 'items'}
                                </Badge>
                            </div>
                        </div>

                        <div className="flex flex-col sm:flex-row gap-2 w-full md:w-auto">
                            <div className="relative w-full sm:w-64">
                                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="Search chemicals..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="pl-8"
                                />
                                {searchTerm && (
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="absolute right-0 top-0 h-9 w-9"
                                        onClick={() => setSearchTerm('')}
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
                                    <Label>Status</Label>
                                    <Select value={statusFilter} onValueChange={setStatusFilter}>
                                        <SelectTrigger>
                                            <SelectValue placeholder="All Statuses" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="available,low_stock">Available & Low Stock</SelectItem>
                                            <SelectItem value="all">All Statuses</SelectItem>
                                            <SelectItem value="available">Available</SelectItem>
                                            <SelectItem value="low_stock">Low Stock</SelectItem>
                                            <SelectItem value="out_of_stock">Out of Stock</SelectItem>
                                            <SelectItem value="expired">Expired</SelectItem>
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
                                    <TableHead className="cursor-pointer" onClick={() => handleSort('part_number')}>
                                        Part Number <ArrowUpDown className="ml-2 h-4 w-4 inline" />
                                    </TableHead>
                                    <TableHead className="cursor-pointer" onClick={() => handleSort('lot_number')}>
                                        Lot Number <ArrowUpDown className="ml-2 h-4 w-4 inline" />
                                    </TableHead>
                                    <TableHead>Description</TableHead>
                                    <TableHead className="hidden md:table-cell cursor-pointer" onClick={() => handleSort('manufacturer')}>
                                        Manufacturer <ArrowUpDown className="ml-2 h-4 w-4 inline" />
                                    </TableHead>
                                    <TableHead className="cursor-pointer" onClick={() => handleSort('quantity')}>
                                        Quantity <ArrowUpDown className="ml-2 h-4 w-4 inline" />
                                    </TableHead>
                                    <TableHead className="hidden md:table-cell">Location</TableHead>
                                    <TableHead className="hidden lg:table-cell cursor-pointer" onClick={() => handleSort('warehouse_name')}>
                                        Warehouse <ArrowUpDown className="ml-2 h-4 w-4 inline" />
                                    </TableHead>
                                    <TableHead className="hidden xl:table-cell cursor-pointer" onClick={() => handleSort('expiration_date')}>
                                        Expiration <ArrowUpDown className="ml-2 h-4 w-4 inline" />
                                    </TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead className="text-right">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {paginatedChemicals.length > 0 ? (
                                    paginatedChemicals.map((chemical) => (
                                        <TableRow key={chemical.id}>
                                            <TableCell className="font-medium">{chemical.part_number}</TableCell>
                                            <TableCell>{chemical.lot_number}</TableCell>
                                            <TableCell className="max-w-[200px] truncate" title={chemical.description}>
                                                {chemical.description || 'N/A'}
                                            </TableCell>
                                            <TableCell className="hidden md:table-cell">{chemical.manufacturer || 'N/A'}</TableCell>
                                            <TableCell>
                                                {chemical.quantity} {chemical.unit}
                                            </TableCell>
                                            <TableCell className="hidden md:table-cell">
                                                {chemical.warehouse_id ? (
                                                    chemical.location || 'N/A'
                                                ) : chemical.box_number ? (
                                                    <Badge variant="outline">{chemical.box_number}</Badge>
                                                ) : (
                                                    'N/A'
                                                )}
                                            </TableCell>
                                            <TableCell className="hidden lg:table-cell">
                                                {chemical.warehouse_id ? (
                                                    <Badge variant="secondary" className="bg-blue-100 text-blue-800 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-100">
                                                        {warehouses.find(w => w.id === chemical.warehouse_id)?.name || `Warehouse ${chemical.warehouse_id}`}
                                                    </Badge>
                                                ) : chemical.kit_name ? (
                                                    <Badge variant="secondary">{chemical.kit_name}</Badge>
                                                ) : (
                                                    <Badge variant="outline" className="text-muted-foreground">Unknown</Badge>
                                                )}
                                            </TableCell>
                                            <TableCell className="hidden xl:table-cell">
                                                {chemical.expiration_date
                                                    ? new Date(chemical.expiration_date).toLocaleDateString()
                                                    : 'N/A'}
                                            </TableCell>
                                            <TableCell>
                                                <Badge variant={getStatusBadgeVariant(chemical.status)}>
                                                    {formatStatus(chemical.status)}
                                                </Badge>
                                            </TableCell>
                                            <TableCell className="text-right">
                                                <div className="flex justify-end gap-1">
                                                    <TooltipProvider>
                                                        <Tooltip>
                                                            <TooltipTrigger asChild>
                                                                <Button
                                                                    variant="ghost"
                                                                    size="icon"
                                                                    className="h-8 w-8"
                                                                    onClick={() => navigate(`/chemicals/${chemical.id}`)}
                                                                >
                                                                    <Eye className="h-4 w-4" />
                                                                    <span className="sr-only">View</span>
                                                                </Button>
                                                            </TooltipTrigger>
                                                            <TooltipContent>View Details</TooltipContent>
                                                        </Tooltip>

                                                        <Tooltip>
                                                            <TooltipTrigger asChild>
                                                                <Button
                                                                    variant="ghost"
                                                                    size="icon"
                                                                    className="h-8 w-8 text-green-600 hover:text-green-700 hover:bg-green-50 dark:hover:bg-green-900/20"
                                                                    onClick={() => navigate(`/chemicals/${chemical.id}/issue`)}
                                                                    disabled={chemical.status === 'out_of_stock' || chemical.status === 'expired'}
                                                                >
                                                                    <FlaskConical className="h-4 w-4" />
                                                                    <span className="sr-only">Issue</span>
                                                                </Button>
                                                            </TooltipTrigger>
                                                            <TooltipContent>
                                                                {chemical.status === 'out_of_stock' || chemical.status === 'expired'
                                                                    ? 'Cannot issue - out of stock or expired'
                                                                    : 'Issue Chemical'}
                                                            </TooltipContent>
                                                        </Tooltip>

                                                        <Tooltip>
                                                            <TooltipTrigger asChild>
                                                                <Button
                                                                    variant="ghost"
                                                                    size="icon"
                                                                    className="h-8 w-8 text-orange-600 hover:text-orange-700 hover:bg-orange-50 dark:hover:bg-orange-900/20"
                                                                    onClick={() => handleTransferClick(chemical)}
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
                                                                    className="h-8 w-8 text-purple-600 hover:text-purple-700 hover:bg-purple-50 dark:hover:bg-purple-900/20"
                                                                    onClick={() => handleReorderClick(chemical)}
                                                                >
                                                                    <ShoppingCart className="h-4 w-4" />
                                                                    <span className="sr-only">Reorder</span>
                                                                </Button>
                                                            </TooltipTrigger>
                                                            <TooltipContent>Reorder Chemical</TooltipContent>
                                                        </Tooltip>

                                                        <Tooltip>
                                                            <TooltipTrigger asChild>
                                                                <Button
                                                                    variant="ghost"
                                                                    size="icon"
                                                                    className="h-8 w-8"
                                                                    onClick={() => handleBarcodeClick(chemical)}
                                                                >
                                                                    <ScanLine className="h-4 w-4" />
                                                                    <span className="sr-only">Barcode</span>
                                                                </Button>
                                                            </TooltipTrigger>
                                                            <TooltipContent>Generate Barcode</TooltipContent>
                                                        </Tooltip>
                                                    </TooltipProvider>
                                                </div>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow>
                                        <TableCell colSpan={10} className="h-24 text-center">
                                            No chemicals found.
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

                                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
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

            {/* Modals */}
            {selectedChemical && (
                <>
                    <ChemicalBarcode
                        show={showBarcodeModal}
                        onHide={() => setShowBarcodeModal(false)}
                        chemical={selectedChemical}
                    />
                    <ItemTransferModal
                        show={showTransferModal}
                        onHide={() => setShowTransferModal(false)}
                        item={selectedChemical}
                        itemType="chemical"
                        onTransferComplete={() => dispatch(fetchChemicals())}
                    />
                    <ChemicalReorderModal
                        show={showReorderModal}
                        onHide={() => setShowReorderModal(false)}
                        chemical={selectedChemical}
                    />
                </>
            )}
        </div>
    );
};

export default ChemicalListNew;
