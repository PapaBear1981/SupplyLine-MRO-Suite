import { useState } from 'react';
import { Search, History, Package, AlertCircle, Loader2, RefreshCw, ChevronLeft, ChevronRight, Building, Box } from 'lucide-react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';
import { Badge } from '../components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';

const ItemHistoryPageNew = () => {
  const [searchForm, setSearchForm] = useState({
    identifier: '',
    tracking_number: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [historyData, setHistoryData] = useState(null);
  const [searched, setSearched] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const eventsPerPage = 5;

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSearchForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!searchForm.identifier.trim() || !searchForm.tracking_number.trim()) {
      setError('Both Part/Tool Number and Lot/Serial Number are required');
      return;
    }

    setLoading(true);
    setError(null);
    setHistoryData(null);
    setSearched(true);
    setCurrentPage(1); // Reset to first page on new search

    try {
      const response = await axios.post('/api/history/lookup', {
        identifier: searchForm.identifier.trim(),
        tracking_number: searchForm.tracking_number.trim()
      });

      setHistoryData(response.data);
    } catch (err) {
      if (err.response?.status === 404) {
        setError(`No item found with the provided identifiers`);
      } else {
        setError(err.response?.data?.error || 'Failed to fetch item history');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSearchForm({ identifier: '', tracking_number: '' });
    setHistoryData(null);
    setError(null);
    setSearched(false);
    setCurrentPage(1);
  };

  const handleLotClick = async (partNumber, lotNumber) => {
    // Update search form and trigger search for the clicked lot
    setSearchForm({
      identifier: partNumber,
      tracking_number: lotNumber
    });

    setLoading(true);
    setError(null);
    setHistoryData(null);
    setSearched(true);
    setCurrentPage(1); // Reset to first page

    try {
      const response = await axios.post('/api/history/lookup', {
        identifier: partNumber,
        tracking_number: lotNumber
      });

      setHistoryData(response.data);
      // Scroll to top to show the new results
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      if (err.response?.status === 404) {
        setError(`No item found with the provided identifiers`);
      } else {
        setError(err.response?.data?.error || 'Failed to fetch item history');
      }
    } finally {
      setLoading(false);
    }
  };

  const getItemTypeLabel = (itemType) => {
    switch (itemType) {
      case 'tool':
        return 'Tool';
      case 'chemical':
        return 'Chemical';
      case 'expendable':
        return 'Expendable';
      default:
        return 'Item';
    }
  };

  const getEventVariant = (eventType) => {
    if (eventType.includes('transfer')) return 'default';
    if (eventType === 'issuance' || eventType === 'kit_issuance') return 'success';
    if (eventType === 'checkout') return 'info';
    if (eventType === 'return') return 'success';
    if (eventType === 'retirement') return 'destructive';
    if (eventType === 'creation') return 'secondary';
    if (eventType === 'status_change') return 'warning';
    return 'secondary';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Pagination logic
  const getPaginatedEvents = () => {
    if (!historyData || !historyData.history) return [];
    const startIndex = (currentPage - 1) * eventsPerPage;
    const endIndex = startIndex + eventsPerPage;
    return historyData.history.slice(startIndex, endIndex);
  };

  const getTotalPages = () => {
    if (!historyData || !historyData.history) return 0;
    return Math.ceil(historyData.history.length / eventsPerPage);
  };

  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
    // Scroll to top of page
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const getStatusVariant = (status) => {
    if (!status) return 'secondary';
    const statusLower = status.toLowerCase();
    if (statusLower === 'available') return 'success';
    if (statusLower === 'issued') return 'default';
    if (statusLower === 'retired' || statusLower === 'expired') return 'destructive';
    if (statusLower === 'in_use' || statusLower === 'checked_out') return 'warning';
    return 'secondary';
  };

  const renderPaginationItems = () => {
    const totalPages = getTotalPages();
    const items = [];

    for (let pageNum = 1; pageNum <= totalPages; pageNum++) {
      // Show first page, last page, current page, and pages around current
      if (
        pageNum === 1 ||
        pageNum === totalPages ||
        (pageNum >= currentPage - 1 && pageNum <= currentPage + 1)
      ) {
        items.push(
          <Button
            key={pageNum}
            variant={pageNum === currentPage ? 'default' : 'outline'}
            size="sm"
            onClick={() => handlePageChange(pageNum)}
          >
            {pageNum}
          </Button>
        );
      } else if (
        pageNum === currentPage - 2 ||
        pageNum === currentPage + 2
      ) {
        items.push(
          <span key={pageNum} className="px-2 text-muted-foreground">...</span>
        );
      }
    }

    return items;
  };

  return (
    <div className="w-full space-y-6">
      <div className="flex flex-wrap justify-between items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Item History Lookup</h1>
          <p className="text-muted-foreground mt-2">
            Search for complete history of any chemical, expendable, or tool item
          </p>
        </div>
      </div>

      {/* Search Form */}
      <Card>
        <CardContent className="pt-6">
          <form onSubmit={handleSearch}>
            <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
              <div className="md:col-span-5">
                <div className="space-y-2">
                  <Label htmlFor="identifier" className="font-semibold">
                    Part Number / Tool Number
                  </Label>
                  <Input
                    id="identifier"
                    type="text"
                    name="identifier"
                    value={searchForm.identifier}
                    onChange={handleInputChange}
                    placeholder="e.g., T-12345 or CHEM-001"
                    disabled={loading}
                  />
                  <p className="text-sm text-muted-foreground">
                    Enter the part number for chemicals/expendables or tool number for tools
                  </p>
                </div>
              </div>
              <div className="md:col-span-5">
                <div className="space-y-2">
                  <Label htmlFor="tracking_number" className="font-semibold">
                    Lot Number / Serial Number
                  </Label>
                  <Input
                    id="tracking_number"
                    type="text"
                    name="tracking_number"
                    value={searchForm.tracking_number}
                    onChange={handleInputChange}
                    placeholder="e.g., LOT-251014-0001 or SN-001"
                    disabled={loading}
                  />
                  <p className="text-sm text-muted-foreground">
                    Enter the lot number or serial number (items have one or the other, never both)
                  </p>
                </div>
              </div>
              <div className="md:col-span-2 flex items-end">
                <div className="w-full space-y-2">
                  <Button
                    type="submit"
                    className="w-full"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Searching...
                      </>
                    ) : (
                      <>
                        <Search className="mr-2 h-4 w-4" />
                        Search
                      </>
                    )}
                  </Button>
                  {searched && (
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={handleReset}
                      disabled={loading}
                    >
                      <RefreshCw className="mr-2 h-4 w-4" />
                      Reset
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Error Message */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* No Results Message */}
      {searched && !loading && !historyData && !error && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>No Results</AlertTitle>
          <AlertDescription>
            No item found with the provided identifiers. Please check your input and try again.
          </AlertDescription>
        </Alert>
      )}

      {/* Results */}
      {historyData && historyData.item_found && (
        <div className="space-y-6">
          {/* Item Details Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Package className="h-5 w-5" />
                {getItemTypeLabel(historyData.item_type)} Details
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <div className="text-sm font-medium text-muted-foreground mb-1">Identifier</div>
                    <div className="text-foreground">{historyData.item_details.part_number || historyData.item_details.tool_number}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-muted-foreground mb-1">Tracking Number</div>
                    <div>
                      <Button
                        variant="link"
                        size="sm"
                        className="p-0 h-auto"
                        onClick={() => handleLotClick(
                          historyData.item_details.part_number || historyData.item_details.tool_number,
                          historyData.item_details.serial_number || historyData.item_details.lot_number
                        )}
                        title="Click to refresh history for this item"
                      >
                        <Badge variant="success" className="gap-1">
                          {historyData.item_details.serial_number || historyData.item_details.lot_number}
                          <Search className="h-3 w-3" />
                        </Badge>
                      </Button>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-muted-foreground mb-1">Description</div>
                    <div className="text-foreground">{historyData.item_details.description || 'N/A'}</div>
                  </div>
                  {historyData.item_details.category && (
                    <div>
                      <div className="text-sm font-medium text-muted-foreground mb-1">Category</div>
                      <div className="text-foreground">{historyData.item_details.category}</div>
                    </div>
                  )}
                </div>
                <div className="space-y-4">
                  <div>
                    <div className="text-sm font-medium text-muted-foreground mb-1">Status</div>
                    <div>
                      <Badge variant={getStatusVariant(historyData.item_details.status)}>
                        {historyData.item_details.status}
                      </Badge>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-muted-foreground mb-1">Current Location</div>
                    <div className="flex items-center gap-1 text-foreground">
                      {historyData.current_location.type === 'warehouse' && <Building className="h-4 w-4" />}
                      {historyData.current_location.type === 'kit' && <Box className="h-4 w-4" />}
                      {historyData.current_location.name}
                      {historyData.current_location.details && ` - ${historyData.current_location.details}`}
                    </div>
                  </div>
                  {historyData.item_details.quantity !== undefined && (
                    <div>
                      <div className="text-sm font-medium text-muted-foreground mb-1">Quantity</div>
                      <div className="text-foreground">{historyData.item_details.quantity} {historyData.item_details.unit || ''}</div>
                    </div>
                  )}
                </div>
              </div>

              {/* Parent/Child Lot Information */}
              {(historyData.parent_lot || (historyData.child_lots && historyData.child_lots.length > 0)) && (
                <div className="border-t pt-6 mt-6">
                  <h6 className="text-sm font-semibold text-muted-foreground mb-3">Lot Lineage</h6>
                  {historyData.parent_lot && (
                    <Alert className="mb-2">
                      <AlertTitle className="text-sm">Parent Lot</AlertTitle>
                      <AlertDescription className="flex items-center gap-2">
                        <Button
                          variant="link"
                          size="sm"
                          className="p-0 h-auto"
                          onClick={() => handleLotClick(historyData.parent_lot.part_number, historyData.parent_lot.lot_number)}
                          title="Click to view history of this parent lot"
                        >
                          <Badge variant="warning" className="gap-1">
                            {historyData.parent_lot.lot_number}
                            <Search className="h-3 w-3" />
                          </Badge>
                        </Button>
                        <span>{historyData.parent_lot.description}</span>
                      </AlertDescription>
                    </Alert>
                  )}
                  {historyData.child_lots && historyData.child_lots.length > 0 && (
                    <Alert variant="secondary">
                      <AlertTitle className="text-sm">Child Lots ({historyData.child_lots.length})</AlertTitle>
                      <AlertDescription>
                        <ul className="mt-2 space-y-2">
                          {historyData.child_lots.map((child, idx) => (
                            <li key={idx} className="flex items-center gap-2">
                              <Button
                                variant="link"
                                size="sm"
                                className="p-0 h-auto"
                                onClick={() => handleLotClick(child.part_number, child.lot_number)}
                                title="Click to view history of this child lot"
                              >
                                <Badge variant="info" className="gap-1">
                                  {child.lot_number}
                                  <Search className="h-3 w-3" />
                                </Badge>
                              </Button>
                              <span className="text-sm">
                                {child.description} ({child.quantity} - {child.status})
                              </span>
                            </li>
                          ))}
                        </ul>
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* History Timeline */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <History className="h-5 w-5" />
                Complete History ({historyData.history.length} events)
              </CardTitle>
            </CardHeader>
            <CardContent>
              {historyData.history.length === 0 ? (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>No history events found for this item.</AlertDescription>
                </Alert>
              ) : (
                <>
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="w-[15%]">Event Type</TableHead>
                          <TableHead className="w-[18%]">Date & Time</TableHead>
                          <TableHead className="w-[35%]">Description</TableHead>
                          <TableHead className="w-[12%]">User</TableHead>
                          <TableHead className="w-[20%]">Details</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {getPaginatedEvents().map((event, index) => (
                          <TableRow key={index}>
                            <TableCell>
                              <Badge variant={getEventVariant(event.event_type)}>
                                {event.event_type.replace(/_/g, ' ').toUpperCase()}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <span className="text-sm text-muted-foreground">{formatDate(event.timestamp)}</span>
                            </TableCell>
                            <TableCell className="text-foreground">{event.description}</TableCell>
                            <TableCell>
                              <span className="text-sm text-muted-foreground">{event.user}</span>
                            </TableCell>
                            <TableCell>
                              {event.details && Object.keys(event.details).length > 0 && (
                                <div className="space-y-1">
                                  {Object.entries(event.details).map(([key, value]) => (
                                    value && key !== 'child_lot_status' && (
                                      <div key={key}>
                                        <span className="text-xs">
                                          <span className="font-medium text-muted-foreground">{key.replace(/_/g, ' ')}:</span>{' '}
                                          {key === 'child_lot_number' ? (
                                            <span className="inline-flex items-center gap-1">
                                              <Button
                                                variant="link"
                                                size="sm"
                                                className="p-0 h-auto"
                                                onClick={() => handleLotClick(historyData.item_details.part_number, value)}
                                                title="Click to view history of this child lot"
                                              >
                                                <Badge variant="info" className="gap-1">
                                                  {value}
                                                  <Search className="h-3 w-3" />
                                                </Badge>
                                              </Button>
                                              {event.details.child_lot_status && (
                                                <Badge variant={getStatusVariant(event.details.child_lot_status)}>
                                                  {event.details.child_lot_status}
                                                </Badge>
                                              )}
                                            </span>
                                          ) : (
                                            typeof value === 'object' ? JSON.stringify(value) : value
                                          )}
                                        </span>
                                      </div>
                                    )
                                  ))}
                                </div>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>

                  {/* Pagination Controls */}
                  {getTotalPages() > 1 && (
                    <div className="flex flex-col sm:flex-row justify-between items-center gap-4 border-t pt-4 mt-4">
                      <div className="text-sm text-muted-foreground">
                        Showing {((currentPage - 1) * eventsPerPage) + 1} - {Math.min(currentPage * eventsPerPage, historyData.history.length)} of {historyData.history.length} events
                      </div>
                      <div className="flex items-center gap-1">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handlePageChange(currentPage - 1)}
                          disabled={currentPage === 1}
                        >
                          <ChevronLeft className="h-4 w-4" />
                        </Button>

                        {renderPaginationItems()}

                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handlePageChange(currentPage + 1)}
                          disabled={currentPage === getTotalPages()}
                        >
                          <ChevronRight className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default ItemHistoryPageNew;
