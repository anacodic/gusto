import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../hooks/useChat';
import StoryCard from '../components/story/StoryCard';
import ChatBar from '../components/story/ChatBar';
import ChatInput from '../components/story/ChatInput';
import './Chat.css';

function Chat() {
  const { messages, loading, sendMessage, error } = useChat();
  const [recommendations, setRecommendations] = useState([]);
  const storyRef = useRef(null);

  // Extract recommendations from messages
  useEffect(() => {
    const latestMessage = messages[messages.length - 1];
    if (latestMessage?.recommendations) {
      setRecommendations(latestMessage.recommendations);
      // Scroll to story section when recommendations arrive
      setTimeout(() => {
        storyRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 300);
    }
  }, [messages]);

  const handleSend = async (text) => {
    await sendMessage(text);
  };

  return (
    <div className="gusto-app">
      {/* Header */}
      <header className="gusto-header">
        <h1 className="gusto-title">🍽️ Gusto</h1>
      </header>

      {/* Main Content */}
      <main className="gusto-main">
        {/* Chat Bar Section */}
        <section className="chat-bar-section">
          <ChatBar messages={messages} loading={loading} />
        </section>

        {/* Story Mode Section */}
        {recommendations.length > 0 && (
          <section className="story-mode-section" ref={storyRef}>
            <div className="story-header">
              <h2>📖 Story Mode - Scroll to explore</h2>
            </div>
            <div className="story-cards">
              {recommendations.map((restaurant, index) => (
                <StoryCard
                  key={restaurant.id || restaurant.name || `restaurant-${index}`}
                  restaurant={restaurant}
                  index={index}
                />
              ))}
              <div className="scroll-indicator">
                <span>Scroll for more... ↓</span>
              </div>
            </div>
          </section>
        )}

        {/* Empty State */}
        {recommendations.length === 0 && messages.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">🌸</div>
            <p>Start a conversation to discover amazing restaurants!</p>
          </div>
        )}
      </main>

      {/* Input Bar */}
      <footer className="gusto-footer">
        <ChatInput onSend={handleSend} loading={loading} />
      </footer>
    </div>
  );
}

export default Chat;
