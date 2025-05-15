import { useState, useEffect } from 'react';
import SuggestionBar from './SuggestionBar';

function ChatInput({ onSendMessage, language, setLanguage }) {
  const [message, setMessage] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  useEffect(() => {
    // Fetch suggestions when user types
    const fetchSuggestions = async () => {
      if (message.trim().length > 0) {
        try {
          const response = await fetch('http://127.0.0.1:5000/suggest', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
              current_text: message,
              language: language 
            }),
          });
          
          const data = await response.json();
          setSuggestions(data.suggestions || []);
          setShowSuggestions(data.suggestions && data.suggestions.length > 0);
        } catch (error) {
          console.error('Error fetching suggestions:', error);
          setSuggestions([]);
          setShowSuggestions(false);
        }
      } else {
        setSuggestions([]);
        setShowSuggestions(false);
      }
    };

    // Add debounce to avoid too many requests
    const debounceTimer = setTimeout(() => {
      fetchSuggestions();
    }, 300);

    return () => clearTimeout(debounceTimer);
  }, [message, language]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setMessage(suggestion);
    setSuggestions([]);
    setShowSuggestions(false);
  };

  return (
    <div className="chat-input-container">
      <div className="chat-input">
        <form onSubmit={handleSubmit}>
          <div className="input-with-suggestions">
            <SuggestionBar 
              suggestions={suggestions} 
              onSuggestionClick={handleSuggestionClick} 
              isVisible={showSuggestions}
            />
            <input
              type="text"
              placeholder="Type a message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
          </div>
          <button type="submit" className="send-button">
            <svg viewBox="0 0 24 24" width="24" height="24">
              <path
                fill="currentColor"
                d="M1.101 21.757L23.8 12.028 1.101 2.3l.011 7.912 13.623 1.816-13.623 1.817-.011 7.912z"
              ></path>
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatInput;