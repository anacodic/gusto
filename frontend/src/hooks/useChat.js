import { useState, useRef, useEffect } from 'react';
import api from '../utils/api';

export function useChat(userKey = 'default') {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [chatId, setChatId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (text) => {
    const userMessage = {
      role: 'user',
      text,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      const response = await api.post('/api/chat', {
        query: text,
        user_key: userKey,
        chat_id: chatId,
        max_results: 10
      });

      const assistantMessage = {
        role: 'assistant',
        text: response.data.response?.text || 'No response',
        recommendations: response.data.menu_buddy?.recommendations || [],
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      if (response.data.chat_id) {
        setChatId(response.data.chat_id);
      }
    } catch (err) {
      setError(err.message || 'Failed to send message');
      const errorMessage = {
        role: 'assistant',
        text: `Error: ${err.message}`,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setChatId(null);
  };

  return {
    messages,
    loading,
    error,
    sendMessage,
    clearChat,
    messagesEndRef
  };
}
