import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import './Navigation.css';

function Navigation() {
  const location = useLocation();
  const { user, signOut } = useAuth();
  
  const isActive = (path) => location.pathname === path;
  
  return (
    <nav className="navigation">
      <div className="nav-header">
        <Link to="/" className="logo">
          🍽️ Gusto
        </Link>
        <div className="nav-right">
          <span className="notifications">🔔</span>
          <Link to="/profile" className="profile-link">
            👤 {user?.name || 'Profile'}
          </Link>
        </div>
      </div>
      <div className="nav-tabs">
        <Link 
          to="/" 
          className={isActive('/') ? 'active' : ''}
        >
          🔍 Discover
        </Link>
        <Link 
          to="/collections" 
          className={isActive('/collections') ? 'active' : ''}
        >
          📌 Collections
        </Link>
        <Link 
          to="/chat" 
          className={isActive('/chat') ? 'active' : ''}
        >
          💬 Chat
        </Link>
        <Link 
          to="/groups" 
          className={isActive('/groups') ? 'active' : ''}
        >
          👥 Groups
        </Link>
        <Link 
          to="/profile" 
          className={isActive('/profile') ? 'active' : ''}
        >
          👤 Profile
        </Link>
        <button onClick={signOut} className="signout-btn">
          Sign Out
        </button>
      </div>
    </nav>
  );
}

export default Navigation;
