import { useState, useEffect } from 'react';
import './AgentActivity.css';

function AgentActivity({ activeAgents = [], isProcessing = false }) {
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    if (activeAgents.length > 0) {
      setAgents(activeAgents);
    } else if (isProcessing) {
      setAgents(['orchestrator']);
    } else {
      setAgents([]);
    }
  }, [activeAgents, isProcessing]);

  if (agents.length === 0) {
    return null;
  }

  const agentLabels = {
    orchestrator: '🎯 Orchestrator',
    yelp_agent: '🔍 Yelp Discovery',
    flavor_agent: '👅 Taste Analysis',
    beverage_agent: '🍺 Beer Pairing',
    budget_agent: '💰 Budget Filter'
  };

  return (
    <div className="agent-activity">
      <div className="activity-header">
        <span className="activity-icon">🤖</span>
        <span>Agent Activity</span>
      </div>
      <div className="agents-list">
        {agents.map((agent, i) => (
          <div key={i} className="agent-item">
            <span className="agent-pulse">●</span>
            <span>{agentLabels[agent] || agent}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default AgentActivity;
