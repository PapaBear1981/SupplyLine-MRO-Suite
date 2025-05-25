import { useState } from 'react';
import { useSelector } from 'react-redux';
import MobileHeader from './MobileHeader';
import MobileBottomNav from './MobileBottomNav';
import MobileHamburgerMenu from './MobileHamburgerMenu';

const MobileLayout = ({ children }) => {
  const { user } = useSelector((state) => state.auth);
  const [showMenu, setShowMenu] = useState(false);

  return (
    <div className="mobile-layout">
      <MobileHeader 
        user={user}
        onMenuToggle={() => setShowMenu(!showMenu)}
      />
      
      <main className="mobile-content">
        {children}
      </main>
      
      <MobileBottomNav user={user} />
      
      <MobileHamburgerMenu 
        show={showMenu}
        onHide={() => setShowMenu(false)}
        user={user}
      />
    </div>
  );
};

export default MobileLayout;
