import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Plane, Edit, Trash2, Plus, Check, X, AlertCircle, Loader2 } from 'lucide-react';
import {
  fetchAircraftTypes,
  createAircraftType,
  updateAircraftType,
  deactivateAircraftType
} from '../../store/kitsSlice';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription, AlertTitle } from '../ui/alert';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../ui/dialog';
import { Switch } from '../ui/switch';

const AircraftTypeManagementNew = () => {
  const dispatch = useDispatch();
  const { aircraftTypes, loading, error } = useSelector((state) => state.kits);
  const { user: currentUser } = useSelector((state) => state.auth);

  // State for modals
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeactivateModal, setShowDeactivateModal] = useState(false);

  // State for form data
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  });

  // State for validation
  const [formErrors, setFormErrors] = useState({});

  // State for selected aircraft type
  const [selectedType, setSelectedType] = useState(null);

  // State for showing inactive types
  const [showInactive, setShowInactive] = useState(false);

  // State for success message
  const [successMessage, setSuccessMessage] = useState('');

  // Fetch aircraft types on component mount
  useEffect(() => {
    dispatch(fetchAircraftTypes(showInactive));
  }, [dispatch, showInactive]);

  // Clear success message after 3 seconds
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(''), 3000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  // Reset form data
  const resetForm = () => {
    setFormData({
      name: '',
      description: ''
    });
    setFormErrors({});
  };

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    // Clear error for this field
    if (formErrors[name]) {
      setFormErrors({
        ...formErrors,
        [name]: null
      });
    }
  };

  // Validate form
  const validateForm = () => {
    const errors = {};
    if (!formData.name.trim()) {
      errors.name = 'Please provide an aircraft type name.';
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle add aircraft type
  const handleAddType = (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    dispatch(createAircraftType(formData))
      .unwrap()
      .then(() => {
        setSuccessMessage('Aircraft type created successfully!');
        setShowAddModal(false);
        resetForm();
        dispatch(fetchAircraftTypes(showInactive));
      })
      .catch((err) => {
        console.error('Failed to create aircraft type:', err);
      });
  };

  // Handle edit aircraft type
  const handleEditType = (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    dispatch(updateAircraftType({ id: selectedType.id, data: formData }))
      .unwrap()
      .then(() => {
        setSuccessMessage('Aircraft type updated successfully!');
        setShowEditModal(false);
        resetForm();
        setSelectedType(null);
        dispatch(fetchAircraftTypes(showInactive));
      })
      .catch((err) => {
        console.error('Failed to update aircraft type:', err);
      });
  };

  // Handle deactivate aircraft type
  const handleDeactivateType = () => {
    dispatch(deactivateAircraftType(selectedType.id))
      .unwrap()
      .then(() => {
        setSuccessMessage('Aircraft type deactivated successfully!');
        setShowDeactivateModal(false);
        setSelectedType(null);
        dispatch(fetchAircraftTypes(showInactive));
      })
      .catch((err) => {
        console.error('Failed to deactivate aircraft type:', err);
      });
  };

  // Open add modal
  const openAddModal = () => {
    resetForm();
    setShowAddModal(true);
  };

  // Open edit modal
  const openEditModal = (type) => {
    setSelectedType(type);
    setFormData({
      name: type.name,
      description: type.description || ''
    });
    setFormErrors({});
    setShowEditModal(true);
  };

  // Open deactivate modal
  const openDeactivateModal = (type) => {
    setSelectedType(type);
    setShowDeactivateModal(true);
  };

  // Check if user is admin
  const isAdmin = currentUser?.is_admin;

  if (!isAdmin) {
    return (
      <Card>
        <CardContent className="pt-6">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Access Denied</AlertTitle>
            <AlertDescription>
              You must be an administrator to access this page.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (loading && aircraftTypes.length === 0) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="w-full space-y-6">
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Plane className="h-5 w-5" />
                Aircraft Type Management
              </CardTitle>
              <CardDescription>Manage aircraft types for kit organization</CardDescription>
            </div>
            <Button onClick={openAddModal}>
              <Plus className="mr-2 h-4 w-4" />
              Add Aircraft Type
            </Button>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {successMessage && (
            <Alert variant="success" className="bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800">
              <Check className="h-4 w-4 text-green-600 dark:text-green-400" />
              <AlertDescription className="text-green-800 dark:text-green-200">
                {successMessage}
              </AlertDescription>
            </Alert>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                {error.message || 'An error occurred'}
              </AlertDescription>
            </Alert>
          )}

          <div className="flex items-center space-x-2">
            <Switch
              id="show-inactive"
              checked={showInactive}
              onCheckedChange={setShowInactive}
            />
            <Label htmlFor="show-inactive" className="text-sm font-normal">
              Show inactive aircraft types
            </Label>
          </div>

          <div className="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="w-[150px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {aircraftTypes.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-muted-foreground">
                      No aircraft types found
                    </TableCell>
                  </TableRow>
                ) : (
                  aircraftTypes.map((type) => (
                    <TableRow key={type.id}>
                      <TableCell>
                        <span className="font-semibold">{type.name}</span>
                      </TableCell>
                      <TableCell>
                        {type.description || <span className="text-muted-foreground">No description</span>}
                      </TableCell>
                      <TableCell>
                        {type.is_active ? (
                          <Badge variant="success" className="gap-1">
                            <Check className="h-3 w-3" />
                            Active
                          </Badge>
                        ) : (
                          <Badge variant="secondary" className="gap-1">
                            <X className="h-3 w-3" />
                            Inactive
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        {type.created_at
                          ? new Date(type.created_at).toLocaleDateString()
                          : 'N/A'}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => openEditModal(type)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          {type.is_active && (
                            <Button
                              variant="destructive"
                              size="sm"
                              onClick={() => openDeactivateModal(type)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Add Aircraft Type Dialog */}
      <Dialog open={showAddModal} onOpenChange={setShowAddModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Aircraft Type</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleAddType}>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="add-name">Name *</Label>
                <Input
                  id="add-name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="e.g., Q400, RJ85, CL415"
                  className={formErrors.name ? 'border-destructive' : ''}
                />
                {formErrors.name && (
                  <p className="text-sm text-destructive">{formErrors.name}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="add-description">Description</Label>
                <Textarea
                  id="add-description"
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Optional description of the aircraft type"
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="secondary" onClick={() => setShowAddModal(false)}>
                Cancel
              </Button>
              <Button type="submit">
                Create Aircraft Type
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Edit Aircraft Type Dialog */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Aircraft Type</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleEditType}>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="edit-name">Name *</Label>
                <Input
                  id="edit-name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="e.g., Q400, RJ85, CL415"
                  className={formErrors.name ? 'border-destructive' : ''}
                />
                {formErrors.name && (
                  <p className="text-sm text-destructive">{formErrors.name}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit-description">Description</Label>
                <Textarea
                  id="edit-description"
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Optional description of the aircraft type"
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="secondary" onClick={() => setShowEditModal(false)}>
                Cancel
              </Button>
              <Button type="submit">
                Update Aircraft Type
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Deactivate Confirmation Dialog */}
      <Dialog open={showDeactivateModal} onOpenChange={setShowDeactivateModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Deactivate Aircraft Type</DialogTitle>
            <DialogDescription>
              Are you sure you want to deactivate the aircraft type{' '}
              <strong>{selectedType?.name}</strong>?
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <Alert variant="warning" className="bg-yellow-50 dark:bg-yellow-950 border-yellow-200 dark:border-yellow-800">
              <AlertCircle className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
              <AlertDescription className="text-yellow-800 dark:text-yellow-200">
                This will prevent new kits from being created for this aircraft type. Existing kits
                will not be affected.
              </AlertDescription>
            </Alert>
            <p className="text-sm text-muted-foreground">
              Note: You cannot deactivate an aircraft type that has active kits.
            </p>
          </div>
          <DialogFooter>
            <Button variant="secondary" onClick={() => setShowDeactivateModal(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeactivateType}>
              Deactivate
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AircraftTypeManagementNew;
