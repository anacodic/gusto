import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../utils/api';
import RestaurantCard from '../components/restaurant/RestaurantCard';
import './GroupRecommendations.css';

function GroupRecommendations() {
  const { groupId } = useParams();
  const [groupData, setGroupData] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadGroupData();
  }, [groupId]);

  const loadGroupData = async () => {
    try {
      const response = await api.get(`/api/groups/${groupId}/recommendations`);
      setGroupData(response.data);
      
      // Get restaurant recommendations using chat endpoint with group context
      // The chat endpoint handles group taste vectors and allergies
      const location = response.data.location || 'Boston, MA';
      const chatResponse = await api.post('/api/chat', {
        query: `Find restaurants for our group in ${location}`,
        location: location,
        user_taste_vector: response.data.combined_taste,
        allergies: response.data.combined_allergies || [],
        budget: response.data.budget
      });
      
      if (chatResponse.data?.menu_buddy?.recommendations) {
        setRecommendations(chatResponse.data.menu_buddy.recommendations);
      }
    } catch (error) {
      console.error('Error loading group recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!groupData) {
    return <div>Group not found</div>;
  }

  return (
    <div className="group-recommendations-page">
      <div className="page-header">
        <Link to="/groups" className="back-link">← Back</Link>
        <h1>🍽️ Group Recommendations ({groupData.group_name})</h1>
      </div>

      <div className="group-analysis">
        <h2>📊 Group Compatibility Analysis</h2>
        <p><strong>Combined Taste:</strong> {JSON.stringify(groupData.combined_taste)}</p>
        <p><strong>Safe for:</strong> ✅ All ({groupData.combined_allergies?.length === 0 ? 'no allergies' : groupData.combined_allergies?.join(', ')})</p>
        {groupData.budget && <p><strong>Budget:</strong> ${groupData.budget}/person</p>}
      </div>

      <div className="recommendations-list">
        {recommendations.map((restaurant, index) => (
          <RestaurantCard 
            key={restaurant.id || index} 
            restaurant={restaurant}
            showGroupScores={true}
            groupMembers={groupData.members}
          />
        ))}
      </div>

      {recommendations.length === 0 && (
        <div className="empty-state">
          <p>No recommendations found. Try adjusting your group preferences.</p>
        </div>
      )}
    </div>
  );
}

export default GroupRecommendations;
