import { useMemo } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { FaBarcode, FaClipboardList, FaTools, FaTruckLoading, FaBoxes, FaQuestionCircle } from 'react-icons/fa';
import './MobileHomePage.css';

const MobileHomePage = () => {
  const { user } = useSelector((state) => state.auth);
  const navigate = useNavigate();

  const quickActions = useMemo(
    () => [
      {
        title: 'Scan & Go',
        description: 'Open the scanner to check tools in or out instantly.',
        icon: <FaBarcode />,
        onClick: () => navigate('/scanner'),
        accent: 'accent-blue'
      },
      {
        title: 'Find a Tool',
        description: 'Search inventory, check availability, and start a checkout.',
        icon: <FaTools />,
        onClick: () => navigate('/tools?tab=search'),
        accent: 'accent-green'
      },
      {
        title: 'Request Something',
        description: 'Create or track material and tooling requests.',
        icon: <FaClipboardList />,
        onClick: () => navigate('/requests'),
        accent: 'accent-orange'
      },
      {
        title: 'Receive & Returns',
        description: 'Jump to orders and returns in one tap.',
        icon: <FaTruckLoading />,
        onClick: () => navigate('/orders'),
        accent: 'accent-purple'
      }
    ],
    [navigate]
  );

  const secondaryShortcuts = useMemo(
    () => [
      {
        title: 'Kits & Stowage',
        description: 'Open the mobile-first kit interface.',
        icon: <FaBoxes />,
        onClick: () => navigate('/kits')
      },
      {
        title: 'Need help?',
        description: 'Review help docs or open a support request.',
        icon: <FaQuestionCircle />,
        onClick: () => navigate('/dashboard?showHelp=true')
      }
    ],
    [navigate]
  );

  return (
    <div className="mobile-home">
      <section className="mobile-home__hero">
        <div>
          <p className="mobile-home__eyebrow">Mobile cockpit</p>
          <h2 className="mobile-home__headline">Everything you need for the flight line.</h2>
          <p className="mobile-home__lede">
            Designed for one-handed use. Big tap targets, clear actions, and instant access to the jobs you run
            most.
          </p>
        </div>
        <div className="mobile-home__pill">
          <span className="mobile-home__pill-label">On duty</span>
          <span className="mobile-home__pill-value">{user?.full_name || user?.username || 'You'}</span>
        </div>
      </section>

      <section className="mobile-home__section">
        <div className="mobile-home__section-header">
          <h3>Quick actions</h3>
          <p>One-tap entry to the flows techs use most.</p>
        </div>
        <div className="mobile-home__grid">
          {quickActions.map((action) => (
            <button
              key={action.title}
              type="button"
              className={`mobile-home__card ${action.accent}`}
              onClick={action.onClick}
            >
              <div className="mobile-home__card-icon" aria-hidden>
                {action.icon}
              </div>
              <div>
                <p className="mobile-home__card-title">{action.title}</p>
                <p className="mobile-home__card-copy">{action.description}</p>
              </div>
            </button>
          ))}
        </div>
      </section>

      <section className="mobile-home__section">
        <div className="mobile-home__section-header">
          <h3>More shortcuts</h3>
          <p>Stay productive without hunting through menus.</p>
        </div>
        <div className="mobile-home__list">
          {secondaryShortcuts.map((shortcut) => (
            <button
              key={shortcut.title}
              type="button"
              className="mobile-home__list-item"
              onClick={shortcut.onClick}
            >
              <div className="mobile-home__list-icon" aria-hidden>
                {shortcut.icon}
              </div>
              <div className="mobile-home__list-copy">
                <p className="mobile-home__list-title">{shortcut.title}</p>
                <p className="mobile-home__list-description">{shortcut.description}</p>
              </div>
              <span className="mobile-home__chevron" aria-hidden>
                →
              </span>
            </button>
          ))}
        </div>
      </section>
    </div>
  );
};

export default MobileHomePage;
