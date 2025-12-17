import { useState } from 'react';
import './ChatInput.css';

function ChatInput({ onSend, disabled = false }) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Ask about restaurants, dishes, or get recommendations..."
        disabled={disabled}
        className="chat-input-field"
      />
      <button 
        type="submit" 
        disabled={disabled || !message.trim()}
        className="chat-send-button"
      >
        {disabled ? '⏳' : '📤'}
      </button>
    </form>
  );
}

export default ChatInput;
