import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { ArrowLeft, Edit, Package, ScanBarcode, Trash2 } from 'lucide-react';
import {
  fetchChemicalById,
  fetchChemicalIssuances,
  fetchChemicalReturns,
  archiveChemical,
} from '../store/chemicalsSlice';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ChemicalIssuanceHistory from '../components/chemicals/ChemicalIssuanceHistory';
import ChemicalReturnHistory from '../components/chemicals/ChemicalReturnHistory';
import ChemicalBarcode from '../components/chemicals/ChemicalBarcode';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Textarea } from '../components/ui/textarea';

const ChemicalDetailPageNew = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const {
    currentChemical,
    loading,
    error,
    issuances,
    issuanceLoading,
    returns,
    returnsLoading,
  } = useSelector((state) => state.chemicals);
  const { user } = useSelector((state) => state.auth);
  const isAuthorized = user?.is_admin || user?.department === 'Materials';

  // State for modals
  const [showArchiveModal, setShowArchiveModal] = useState(false);
  const [showBarcodeModal, setShowBarcodeModal] = useState(false);
  const [archiveReason, setArchiveReason] = useState('');
  const [archiveCustomReason, setArchiveCustomReason] = useState('');

  useEffect(() => {
    if (id) {
      dispatch(fetchChemicalById(id));
      dispatch(fetchChemicalIssuances(id));
      dispatch(fetchChemicalReturns(id));
    }
  }, [dispatch, id]);

  if (loading && !currentChemical) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>{error.message}</AlertDescription>
      </Alert>
    );
  }

  if (!currentChemical) {
    return (
      <Alert variant="warning">
        <AlertDescription>Chemical not found</AlertDescription>
      </Alert>
    );
  }

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

  // Handle archive button click
  const handleArchiveClick = () => {
    setArchiveReason('');
    setArchiveCustomReason('');
    setShowArchiveModal(true);
  };

  // Handle archive confirmation
  const handleArchiveConfirm = () => {
    let reason = archiveReason;

    // If "other" is selected, use the custom reason
    if (archiveReason === 'other' && archiveCustomReason.trim()) {
      reason = archiveCustomReason.trim();
    }

    if (!reason) {
      return; // Don't proceed if no reason is provided
    }

    dispatch(archiveChemical({ id, reason }))
      .unwrap()
      .then(() => {
        setShowArchiveModal(false);
        navigate('/chemicals');
      })
      .catch((err) => {
        console.error('Failed to archive chemical:', err);
      });
  };

  return (
    <div className="w-full space-y-6">
      <div className="flex flex-wrap justify-between items-center gap-4">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Chemical Details</h1>
        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" onClick={() => navigate('/chemicals')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to List
          </Button>
          {isAuthorized && !(currentChemical.is_archived === true) && (
            <>
              <Button
                variant="default"
                onClick={() => navigate(`/chemicals/${id}/edit`)}
              >
                <Edit className="mr-2 h-4 w-4" />
                Edit
              </Button>
              <Button
                variant="success"
                onClick={() => navigate(`/chemicals/${id}/issue`)}
                disabled={currentChemical.status === 'out_of_stock' || currentChemical.status === 'expired'}
              >
                <Package className="mr-2 h-4 w-4" />
                Issue Chemical
              </Button>
              <Button
                variant="info"
                onClick={() => setShowBarcodeModal(true)}
              >
                <ScanBarcode className="mr-2 h-4 w-4" />
                Barcode
              </Button>
              <Button
                variant="destructive"
                onClick={handleArchiveClick}
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Archive
              </Button>
            </>
          )}
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="text-xl">
              {currentChemical.part_number} - {currentChemical.lot_number}
            </CardTitle>
            <Badge variant={getStatusBadgeVariant(currentChemical.status)} className="text-base">
              {formatStatus(currentChemical.status)}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h5 className="text-lg font-semibold text-foreground">Basic Information</h5>
              <hr className="border-border" />
              <div className="space-y-2">
                <p className="text-foreground">
                  <span className="font-semibold">Part Number:</span> {currentChemical.part_number}
                </p>
                <p className="text-foreground">
                  <span className="font-semibold">Lot Number:</span> {currentChemical.lot_number}
                </p>
                <p className="text-foreground">
                  <span className="font-semibold">Description:</span> {currentChemical.description || 'N/A'}
                </p>
                <p className="text-foreground">
                  <span className="font-semibold">Manufacturer:</span> {currentChemical.manufacturer || 'N/A'}
                </p>
                <p className="text-foreground">
                  <span className="font-semibold">Category:</span> {currentChemical.category}
                </p>
              </div>
            </div>
            <div className="space-y-4">
              <h5 className="text-lg font-semibold text-foreground">Inventory Information</h5>
              <hr className="border-border" />
              <div className="space-y-2">
                <p className="text-foreground">
                  <span className="font-semibold">Quantity:</span> {currentChemical.quantity} {currentChemical.unit}
                </p>
                <p className="text-foreground">
                  <span className="font-semibold">Location:</span> {currentChemical.location || 'N/A'}
                </p>
                <p className="text-foreground">
                  <span className="font-semibold">Date Added:</span>{' '}
                  {new Date(currentChemical.date_added).toLocaleDateString()}
                </p>
                <p className="text-foreground">
                  <span className="font-semibold">Expiration Date:</span>{' '}
                  {currentChemical.expiration_date
                    ? new Date(currentChemical.expiration_date).toLocaleDateString()
                    : 'N/A'}
                </p>
                <p className="text-foreground">
                  <span className="font-semibold">Minimum Stock Level:</span>{' '}
                  {currentChemical.minimum_stock_level
                    ? `${currentChemical.minimum_stock_level} ${currentChemical.unit}`
                    : 'Not set'}
                </p>
              </div>
            </div>
          </div>

          {currentChemical.notes && (
            <>
              <h5 className="text-lg font-semibold text-foreground mt-6">Notes</h5>
              <hr className="border-border" />
              <p className="text-foreground mt-2">{currentChemical.notes}</p>
            </>
          )}
        </CardContent>
      </Card>

      <Tabs defaultValue="issuances" className="w-full">
        <TabsList>
          <TabsTrigger value="issuances">Issuance History</TabsTrigger>
          <TabsTrigger value="returns">Return History</TabsTrigger>
        </TabsList>
        <TabsContent value="issuances" className="mt-4">
          <ChemicalIssuanceHistory
            issuances={issuances[id] || []}
            loading={issuanceLoading}
          />
        </TabsContent>
        <TabsContent value="returns" className="mt-4">
          <ChemicalReturnHistory
            returns={returns[id] || []}
            loading={returnsLoading}
          />
        </TabsContent>
      </Tabs>

      {/* Archive Modal */}
      <Dialog open={showArchiveModal} onOpenChange={setShowArchiveModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Archive Chemical</DialogTitle>
            <DialogDescription>
              Archiving this chemical will remove it from the active inventory.
              This action is reversible, but the chemical will be moved to the archive.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="archive-reason">Reason for Archiving</Label>
              <Select value={archiveReason} onValueChange={setArchiveReason}>
                <SelectTrigger id="archive-reason">
                  <SelectValue placeholder="Select a reason" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="expired">Expired</SelectItem>
                  <SelectItem value="depleted">Depleted (Used Up)</SelectItem>
                  <SelectItem value="damaged">Damaged</SelectItem>
                  <SelectItem value="recalled">Recalled by Manufacturer</SelectItem>
                  <SelectItem value="other">Other (Specify)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {archiveReason === 'other' && (
              <div className="space-y-2">
                <Label htmlFor="custom-reason">Specify Reason</Label>
                <Textarea
                  id="custom-reason"
                  rows={2}
                  value={archiveCustomReason}
                  onChange={(e) => setArchiveCustomReason(e.target.value)}
                  placeholder="Enter specific reason for archiving"
                />
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="secondary" onClick={() => setShowArchiveModal(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleArchiveConfirm}
              disabled={!archiveReason || (archiveReason === 'other' && !archiveCustomReason.trim())}
            >
              Archive Chemical
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Barcode Modal */}
      {showBarcodeModal && (
        <ChemicalBarcode
          show={showBarcodeModal}
          onHide={() => setShowBarcodeModal(false)}
          chemical={currentChemical}
        />
      )}
    </div>
  );
};

export default ChemicalDetailPageNew;
