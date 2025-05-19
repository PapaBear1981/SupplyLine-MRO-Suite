import { Card } from 'react-bootstrap';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { formatChartDate } from '../../../utils/dateUtils';

const CheckoutTrendsChart = ({ data, timeframe }) => {
  // Check if we have the necessary data
  if (!data || !data.checkoutsByDay || data.checkoutsByDay.length === 0) {
    return (
      <Card className="shadow-sm">
        <Card.Header className="bg-light">
          <h5 className="mb-0">Checkout Trends</h5>
        </Card.Header>
        <Card.Body className="text-center text-muted p-5">
          No checkout trend data available
        </Card.Body>
      </Card>
    );
  }

  // Format the title based on timeframe
  let timeframeTitle = 'Over Time';
  switch (timeframe) {
    case 'week':
      timeframeTitle = 'Last 7 Days';
      break;
    case 'month':
      timeframeTitle = 'Last 30 Days';
      break;
    case 'quarter':
      timeframeTitle = 'Last 90 Days';
      break;
    case 'year':
      timeframeTitle = 'Last 365 Days';
      break;
    case 'all':
      timeframeTitle = 'All Time';
      break;
    default:
      timeframeTitle = 'Over Time';
  }

  // Format the dates for the chart
  const formattedData = data.checkoutsByDay.map(item => ({
    ...item,
    formattedDate: formatChartDate(item.date)
  }));

  return (
    <Card className="shadow-sm">
      <Card.Header className="bg-light">
        <h5 className="mb-0">Checkout Trends {timeframeTitle}</h5>
      </Card.Header>
      <Card.Body>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={formattedData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="formattedDate" />
            <YAxis />
            <Tooltip labelFormatter={(value) => `Date: ${value}`} />
            <Legend />
            <Line
              type="monotone"
              dataKey="checkouts"
              stroke="#8884d8"
              activeDot={{ r: 8 }}
              name="Checkouts"
            />
            <Line
              type="monotone"
              dataKey="returns"
              stroke="#82ca9d"
              name="Returns"
            />
          </LineChart>
        </ResponsiveContainer>
      </Card.Body>
    </Card>
  );
};

export default CheckoutTrendsChart;
