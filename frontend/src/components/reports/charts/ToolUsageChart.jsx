import { Card } from 'react-bootstrap';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ToolUsageChart = ({ data }) => {
  // Check if we have the necessary data
  if (!data || !data.toolUsageByCategory || data.toolUsageByCategory.length === 0) {
    return (
      <Card className="shadow-sm">
        <Card.Header className="bg-light">
          <h5 className="mb-0">Tool Usage by Category</h5>
        </Card.Header>
        <Card.Body className="text-center text-muted p-5">
          No tool usage data available
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm">
      <Card.Header className="bg-light">
        <h5 className="mb-0">Tool Usage by Category</h5>
      </Card.Header>
      <Card.Body>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={data.toolUsageByCategory}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="checkouts" fill="#8884d8" name="Checkouts" />
            <Bar dataKey="returns" fill="#82ca9d" name="Returns" />
          </BarChart>
        </ResponsiveContainer>
      </Card.Body>
    </Card>
  );
};

export default ToolUsageChart;
