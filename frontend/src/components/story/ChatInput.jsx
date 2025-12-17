import React, { useState } from 'react';
import './ChatInput.css';

function ChatInput({ onSend, loading }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !loading) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form className="chat-input-form" onSubmit={handleSubmit}>
      <input
        type="text"
        className="chat-input"
        placeholder="Type your message..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
        disabled={loading}
      />
      <div className="input-actions">
        <button type="button" className="icon-btn" title="Attach">
          📎
        </button>
        <button type="button" className="icon-btn" title="Voice">
          🎤
        </button>
        <button 
          type="submit" 
          className="send-btn"
          disabled={!input.trim() || loading}
        >
          🚀 Send
        </button>
      </div>
    </form>
  );
}

export default ChatInput;
