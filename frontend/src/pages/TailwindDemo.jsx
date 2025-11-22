import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';

const TailwindDemo = () => {
    return (
        <div className="p-8 space-y-8">
            <div>
                <h1 className="text-4xl font-bold mb-2">Tailwind + shadcn/ui Demo</h1>
                <p className="text-muted-foreground">
                    This page demonstrates the new design system components.
                </p>
            </div>

            {/* Buttons Section */}
            <Card>
                <CardHeader>
                    <CardTitle>Buttons</CardTitle>
                    <CardDescription>Various button styles and variants</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-2">
                    <Button>Default</Button>
                    <Button variant="secondary">Secondary</Button>
                    <Button variant="destructive">Destructive</Button>
                    <Button variant="outline">Outline</Button>
                    <Button variant="ghost">Ghost</Button>
                    <Button variant="link">Link</Button>
                    <Button size="sm">Small</Button>
                    <Button size="lg">Large</Button>
                </CardContent>
            </Card>

            {/* Badges Section */}
            <Card>
                <CardHeader>
                    <CardTitle>Badges</CardTitle>
                    <CardDescription>Status indicators and labels</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-2">
                    <Badge>Default</Badge>
                    <Badge variant="secondary">Secondary</Badge>
                    <Badge variant="destructive">Destructive</Badge>
                    <Badge variant="outline">Outline</Badge>
                    <Badge variant="success">Success</Badge>
                    <Badge variant="warning">Warning</Badge>
                    <Badge variant="info">Info</Badge>
                </CardContent>
            </Card>

            {/* Input Section */}
            <Card>
                <CardHeader>
                    <CardTitle>Form Inputs</CardTitle>
                    <CardDescription>Text inputs and form controls</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Email</label>
                        <Input type="email" placeholder="Enter your email" />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Password</label>
                        <Input type="password" placeholder="Enter your password" />
                    </div>
                </CardContent>
            </Card>

            {/* Table Section */}
            <Card>
                <CardHeader>
                    <CardTitle>Data Table</CardTitle>
                    <CardDescription>Example inventory table</CardDescription>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Tool ID</TableHead>
                                <TableHead>Name</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Location</TableHead>
                                <TableHead className="text-right">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            <TableRow>
                                <TableCell className="font-medium">T-001</TableCell>
                                <TableCell>Torque Wrench</TableCell>
                                <TableCell>
                                    <Badge variant="success">Available</Badge>
                                </TableCell>
                                <TableCell>Warehouse A</TableCell>
                                <TableCell className="text-right">
                                    <Button size="sm" variant="outline">View</Button>
                                </TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell className="font-medium">T-002</TableCell>
                                <TableCell>Drill Press</TableCell>
                                <TableCell>
                                    <Badge variant="warning">Checked Out</Badge>
                                </TableCell>
                                <TableCell>Warehouse B</TableCell>
                                <TableCell className="text-right">
                                    <Button size="sm" variant="outline">View</Button>
                                </TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell className="font-medium">T-003</TableCell>
                                <TableCell>Multimeter</TableCell>
                                <TableCell>
                                    <Badge variant="info">Maintenance</Badge>
                                </TableCell>
                                <TableCell>Warehouse A</TableCell>
                                <TableCell className="text-right">
                                    <Button size="sm" variant="outline">View</Button>
                                </TableCell>
                            </TableRow>
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            {/* Stats Cards Section */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                    <CardHeader className="pb-2">
                        <CardDescription>Total Tools</CardDescription>
                        <CardTitle className="text-3xl">1,234</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-xs text-muted-foreground">+12% from last month</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardDescription>Checked Out</CardDescription>
                        <CardTitle className="text-3xl">456</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-xs text-muted-foreground">+5% from last month</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardDescription>In Maintenance</CardDescription>
                        <CardTitle className="text-3xl">23</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-xs text-muted-foreground">-2% from last month</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardDescription>Available</CardDescription>
                        <CardTitle className="text-3xl">755</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-xs text-muted-foreground">+8% from last month</p>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default TailwindDemo;
