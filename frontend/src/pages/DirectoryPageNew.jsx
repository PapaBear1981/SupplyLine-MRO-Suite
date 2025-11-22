import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { useLocation, useNavigate } from 'react-router-dom';
import { Search, Users, ArrowRight, Loader2 } from 'lucide-react';
import api from '../services/api';
import UserProfileModal from '../components/users/UserProfileModal';
import { Card, CardContent, CardFooter, CardHeader } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Avatar, AvatarFallback } from '../components/ui/avatar';

const DirectoryPageNew = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  const location = useLocation();
  const navigate = useNavigate();

  // Helper function to get department badge variant
  const getDepartmentBadgeVariant = (department) => {
    const departmentColors = {
      'Materials': 'default',
      'Engineering': 'secondary',
      'Maintenance': 'warning',
      'Quality': 'success',
      'Production': 'destructive',
      'Safety': 'outline',
      'Administration': 'secondary',
    };
    return departmentColors[department] || 'secondary';
  };

  // Fetch current user permissions
  useEffect(() => {
    const fetchCurrentUser = async () => {
      try {
        const response = await api.get('/auth/me');
        setCurrentUser(response.data);
      } catch (error) {
        console.error('Error fetching current user:', error);
      }
    };
    fetchCurrentUser();
  }, []);

  // Check for userId in query params
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const userIdParam = searchParams.get('userId');

    if (userIdParam) {
      // Set selected user with just the ID to trigger the modal
      // The modal fetches full details itself
      setSelectedUser({ id: parseInt(userIdParam) });
      setShowProfileModal(true);
    }
  }, [location.search]);

  // Fetch users list
  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      try {
        const endpoint = searchQuery
          ? `/users?q=${encodeURIComponent(searchQuery)}`
          : '/users';

        const response = await api.get(endpoint);
        setUsers(response.data);
      } catch (error) {
        console.error('Error fetching users:', error);
        toast.error('Failed to load directory. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    // Debounce search
    const timeoutId = setTimeout(() => {
      fetchUsers();
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  const handleUserClick = (user) => {
    setSelectedUser(user);
    setShowProfileModal(true);
    // Update URL without reloading to allow bookmarking/sharing
    navigate(`/directory?userId=${user.id}`, { replace: true });
  };

  const handleCloseModal = () => {
    setShowProfileModal(false);
    setSelectedUser(null);
    // Clear query param on close
    navigate('/directory', { replace: true });
  };

  const handleUserUpdated = (updatedUser) => {
    setUsers(users.map(u => u.id === updatedUser.id ? updatedUser : u));
  };

  return (
    <div className="w-full space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Employee Directory</h1>
        <p className="text-muted-foreground">
          Search and view employee profiles, checkouts, and history.
        </p>
      </div>

      <Card className="shadow-sm">
        <CardHeader className="pb-3">
          <div className="flex flex-col gap-4 md:flex-row md:items-center">
            <div className="relative flex-1 md:max-w-md">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by name or badge ID..."
                className="pl-9"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-0">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              <p className="mt-4 text-muted-foreground">Loading directory...</p>
            </div>
          ) : users.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Users className="h-16 w-16 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold">No employees found</h3>
              <p className="text-muted-foreground">
                Try adjusting your search terms.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="pl-6">Employee</TableHead>
                    <TableHead>Badge ID</TableHead>
                    <TableHead>Department</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right pr-6">Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {users.map((user) => (
                    <TableRow
                      key={user.id}
                      onClick={() => handleUserClick(user)}
                      className="cursor-pointer hover:bg-muted/50"
                    >
                      <TableCell className="pl-6">
                        <div className="flex items-center gap-3">
                          <Avatar className="h-10 w-10">
                            <AvatarFallback className="bg-primary text-primary-foreground">
                              {user.name.charAt(0).toUpperCase()}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <div className="font-semibold">{user.name}</div>
                            <div className="text-sm text-muted-foreground">{user.email || 'No email'}</div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="font-mono text-sm">{user.employee_number}</span>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getDepartmentBadgeVariant(user.department)}>
                          {user.department || 'Unassigned'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {user.is_active ? (
                            <Badge variant="success" className="gap-1">
                              <i className="bi bi-check-circle-fill text-xs"></i>
                              Active
                            </Badge>
                          ) : (
                            <Badge variant="secondary">Inactive</Badge>
                          )}
                          {user.is_admin && (
                            <Badge variant="default">Admin</Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-right pr-6">
                        <Button
                          variant="link"
                          className="p-0 h-auto"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleUserClick(user);
                          }}
                        >
                          View Profile <ArrowRight className="ml-1 h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
        <CardFooter className="text-sm text-muted-foreground">
          Showing {users.length} employees
        </CardFooter>
      </Card>

      {selectedUser && (
        <UserProfileModal
          show={showProfileModal}
          onHide={handleCloseModal}
          userId={selectedUser.id}
          onUserUpdated={handleUserUpdated}
        />
      )}
    </div>
  );
};

export default DirectoryPageNew;
