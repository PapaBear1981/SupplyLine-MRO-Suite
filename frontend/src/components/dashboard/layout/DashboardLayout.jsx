import React from 'react';
import { Responsive, WidthProvider } from 'react-grid-layout';
import Widget from './Widget';
import OverdueChemicals from '../OverdueChemicals';
import CalibrationNotifications from '../../calibration/CalibrationNotifications';
import UserCheckoutStatus from '../UserCheckoutStatus';
import RecentActivity from '../RecentActivity';
import Announcements from '../Announcements';
import QuickActions from '../QuickActions';
import PastDueTools from '../PastDueTools';
import MyKits from '../MyKits';
import KitAlertsSummary from '../KitAlertsSummary';
import RecentKitActivity from '../RecentKitActivity';

const ResponsiveGridLayout = WidthProvider(Responsive);

const widgetComponents = {
  OverdueChemicals,
  CalibrationNotifications,
  UserCheckoutStatus,
  RecentActivity,
  Announcements,
  QuickActions,
  PastDueTools,
  MyKits,
  KitAlertsSummary,
  RecentKitActivity,
};

const DashboardLayout = ({ layout, onLayoutChange, onRemoveWidget }) => {
  return (
    <ResponsiveGridLayout
      className="layout"
      layouts={{ lg: layout }}
      breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
      cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
      rowHeight={30}
      onLayoutChange={(newLayout) => onLayoutChange(newLayout)}
    >
      {layout.map((item) => {
        const WidgetComponent = widgetComponents[item.i];
        return (
          <div key={item.i} data-grid={item}>
            <Widget
              title={item.i.replace(/([A-Z])/g, ' $1').trim()}
              onRemove={() => onRemoveWidget(item.i)}
            >
              {WidgetComponent ? <WidgetComponent /> : <div>Widget not found</div>}
            </Widget>
          </div>
        );
      })}
    </ResponsiveGridLayout>
  );
};

export default DashboardLayout;
