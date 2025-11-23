import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { RotateCcw } from 'lucide-react';
import { fetchUserCheckouts } from '../../store/checkoutsSlice';
import LoadingSpinner from '../common/LoadingSpinner';
import ReturnToolModal from './ReturnToolModal';
import { formatDate } from '../../utils/dateUtils';
import { Button } from '../ui/button';
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
import { Alert, AlertDescription } from '../ui/alert';
import { Info } from 'lucide-react';

const UserCheckoutsNew = () => {
  const dispatch = useDispatch();
  const { userCheckouts, loading } = useSelector((state) => state.checkouts);
  const { user } = useSelector((state) => state.auth);
  const [showReturnModal, setShowReturnModal] = useState(false);
  const [selectedCheckoutId, setSelectedCheckoutId] = useState(null);
  const [selectedToolInfo, setSelectedToolInfo] = useState(null);

  // Check if user has permission to return tools
  const canReturnTools = user?.is_admin || user?.department === 'Materials';

  useEffect(() => {
    dispatch(fetchUserCheckouts())
      .catch(error => {
        console.error("UserCheckouts: Error fetching user checkouts:", error);
      });
  }, [dispatch]);

  const handleReturnTool = (checkout) => {
    setSelectedCheckoutId(checkout.id);
    setSelectedToolInfo({
      tool_number: checkout.tool_number,
      serial_number: checkout.serial_number,
      description: checkout.description,
      user_name: user?.name || 'Current User'
    });
    setShowReturnModal(true);
  };

  if (loading && !userCheckouts.length) {
    return <LoadingSpinner />;
  }

  // Filter active checkouts (not returned)
  const activeCheckouts = userCheckouts.filter(checkout => !checkout.return_date);

  // Filter past checkouts (returned)
  const pastCheckouts = userCheckouts.filter(checkout => checkout.return_date);

  const getStatusBadge = (checkout) => {
    if (checkout.return_date) {
      return <Badge variant="outline">Returned</Badge>;
    }

    if (checkout.expected_return_date && new Date(checkout.expected_return_date) < new Date()) {
      return <Badge variant="destructive">Overdue</Badge>;
    }

    return <Badge variant="secondary">Checked Out</Badge>;
  };

  return (
    <>
      <div className="w-full space-y-6">
        {!canReturnTools && activeCheckouts.length > 0 && (
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              <strong>Note:</strong> Only Materials department and Admin personnel can return tools. Please contact them to return your tools.
            </AlertDescription>
          </Alert>
        )}

        {/* Active Checkouts */}
        <Card>
          <CardHeader>
            <CardTitle>Active Checkouts</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Tool Number</TableHead>
                    <TableHead>Serial Number</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Checkout Date</TableHead>
                    <TableHead>Expected Return</TableHead>
                    <TableHead>Status</TableHead>
                    {canReturnTools && (
                      <TableHead className="w-[150px]">Actions</TableHead>
                    )}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {activeCheckouts.length > 0 ? (
                    activeCheckouts.map((checkout) => (
                      <TableRow key={checkout.id}>
                        <TableCell>
                          <Link
                            to={`/tools/${checkout.tool_id}`}
                            className="font-semibold text-primary hover:underline"
                          >
                            {checkout.tool_number}
                          </Link>
                        </TableCell>
                        <TableCell>{checkout.serial_number}</TableCell>
                        <TableCell>{checkout.description}</TableCell>
                        <TableCell>{formatDate(checkout.checkout_date)}</TableCell>
                        <TableCell>
                          {formatDate(checkout.expected_return_date)}
                        </TableCell>
                        <TableCell>
                          {getStatusBadge(checkout)}
                        </TableCell>
                        {canReturnTools && (
                          <TableCell>
                            <Button
                              size="sm"
                              onClick={() => handleReturnTool(checkout)}
                              className="w-full"
                            >
                              <RotateCcw className="mr-2 h-4 w-4" />
                              Return
                            </Button>
                          </TableCell>
                        )}
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={canReturnTools ? 7 : 6} className="text-center py-8 text-muted-foreground">
                        You have no active checkouts.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        {/* Checkout History */}
        <Card>
          <CardHeader>
            <CardTitle>Checkout History</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Tool Number</TableHead>
                    <TableHead>Serial Number</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Checkout Date</TableHead>
                    <TableHead>Return Date</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {pastCheckouts.length > 0 ? (
                    pastCheckouts.map((checkout) => (
                      <TableRow key={checkout.id}>
                        <TableCell>
                          <Link
                            to={`/tools/${checkout.tool_id}`}
                            className="font-semibold text-primary hover:underline"
                          >
                            {checkout.tool_number}
                          </Link>
                        </TableCell>
                        <TableCell>{checkout.serial_number}</TableCell>
                        <TableCell>{checkout.description}</TableCell>
                        <TableCell>{formatDate(checkout.checkout_date)}</TableCell>
                        <TableCell>{formatDate(checkout.return_date)}</TableCell>
                        <TableCell>
                          {getStatusBadge(checkout)}
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                        You have no checkout history.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Return Tool Modal */}
      <ReturnToolModal
        show={showReturnModal}
        onHide={() => setShowReturnModal(false)}
        checkoutId={selectedCheckoutId}
        toolInfo={selectedToolInfo}
      />
    </>
  );
};

export default UserCheckoutsNew;
