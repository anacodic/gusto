import React from 'react';
import './ChatBar.css';

function ChatBar({ messages, loading }) {
  // Show only recent messages in chat bar (last 3)
  const recentMessages = messages.slice(-3);

  return (
    <div className="chat-bar">
      <div className="chat-bar-title">💬 Chat Bar</div>
      <div className="chat-messages">
        {recentMessages.length === 0 && (
          <div className="chat-message bot-message">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              "Hi! What are you craving today?"
            </div>
          </div>
        )}
        {recentMessages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.role}-message`}>
            <div className="message-avatar">
              {msg.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              {msg.role === 'user' ? `"${msg.text}"` : `"${msg.text}"`}
            </div>
          </div>
        ))}
        {loading && (
          <div className="chat-message bot-message">
            <div className="message-avatar">🤖</div>
            <div className="message-content loading">
              <span className="typing-dots">...</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatBar;
