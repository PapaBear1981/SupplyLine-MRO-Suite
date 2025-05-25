import PropTypes from 'prop-types';
import { useMobileLayout } from '../../utils/deviceDetection';
import MainLayout from './MainLayout';
import MobileLayout from '../mobile/MobileLayout';

const ResponsiveLayout = ({ children, mobileComponent = null }) => {
  const shouldUseMobileLayout = useMobileLayout();

  if (shouldUseMobileLayout) {
    return (
      <MobileLayout>
        {mobileComponent || children}
      </MobileLayout>
    );
  }

  return (
    <MainLayout>
      {children}
    </MainLayout>
  );
};

ResponsiveLayout.propTypes = {
  children: PropTypes.node.isRequired,
  mobileComponent: PropTypes.node,
};

export default ResponsiveLayout;
