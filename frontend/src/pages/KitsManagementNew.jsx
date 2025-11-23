import React, { useEffect, useState, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Plus, Search, AlertTriangle, Package, Plane } from 'lucide-react';
import { fetchKits, fetchAircraftTypes } from '../store/kitsSlice';
import { fetchUnreadCount } from '../store/kitMessagesSlice';
import LoadingSpinner from '../components/common/LoadingSpinner';
import useHotkeys from '../hooks/useHotkeys';

import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';

const KitsManagementNew = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { kits, aircraftTypes, loading } = useSelector((state) => state.kits);
  const { unreadCount } = useSelector((state) => state.kitMessages);

  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAircraftType, setSelectedAircraftType] = useState('all');
  const searchInputRef = useRef(null);

  // Page-specific hotkeys
  useHotkeys({
    'n': () => navigate('/kits/new'),
    '/': () => searchInputRef.current?.focus()
  }, {
    deps: [navigate]
  });

  useEffect(() => {
    dispatch(fetchKits());
    dispatch(fetchAircraftTypes());
    dispatch(fetchUnreadCount());
  }, [dispatch]);

  const filteredKits = kits.filter(kit => {
    // Filter by tab
    if (activeTab === 'active' && kit.status !== 'active') return false;
    if (activeTab === 'inactive' && kit.status !== 'inactive') return false;
    if (activeTab === 'alerts' && (!kit.alert_count || kit.alert_count === 0)) return false;

    // Filter by search term
    if (searchTerm && !kit.name.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }

    // Filter by aircraft type
    if (selectedAircraftType !== 'all' && kit.aircraft_type_id !== parseInt(selectedAircraftType)) {
      return false;
    }

    return true;
  });

  const getStatusBadge = (status) => {
    const variants = {
      active: 'default',
      inactive: 'secondary',
      maintenance: 'warning'
    };
    return (
      <Badge variant={variants[status] || 'secondary'} className="capitalize">
        {status}
      </Badge>
    );
  };

  const KitCard = ({ kit }) => {
    const aircraftType = aircraftTypes.find(at => at.id === kit.aircraft_type_id);

    return (
      <Card
        className="group cursor-pointer transition-all duration-200 hover:shadow-lg dark:hover:shadow-primary/25 hover:bg-accent/10"
        onClick={() => navigate(`/kits/${kit.id}`)}
        data-testid="kit-card"
      >
        <CardContent className="p-6">
          <div className="flex justify-between items-start mb-3">
            <div className="flex-1">
              <h3 className="text-lg font-semibold mb-1 group-hover:text-primary transition-colors">
                {kit.name}
              </h3>
              <div className="flex items-center text-sm text-muted-foreground">
                <Plane className="mr-1 h-3 w-3" />
                {aircraftType?.name || 'Unknown'}
              </div>
            </div>
            <div>
              {getStatusBadge(kit.status)}
            </div>
          </div>

          {kit.description && (
            <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
              {kit.description}
            </p>
          )}

          <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t">
            <div className="text-center">
              <div className="text-xs text-muted-foreground mb-1">Boxes</div>
              <div className="text-lg font-bold">{kit.box_count || 0}</div>
            </div>
            <div className="text-center">
              <div className="text-xs text-muted-foreground mb-1">Items</div>
              <div className="text-lg font-bold">{kit.item_count || 0}</div>
            </div>
            <div className="text-center">
              <div className="text-xs text-muted-foreground mb-1">Alerts</div>
              <div className={`text-lg font-bold ${kit.alert_count > 0 ? 'text-destructive' : ''}`}>
                <div className="flex items-center justify-center gap-1">
                  {kit.alert_count || 0}
                  {kit.alert_count > 0 && <AlertTriangle className="h-4 w-4" />}
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  const activeKitsCount = kits.filter(k => k.status === 'active').length;
  const inactiveKitsCount = kits.filter(k => k.status === 'inactive').length;
  const alertKitsCount = kits.filter(k => k.alert_count > 0).length;

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Package className="h-8 w-8" />
            Mobile Warehouses (Kits)
          </h1>
          <p className="text-muted-foreground mt-1">
            Manage mobile warehouses that follow aircraft to operating bases
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            onClick={() => navigate('/kits/new')}
            data-testid="create-kit-button"
          >
            <Plus className="mr-2 h-4 w-4" />
            Create Kit
          </Button>
          {unreadCount > 0 && (
            <Button
              variant="outline"
              onClick={() => navigate('/kits/messages')}
              data-testid="messages-button"
            >
              Messages
              <Badge variant="destructive" className="ml-2">{unreadCount}</Badge>
            </Button>
          )}
        </div>
      </div>

      {/* Search and Filter */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="relative">
          <Label htmlFor="search-kits" className="sr-only">Search kits</Label>
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            id="search-kits"
            ref={searchInputRef}
            type="text"
            placeholder="Search kits..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
            data-testid="search-kits-input"
          />
        </div>
        <div>
          <Label htmlFor="aircraft-type-filter" className="sr-only">Filter by aircraft type</Label>
          <Select
            value={selectedAircraftType}
            onValueChange={setSelectedAircraftType}
          >
            <SelectTrigger id="aircraft-type-filter" data-testid="aircraft-type-filter">
              <SelectValue placeholder="All Aircraft Types" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Aircraft Types</SelectItem>
              {aircraftTypes.map(at => (
                <SelectItem key={at.id} value={at.id.toString()}>
                  {at.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="all">
            All Kits ({kits.length})
          </TabsTrigger>
          <TabsTrigger value="active">
            Active ({activeKitsCount})
          </TabsTrigger>
          <TabsTrigger value="inactive">
            Inactive ({inactiveKitsCount})
          </TabsTrigger>
          <TabsTrigger value="alerts" className="relative">
            Alerts
            {alertKitsCount > 0 && (
              <Badge variant="destructive" className="ml-2">
                {alertKitsCount}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="mt-6">
          {filteredKits.length === 0 ? (
            <Card className="p-12">
              <div className="text-center">
                <Package className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No kits found</h3>
                <p className="text-muted-foreground mb-4">
                  {searchTerm || selectedAircraftType
                    ? 'Try adjusting your filters'
                    : 'Create your first kit to get started'}
                </p>
                {!searchTerm && !selectedAircraftType && (
                  <Button onClick={() => navigate('/kits/new')}>
                    <Plus className="mr-2 h-4 w-4" />
                    Create Kit
                  </Button>
                )}
              </div>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredKits.map(kit => (
                <KitCard key={kit.id} kit={kit} />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="active" className="mt-6">
          {filteredKits.length === 0 ? (
            <Card className="p-12">
              <div className="text-center">
                <Package className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No active kits found</h3>
                <p className="text-muted-foreground">
                  Try adjusting your filters
                </p>
              </div>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredKits.map(kit => (
                <KitCard key={kit.id} kit={kit} />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="inactive" className="mt-6">
          {filteredKits.length === 0 ? (
            <Card className="p-12">
              <div className="text-center">
                <Package className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No inactive kits found</h3>
                <p className="text-muted-foreground">
                  Try adjusting your filters
                </p>
              </div>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredKits.map(kit => (
                <KitCard key={kit.id} kit={kit} />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="alerts" className="mt-6">
          {filteredKits.length === 0 ? (
            <Card className="p-12">
              <div className="text-center">
                <Package className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No kits with alerts</h3>
                <p className="text-muted-foreground">
                  All kits are in good condition
                </p>
              </div>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredKits.map(kit => (
                <KitCard key={kit.id} kit={kit} />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default KitsManagementNew;
