import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../utils/api';
import './Groups.css';

function Groups() {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newGroup, setNewGroup] = useState({ name: '', budget: '', location: '' });

  useEffect(() => {
    loadGroups();
  }, []);

  const loadGroups = async () => {
    try {
      const response = await api.get('/api/groups');
      setGroups(response.data.groups || []);
    } catch (error) {
      console.error('Error loading groups:', error);
    } finally {
      setLoading(false);
    }
  };

  const createGroup = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/groups', newGroup);
      setShowCreate(false);
      setNewGroup({ name: '', budget: '', location: '' });
      loadGroups();
    } catch (error) {
      console.error('Error creating group:', error);
      alert('Error creating group');
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="groups-page">
      <div className="groups-header">
        <h1>👥 Groups</h1>
        <button onClick={() => setShowCreate(!showCreate)} className="create-btn">
          + Create Group
        </button>
      </div>

      {showCreate && (
        <div className="create-group-form">
          <h2>Create Group</h2>
          <form onSubmit={createGroup}>
            <input
              type="text"
              placeholder="Group Name"
              value={newGroup.name}
              onChange={(e) => setNewGroup({ ...newGroup, name: e.target.value })}
              required
            />
            <input
              type="number"
              placeholder="Budget per person ($)"
              value={newGroup.budget}
              onChange={(e) => setNewGroup({ ...newGroup, budget: e.target.value })}
            />
            <input
              type="text"
              placeholder="Location"
              value={newGroup.location}
              onChange={(e) => setNewGroup({ ...newGroup, location: e.target.value })}
            />
            <div className="form-actions">
              <button type="submit">Save Group</button>
              <button type="button" onClick={() => setShowCreate(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="groups-grid">
        {groups.map((group) => (
          <Link
            key={group.id}
            to={`/groups/${group.id}/recommendations`}
            className="group-card"
          >
            <div className="group-name">{group.name}</div>
            <div className="group-info">
              <span>{group.member_count} members</span>
              {group.budget && <span>💰 ${group.budget}/person</span>}
            </div>
          </Link>
        ))}
      </div>

      {groups.length === 0 && (
        <div className="empty-state">
          <p>No groups yet. Create one to get group recommendations!</p>
        </div>
      )}
    </div>
  );
}

export default Groups;
