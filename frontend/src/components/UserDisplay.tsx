import React from 'react';
import { User, LogIn, LogOut } from 'lucide-react';
import './UserDisplay.css';

interface UserDisplayProps {
  username: string;
  isLoggedIn: boolean;
}

/**
 * UserDisplay shows the current user in the header.
 *
 * For now, displays a 'dev' user without password.
 * In future versions, this will support multi-user with login/logout.
 */
const UserDisplay: React.FC<UserDisplayProps> = ({ username, isLoggedIn }) => {
  return (
    <div className="user-display">
      <div className="user-info">
        <User size={18} />
        <span className="username">{username}</span>
        {isLoggedIn ? (
          <LogOut size={16} className="user-status-icon" aria-label="Logged in" />
        ) : (
          <LogIn
            size={16}
            className="user-status-icon user-status-icon-inactive"
            aria-label="Not logged in"
          />
        )}
      </div>
    </div>
  );
};

export default UserDisplay;
