import { useState, useEffect } from 'react';
import api from '../utils/api';
import './Friends.css';

function Friends() {
  const [friends, setFriends] = useState([]);
  const [requests, setRequests] = useState({ received: [], sent: [] });
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFriends();
    loadRequests();
  }, []);

  const loadFriends = async () => {
    try {
      const response = await api.get('/api/friends');
      setFriends(response.data.friends || []);
    } catch (error) {
      console.error('Error loading friends:', error);
    }
  };

  const loadRequests = async () => {
    try {
      const response = await api.get('/api/friends/requests');
      setRequests(response.data);
    } catch (error) {
      console.error('Error loading requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const searchUsers = async (query) => {
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }
    try {
      const response = await api.get(`/api/users/search?q=${query}`);
      setSearchResults(response.data || []);
    } catch (error) {
      console.error('Error searching users:', error);
    }
  };

  const sendFriendRequest = async (userId) => {
    try {
      await api.post('/api/friends/request', { to_user_id: userId });
      alert('Friend request sent!');
      loadRequests();
    } catch (error) {
      alert('Error sending friend request: ' + (error.response?.data?.detail || error.message));
    }
  };

  const acceptRequest = async (requestId) => {
    try {
      await api.post(`/api/friends/accept/${requestId}`);
      loadFriends();
      loadRequests();
    } catch (error) {
      alert('Error accepting request');
    }
  };

  const declineRequest = async (requestId) => {
    try {
      await api.post(`/api/friends/decline/${requestId}`);
      loadRequests();
    } catch (error) {
      alert('Error declining request');
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="friends-page">
      <div className="friends-header">
        <h1>👥 Friends & Social</h1>
        <button className="add-friend-btn">+ Add Friend</button>
      </div>

      <div className="search-section">
        <h2>🔍 Find Friends</h2>
        <input
          type="text"
          placeholder="Search by name, email, or username..."
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            searchUsers(e.target.value);
          }}
          className="search-input"
        />
        {searchResults.length > 0 && (
          <div className="search-results">
            {searchResults.map((user) => (
              <div key={user.id} className="search-result-item">
                <div>
                  <div className="user-name">{user.name}</div>
                  <div className="user-email">{user.email}</div>
                </div>
                <button onClick={() => sendFriendRequest(user.id)}>
                  Add Friend
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {requests.received.length > 0 && (
        <div className="requests-section">
          <h2>👥 Friend Requests ({requests.received.length})</h2>
          {requests.received.map((req) => (
            <div key={req.id} className="request-item">
              <div>
                <div className="user-name">{req.from_user.name}</div>
                <div className="user-email">{req.from_user.email}</div>
              </div>
              <div className="request-actions">
                <button onClick={() => acceptRequest(req.id)} className="accept-btn">
                  Accept
                </button>
                <button onClick={() => declineRequest(req.id)} className="decline-btn">
                  Decline
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="friends-section">
        <h2>👥 My Friends ({friends.length})</h2>
        {friends.length === 0 ? (
          <p className="empty-state">No friends yet. Search for users to add friends!</p>
        ) : (
          <div className="friends-list">
            {friends.map((friend) => (
              <div key={friend.id} className="friend-item">
                <div>
                  <div className="user-name">{friend.name}</div>
                  <div className="user-info">
                    Taste: {friend.taste_vector?.slice(0, 2).map(v => v > 0.5 ? 'Spicy' : 'Mild').join(', ')}
                    {friend.allergies?.length > 0 && ` | Allergies: ${friend.allergies.join(', ')}`}
                  </div>
                </div>
                <div className="friend-actions">
                  <button>Message</button>
                  <button>👥</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Friends;
