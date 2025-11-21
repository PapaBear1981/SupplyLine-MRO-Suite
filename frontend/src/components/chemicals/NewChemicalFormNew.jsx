import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { FlaskConical, Save, X } from 'lucide-react';
import { toast } from 'sonner';

import { createChemical } from '../../store/chemicalsSlice';
import LotNumberInput from '../common/LotNumberInput';
import api from '../../services/api';

// UI Components
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { Textarea } from '../ui/textarea';

const NewChemicalFormNew = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, error } = useSelector((state) => state.chemicals);

  // Warehouse state
  const [warehouses, setWarehouses] = useState([]);
  const [loadingWarehouses, setLoadingWarehouses] = useState(false);
  const [warehouseError, setWarehouseError] = useState(null);

  const [chemicalData, setChemicalData] = useState({
    part_number: '',
    lot_number: '',
    description: '',
    manufacturer: '',
    quantity: '',
    unit: 'each',
    location: '',
    category: 'General',
    warehouse_id: '',  // Required field
    expiration_date: '',
    minimum_stock_level: '',
    notes: ''
  });
  const [validationErrors, setValidationErrors] = useState({});

  // Fetch warehouses on mount
  useEffect(() => {
    const fetchWarehouses = async () => {
      setLoadingWarehouses(true);
      try {
        const response = await api.get('/warehouses');
        const warehousesData = response.data.warehouses || response.data;
        setWarehouses(Array.isArray(warehousesData) ? warehousesData : []);
      } catch (err) {
        console.error('Failed to fetch warehouses:', err);
        setWarehouseError('Failed to load warehouses. Please refresh the page.');
      } finally {
        setLoadingWarehouses(false);
      }
    };

    fetchWarehouses();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setChemicalData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear validation error for this field
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleSelectChange = (name, value) => {
    setChemicalData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear validation error for this field
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const errors = {};

    if (!chemicalData.part_number.trim()) {
      errors.part_number = 'Part number is required';
    }

    if (!chemicalData.lot_number.trim()) {
      errors.lot_number = 'Lot number is required';
    }

    if (!chemicalData.warehouse_id) {
      errors.warehouse_id = 'Warehouse is required';
    }

    if (!chemicalData.quantity || parseInt(chemicalData.quantity) < 1) {
      errors.quantity = 'Quantity is required and must be at least 1';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!validateForm()) {
      toast.error('Please fix the validation errors');
      return;
    }

    // Convert quantity and minimum_stock_level to integers, warehouse_id to integer, empty dates to null
    const formattedData = {
      ...chemicalData,
      quantity: parseInt(chemicalData.quantity),
      minimum_stock_level: chemicalData.minimum_stock_level ? parseInt(chemicalData.minimum_stock_level) : null,
      warehouse_id: chemicalData.warehouse_id ? parseInt(chemicalData.warehouse_id) : null,
      expiration_date: chemicalData.expiration_date || null
    };

    dispatch(createChemical(formattedData))
      .unwrap()
      .then(() => {
        toast.success('Chemical added successfully!');
        // Navigate after showing success message for a short time
        setTimeout(() => {
          navigate('/chemicals');
        }, 1000);
      })
      .catch((err) => {
        console.error('Failed to create chemical:', err);
        toast.error('Failed to create chemical');
      });
  };

  return (
    <Card className="shadow-sm border-border">
      <CardHeader className="bg-muted/50 dark:bg-muted/20">
        <div className="flex items-center gap-3">
          <FlaskConical className="h-6 w-6 text-primary" />
          <CardTitle className="text-2xl">Add New Chemical</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error.error || error.message || 'An error occurred'}</AlertDescription>
          </Alert>
        )}
        {warehouseError && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{warehouseError}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Part Number and Lot Number */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="part_number">
                Part Number <span className="text-destructive">*</span>
              </Label>
              <Input
                id="part_number"
                name="part_number"
                value={chemicalData.part_number}
                onChange={handleChange}
                className={validationErrors.part_number ? 'border-destructive' : ''}
              />
              {validationErrors.part_number && (
                <p className="text-sm text-destructive">{validationErrors.part_number}</p>
              )}
            </div>

            <div className="space-y-2">
              <LotNumberInput
                value={chemicalData.lot_number}
                onChange={(value) => {
                  setChemicalData(prev => ({ ...prev, lot_number: value }));
                  if (validationErrors.lot_number) {
                    setValidationErrors(prev => ({ ...prev, lot_number: '' }));
                  }
                }}
                disabled={loading}
                required={true}
                label="Lot Number"
                helpText="Auto-generate a unique lot number or enter manually"
                showAutoGenerate={true}
              />
              {validationErrors.lot_number && (
                <p className="text-sm text-destructive">{validationErrors.lot_number}</p>
              )}
            </div>
          </div>

          {/* Warehouse */}
          <div className="space-y-2">
            <Label htmlFor="warehouse_id">
              Warehouse <span className="text-destructive">*</span>
            </Label>
            <Select
              value={chemicalData.warehouse_id}
              onValueChange={(value) => handleSelectChange('warehouse_id', value)}
              disabled={loadingWarehouses}
            >
              <SelectTrigger className={validationErrors.warehouse_id ? 'border-destructive' : ''}>
                <SelectValue placeholder={loadingWarehouses ? 'Loading warehouses...' : 'Select a warehouse...'} />
              </SelectTrigger>
              <SelectContent>
                {warehouses.map(warehouse => (
                  <SelectItem key={warehouse.id} value={warehouse.id.toString()}>
                    {warehouse.name} - {warehouse.city}, {warehouse.state}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {validationErrors.warehouse_id && (
              <p className="text-sm text-destructive">{validationErrors.warehouse_id}</p>
            )}
            <p className="text-sm text-muted-foreground">
              All chemicals must be created in a warehouse before they can be transferred to kits.
            </p>
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              name="description"
              rows={3}
              value={chemicalData.description}
              onChange={handleChange}
              className="resize-none"
            />
          </div>

          {/* Manufacturer */}
          <div className="space-y-2">
            <Label htmlFor="manufacturer">Manufacturer</Label>
            <Input
              id="manufacturer"
              name="manufacturer"
              value={chemicalData.manufacturer}
              onChange={handleChange}
            />
          </div>

          {/* Quantity and Unit */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="quantity">
                Quantity <span className="text-destructive">*</span>
              </Label>
              <Input
                id="quantity"
                name="quantity"
                type="number"
                step="1"
                min="1"
                value={chemicalData.quantity}
                onChange={handleChange}
                className={validationErrors.quantity ? 'border-destructive' : ''}
              />
              {validationErrors.quantity && (
                <p className="text-sm text-destructive">{validationErrors.quantity}</p>
              )}
              <p className="text-sm text-muted-foreground">
                Only whole numbers allowed (e.g., 1, 5, 10)
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="unit">
                Unit <span className="text-destructive">*</span>
              </Label>
              <Select
                value={chemicalData.unit}
                onValueChange={(value) => handleSelectChange('unit', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="each">Each</SelectItem>
                  <SelectItem value="oz">Ounce (oz)</SelectItem>
                  <SelectItem value="ml">Milliliter (ml)</SelectItem>
                  <SelectItem value="l">Liter (l)</SelectItem>
                  <SelectItem value="g">Gram (g)</SelectItem>
                  <SelectItem value="kg">Kilogram (kg)</SelectItem>
                  <SelectItem value="lb">Pound (lb)</SelectItem>
                  <SelectItem value="gal">Gallon (gal)</SelectItem>
                  <SelectItem value="tubes">Tubes</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Location and Category */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                name="location"
                value={chemicalData.location}
                onChange={handleChange}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="category">Category</Label>
              <Select
                value={chemicalData.category}
                onValueChange={(value) => handleSelectChange('category', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="General">General</SelectItem>
                  <SelectItem value="Sealant">Sealant</SelectItem>
                  <SelectItem value="Paint">Paint</SelectItem>
                  <SelectItem value="Adhesive">Adhesive</SelectItem>
                  <SelectItem value="Lubricant">Lubricant</SelectItem>
                  <SelectItem value="Solvent">Solvent</SelectItem>
                  <SelectItem value="Cleaner">Cleaner</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Expiration Date and Minimum Stock Level */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="expiration_date">Expiration Date</Label>
              <Input
                id="expiration_date"
                name="expiration_date"
                type="date"
                value={chemicalData.expiration_date}
                onChange={handleChange}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="minimum_stock_level">Minimum Stock Level</Label>
              <Input
                id="minimum_stock_level"
                name="minimum_stock_level"
                type="number"
                step="1"
                min="1"
                value={chemicalData.minimum_stock_level}
                onChange={handleChange}
              />
              <p className="text-sm text-muted-foreground">
                Set a threshold for low stock alerts (whole numbers only)
              </p>
            </div>
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              name="notes"
              rows={3}
              value={chemicalData.notes}
              onChange={handleChange}
              className="resize-none"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/chemicals')}
              disabled={loading}
            >
              <X className="h-4 w-4 mr-2" />
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              <Save className="h-4 w-4 mr-2" />
              {loading ? 'Saving...' : 'Save Chemical'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default NewChemicalFormNew;
