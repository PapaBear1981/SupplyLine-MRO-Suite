import { useState } from 'react';
import { useSelector } from 'react-redux';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Plus, Wrench } from 'lucide-react';

import { Button } from '../components/ui/button';
import { Alert, AlertTitle, AlertDescription } from '../components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import ToolListNew from '../components/tools/ToolListNew';
import BulkImportToolsNew from '../components/tools/BulkImportToolsNew';
import useHotkeys from '../hooks/useHotkeys';

const ToolsManagementNew = () => {
    const { user } = useSelector((state) => state.auth);
    const location = useLocation();
    const navigate = useNavigate();
    const isAdmin = user?.is_admin || user?.department === 'Materials';
    const unauthorized = location.state?.unauthorized;
    const [activeTab, setActiveTab] = useState('available');

    // Page-specific hotkeys
    useHotkeys({
        'n': () => {
            if (isAdmin) {
                navigate('/tools/new');
            }
        }
    }, {
        enabled: isAdmin,
        deps: [navigate, isAdmin]
    });

    return (
        <div className="w-full space-y-6">
            {/* Show unauthorized message if redirected from admin page */}
            {unauthorized && (
                <Alert variant="destructive" className="mb-4">
                    <AlertTitle>Access Denied</AlertTitle>
                    <AlertDescription>
                        You do not have permission to access the Admin Dashboard. This area is restricted to administrators only.
                    </AlertDescription>
                </Alert>
            )}

            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-foreground">Tool Inventory</h1>
                    <p className="text-muted-foreground">Manage tools, equipment, and assets by workflow status.</p>
                </div>
                <div className="flex flex-wrap gap-2">
                    {isAdmin && (
                        <Button asChild variant="outline">
                            <Link to="/calibrations">
                                <Wrench className="mr-2 h-4 w-4" />
                                Calibration Management
                            </Link>
                        </Button>
                    )}
                    {isAdmin && <BulkImportToolsNew />}
                    {isAdmin && (
                        <Button asChild>
                            <Link to="/tools/new">
                                <Plus className="mr-2 h-4 w-4" />
                                Add New Tool
                            </Link>
                        </Button>
                    )}
                </div>
            </div>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList>
                    <TabsTrigger value="available">Available</TabsTrigger>
                    <TabsTrigger value="in_use">In Use</TabsTrigger>
                    <TabsTrigger value="maintenance">Maintenance</TabsTrigger>
                    <TabsTrigger value="calibration">Calibration Due</TabsTrigger>
                    <TabsTrigger value="retired">Retired</TabsTrigger>
                    <TabsTrigger value="all">All Tools</TabsTrigger>
                </TabsList>

                <TabsContent value="available" className="mt-6">
                    <ToolListNew workflowFilter="available" />
                </TabsContent>

                <TabsContent value="in_use" className="mt-6">
                    <ToolListNew workflowFilter="in_use" />
                </TabsContent>

                <TabsContent value="maintenance" className="mt-6">
                    <ToolListNew workflowFilter="maintenance" />
                </TabsContent>

                <TabsContent value="calibration" className="mt-6">
                    <ToolListNew workflowFilter="calibration" />
                </TabsContent>

                <TabsContent value="retired" className="mt-6">
                    <ToolListNew workflowFilter="retired" />
                </TabsContent>

                <TabsContent value="all" className="mt-6">
                    <ToolListNew workflowFilter="all" />
                </TabsContent>
            </Tabs>
        </div>
    );
};

export default ToolsManagementNew;
