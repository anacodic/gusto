// Enhanced Chat page - uses existing ChatInterface
import ChatInterface from '../components/chat/ChatInterface';
import './Chat.css';

function Chat() {
  return (
    <div className="chat-page">
      <div className="chat-header">
        <h1>💬 Chat - Restaurant Recommendations</h1>
      </div>
      <ChatInterface />
    </div>
  );
}

export default Chat;
