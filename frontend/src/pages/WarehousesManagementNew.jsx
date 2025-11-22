import { useState, useEffect } from 'react';
import { Warehouse, Plus, Search, MapPin, Box, TestTubes, Edit, X, AlertCircle, Loader2 } from 'lucide-react';
import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import api from '../services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';

const WarehousesManagementNew = () => {
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin;

  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedWarehouse, setSelectedWarehouse] = useState(null);
  const [showDetailsPanel, setShowDetailsPanel] = useState(false);

  // Create/Edit warehouse form
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
    country: 'USA',
    warehouse_type: 'satellite',
    contact_person: '',
    contact_phone: '',
    contact_email: ''
  });
  const [formErrors, setFormErrors] = useState({});
  const [submitError, setSubmitError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchWarehouses();
  }, []);

  const fetchWarehouses = async () => {
    setLoading(true);
    try {
      const response = await api.get('/warehouses');
      const warehousesData = response.data.warehouses || response.data;
      setWarehouses(Array.isArray(warehousesData) ? warehousesData : []);
    } catch (err) {
      console.error('Failed to fetch warehouses:', err);
      setError('Failed to load warehouses. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const validateForm = () => {
    const errors = {};
    if (!formData.name.trim()) {
      errors.name = 'Warehouse name is required';
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleCreateWarehouse = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    setSubmitting(true);
    setSubmitError(null);

    try {
      await api.post('/warehouses', formData);
      setShowCreateModal(false);
      resetForm();
      fetchWarehouses();
    } catch (err) {
      console.error('Failed to create warehouse:', err);
      setSubmitError(err.response?.data?.message || 'Failed to create warehouse');
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      address: '',
      city: '',
      state: '',
      zip_code: '',
      country: 'USA',
      warehouse_type: 'satellite',
      contact_person: '',
      contact_phone: '',
      contact_email: ''
    });
    setFormErrors({});
    setSubmitError(null);
  };

  const handleViewDetails = async (warehouse) => {
    setSelectedWarehouse(warehouse);
    setShowDetailsPanel(true);

    try {
      const response = await api.get(`/warehouses/${warehouse.id}/stats`);
      setSelectedWarehouse(prev => ({ ...prev, stats: response.data }));
    } catch (err) {
      console.error('Failed to fetch warehouse stats:', err);
    }
  };

  const handleEditWarehouse = (warehouse) => {
    setFormData({
      name: warehouse.name || '',
      address: warehouse.address || '',
      city: warehouse.city || '',
      state: warehouse.state || '',
      zip_code: warehouse.zip_code || '',
      country: warehouse.country || 'USA',
      warehouse_type: warehouse.warehouse_type || 'satellite',
      contact_person: warehouse.contact_person || '',
      contact_phone: warehouse.contact_phone || '',
      contact_email: warehouse.contact_email || ''
    });
    setShowEditModal(true);
  };

  const handleUpdateWarehouse = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    setSubmitting(true);
    setSubmitError(null);

    try {
      await api.put(`/warehouses/${selectedWarehouse.id}`, formData);
      setShowEditModal(false);
      resetForm();
      fetchWarehouses();
      setShowDetailsPanel(false);
    } catch (err) {
      console.error('Failed to update warehouse:', err);
      setSubmitError(err.response?.data?.error || 'Failed to update warehouse');
    } finally {
      setSubmitting(false);
    }
  };

  const filteredWarehouses = warehouses.filter(w =>
    w.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    w.city?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    w.state?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!isAdmin) {
    return <Navigate to="/" replace />;
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const WarehouseCard = ({ warehouse }) => (
    <Card
      className="cursor-pointer hover:shadow-lg transition-shadow"
      onClick={() => handleViewDetails(warehouse)}
    >
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Warehouse className="h-5 w-5 text-primary" />
              {warehouse.name}
            </CardTitle>
            <CardDescription className="flex items-center gap-1 mt-1">
              <MapPin className="h-3 w-3" />
              {warehouse.city}, {warehouse.state}
            </CardDescription>
          </div>
          <div className="flex gap-1">
            <Badge variant={warehouse.is_active ? 'success' : 'secondary'}>
              {warehouse.is_active ? 'Active' : 'Inactive'}
            </Badge>
            {warehouse.warehouse_type === 'main' && (
              <Badge variant="default">Main</Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {warehouse.address && (
          <p className="text-sm text-muted-foreground mb-4">{warehouse.address}</p>
        )}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <Box className="h-5 w-5 mx-auto text-blue-500 mb-1" />
            <div className="text-xs text-muted-foreground">Tools</div>
            <div className="font-bold">{warehouse.tools_count || 0}</div>
          </div>
          <div className="text-center">
            <TestTubes className="h-5 w-5 mx-auto text-yellow-500 mb-1" />
            <div className="text-xs text-muted-foreground">Chemicals</div>
            <div className="font-bold">{warehouse.chemicals_count || 0}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="w-full space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Warehouse className="h-8 w-8" />
            Warehouse Management
          </h1>
          <p className="text-muted-foreground mt-1">
            Manage warehouse locations and inventory
          </p>
        </div>
        {isAdmin && (
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Create Warehouse
          </Button>
        )}
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search warehouses by name, city, or state..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-9"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className={showDetailsPanel ? 'lg:col-span-8' : 'lg:col-span-12'}>
          {filteredWarehouses.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Warehouse className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold">No warehouses found</h3>
                <p className="text-muted-foreground mb-4">
                  {searchTerm
                    ? 'Try adjusting your search'
                    : 'Create your first warehouse to get started'}
                </p>
                {!searchTerm && isAdmin && (
                  <Button onClick={() => setShowCreateModal(true)}>
                    <Plus className="mr-2 h-4 w-4" />
                    Create Warehouse
                  </Button>
                )}
              </CardContent>
            </Card>
          ) : (
            <div className={`grid grid-cols-1 ${showDetailsPanel ? 'md:grid-cols-1' : 'md:grid-cols-2 lg:grid-cols-3'} gap-4`}>
              {filteredWarehouses.map(warehouse => (
                <WarehouseCard key={warehouse.id} warehouse={warehouse} />
              ))}
            </div>
          )}
        </div>

        {showDetailsPanel && selectedWarehouse && (
          <div className="lg:col-span-4">
            <Card className="sticky top-4">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <CardTitle className="text-lg">Warehouse Details</CardTitle>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setShowDetailsPanel(false)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-start">
                  <h3 className="font-semibold">{selectedWarehouse.name}</h3>
                  {isAdmin && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEditWarehouse(selectedWarehouse);
                      }}
                    >
                      <Edit className="mr-1 h-3 w-3" />
                      Edit
                    </Button>
                  )}
                </div>
                <p className="text-sm text-muted-foreground">
                  {selectedWarehouse.address}<br />
                  {selectedWarehouse.city}, {selectedWarehouse.state} {selectedWarehouse.zip_code}
                </p>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">Type:</span>
                    <span>{selectedWarehouse.warehouse_type}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">Status:</span>
                    <Badge variant={selectedWarehouse.is_active ? 'success' : 'secondary'}>
                      {selectedWarehouse.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                </div>

                {(selectedWarehouse.contact_person || selectedWarehouse.contact_phone || selectedWarehouse.contact_email) && (
                  <>
                    <hr />
                    <div className="space-y-2">
                      <h4 className="font-semibold text-sm">Contact Information</h4>
                      {selectedWarehouse.contact_person && (
                        <div className="text-sm">
                          <span className="font-medium">Contact:</span> {selectedWarehouse.contact_person}
                        </div>
                      )}
                      {selectedWarehouse.contact_phone && (
                        <div className="text-sm">
                          <span className="font-medium">Phone:</span> {selectedWarehouse.contact_phone}
                        </div>
                      )}
                      {selectedWarehouse.contact_email && (
                        <div className="text-sm">
                          <span className="font-medium">Email:</span> {selectedWarehouse.contact_email}
                        </div>
                      )}
                    </div>
                  </>
                )}

                <hr />

                <div className="space-y-2">
                  <h4 className="font-semibold text-sm">Inventory Summary</h4>
                  <div className="flex items-center gap-2 text-sm">
                    <Box className="h-4 w-4 text-blue-500" />
                    <span className="font-medium">Tools:</span> {selectedWarehouse.tools_count || 0}
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <TestTubes className="h-4 w-4 text-yellow-500" />
                    <span className="font-medium">Chemicals:</span> {selectedWarehouse.chemicals_count || 0}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      {/* Create/Edit Warehouse Modal - Using same form for both */}
      <Dialog
        open={showCreateModal || showEditModal}
        onOpenChange={(open) => {
          if (!open) {
            setShowCreateModal(false);
            setShowEditModal(false);
            resetForm();
          }
        }}
      >
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{showEditModal ? 'Edit Warehouse' : 'Create New Warehouse'}</DialogTitle>
          </DialogHeader>
          <form onSubmit={showEditModal ? handleUpdateWarehouse : handleCreateWarehouse}>
            <div className="space-y-4 py-4">
              {submitError && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{submitError}</AlertDescription>
                </Alert>
              )}

              <div className="grid gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Warehouse Name *</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="e.g., Main Warehouse, Satellite A"
                    className={formErrors.name ? 'border-destructive' : ''}
                  />
                  {formErrors.name && (
                    <p className="text-sm text-destructive">{formErrors.name}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="warehouse_type">Warehouse Type *</Label>
                  <Select
                    value={formData.warehouse_type}
                    onValueChange={(value) => setFormData({ ...formData, warehouse_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="main">Main Warehouse</SelectItem>
                      <SelectItem value="satellite">Satellite Warehouse</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="address">Address</Label>
                  <Input
                    id="address"
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                    placeholder="Street address"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="city">City</Label>
                    <Input
                      id="city"
                      value={formData.city}
                      onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="space-y-2">
                      <Label htmlFor="state">State</Label>
                      <Input
                        id="state"
                        value={formData.state}
                        onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                        maxLength={2}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="zip_code">Zip</Label>
                      <Input
                        id="zip_code"
                        value={formData.zip_code}
                        onChange={(e) => setFormData({ ...formData, zip_code: e.target.value })}
                      />
                    </div>
                  </div>
                </div>

                <hr />
                <h4 className="font-semibold text-sm">Contact Information (Optional)</h4>

                <div className="space-y-2">
                  <Label htmlFor="contact_person">Contact Person</Label>
                  <Input
                    id="contact_person"
                    value={formData.contact_person}
                    onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                    placeholder="Name of primary contact"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="contact_phone">Contact Phone</Label>
                    <Input
                      id="contact_phone"
                      type="tel"
                      value={formData.contact_phone}
                      onChange={(e) => setFormData({ ...formData, contact_phone: e.target.value })}
                      placeholder="(555) 123-4567"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="contact_email">Contact Email</Label>
                    <Input
                      id="contact_email"
                      type="email"
                      value={formData.contact_email}
                      onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                      placeholder="contact@example.com"
                    />
                  </div>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button
                type="button"
                variant="secondary"
                onClick={() => {
                  setShowCreateModal(false);
                  setShowEditModal(false);
                  resetForm();
                }}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={submitting}>
                {submitting ? 'Saving...' : (showEditModal ? 'Save Changes' : 'Create Warehouse')}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default WarehousesManagementNew;
