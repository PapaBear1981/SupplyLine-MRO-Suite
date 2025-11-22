import { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { Link, useLocation } from 'react-router-dom';
import { CalendarCheck, CalendarX, History, Ruler, PlusCircle, AlertCircle } from 'lucide-react';
import CalibrationDueList from '../components/calibration/CalibrationDueList';
import CalibrationOverdueList from '../components/calibration/CalibrationOverdueList';
import CalibrationHistoryList from '../components/calibration/CalibrationHistoryList';
import CalibrationStandardsList from '../components/calibration/CalibrationStandardsList';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';
import { Button } from '../components/ui/button';

const CalibrationManagementNew = () => {
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin || user?.department === 'Materials';
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const tabParam = queryParams.get('tab');
  const [activeTab, setActiveTab] = useState(tabParam || 'due');

  // Update active tab when URL query parameter changes
  useEffect(() => {
    if (tabParam && ['due', 'overdue', 'history', 'standards'].includes(tabParam)) {
      setActiveTab(tabParam);
    }
  }, [tabParam]);

  if (!isAdmin) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Access Denied</AlertTitle>
        <AlertDescription>
          You do not have permission to access the calibration management page.
          This feature is only available to administrators and Materials department personnel.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="w-full space-y-6">
      <div className="flex flex-wrap justify-between items-center gap-4">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Calibration Management</h1>
        <Button asChild variant="outline">
          <Link to="/calibration-standards/new">
            <PlusCircle className="mr-2 h-4 w-4" />
            Add Calibration Standard
          </Link>
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Sidebar Navigation */}
        <div className="md:col-span-3 lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Navigation</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="flex flex-col space-y-1">
                <button
                  onClick={() => setActiveTab('due')}
                  className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors ${
                    activeTab === 'due'
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-muted'
                  }`}
                >
                  <CalendarCheck className="h-4 w-4" />
                  Due Soon
                </button>
                <button
                  onClick={() => setActiveTab('overdue')}
                  className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors ${
                    activeTab === 'overdue'
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-muted'
                  }`}
                >
                  <CalendarX className="h-4 w-4" />
                  Overdue
                </button>
                <button
                  onClick={() => setActiveTab('history')}
                  className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors ${
                    activeTab === 'history'
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-muted'
                  }`}
                >
                  <History className="h-4 w-4" />
                  Calibration History
                </button>
                <button
                  onClick={() => setActiveTab('standards')}
                  className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors ${
                    activeTab === 'standards'
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-muted'
                  }`}
                >
                  <Ruler className="h-4 w-4" />
                  Calibration Standards
                </button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="md:col-span-9 lg:col-span-10">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsContent value="due" className="mt-0">
              <Card>
                <CardHeader>
                  <CardTitle>Tools Due for Calibration</CardTitle>
                </CardHeader>
                <CardContent>
                  <CalibrationDueList />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="overdue" className="mt-0">
              <Card>
                <CardHeader>
                  <CardTitle>Overdue Calibrations</CardTitle>
                </CardHeader>
                <CardContent>
                  <CalibrationOverdueList />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="history" className="mt-0">
              <Card>
                <CardHeader>
                  <CardTitle>Calibration History</CardTitle>
                </CardHeader>
                <CardContent>
                  <CalibrationHistoryList />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="standards" className="mt-0">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle>Calibration Standards</CardTitle>
                  <Button asChild size="sm">
                    <Link to="/calibration-standards/new">
                      <PlusCircle className="mr-2 h-4 w-4" />
                      Add Standard
                    </Link>
                  </Button>
                </CardHeader>
                <CardContent>
                  <CalibrationStandardsList />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default CalibrationManagementNew;
