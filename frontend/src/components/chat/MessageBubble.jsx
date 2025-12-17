import './MessageBubble.css';

function MessageBubble({ message, isUser = false, agent = null }) {
  return (
    <div className={`message-bubble ${isUser ? 'user' : 'assistant'}`}>
      {!isUser && agent && (
        <div className="agent-badge">
          {agent === 'orchestrator' && '🎯'}
          {agent === 'yelp_agent' && '🔍'}
          {agent === 'flavor_agent' && '👅'}
          {agent === 'beverage_agent' && '🍺'}
          {agent === 'budget_agent' && '💰'}
        </div>
      )}
      <div className="message-content">
        {typeof message === 'string' ? (
          <p>{message}</p>
        ) : (
          <>
            {message.text && <p>{message.text}</p>}
            {message.recommendations && message.recommendations.length > 0 && (
              <div className="recommendations-preview">
                {message.recommendations.length} restaurant(s) found
              </div>
            )}
          </>
        )}
      </div>
      <div className="message-time">
        {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </div>
    </div>
  );
}

export default MessageBubble;
