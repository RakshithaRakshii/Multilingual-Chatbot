import { useState, useEffect } from 'react'
import ChatWindow from './components/ChatWindow'
import ChatHeader from './components/ChatHeader'
import ChatInput from './components/ChatInput'
import LanguageSelector from './components/LanguageSelector'
import './styles/App.css'

function App() {
  const [messages, setMessages] = useState([]);
  const [language, setLanguage] = useState('english');
  const [loading, setLoading] = useState(false);

  // Add welcome message when component mounts
  useEffect(() => {
    const welcomeMessage = {
      id: Date.now(),
      text: "Welcome to the chatbox! Type something to start a conversation.",
      sender: 'bot',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages([welcomeMessage]);
  }, []);

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    
    // Add user message
    const userMessage = {
      id: Date.now(),
      text: text,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setLoading(true);
    
    try {
      const response = await fetch('http://127.0.0.1:5000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: text,
          language: language 
        }),
      });
      
      const data = await response.json();
      
      // Add bot message
      const botMessage = {
        id: Date.now() + 1,
        text: data.response,
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      setMessages(prevMessages => [...prevMessages, botMessage]);
    } catch (error) {
      console.error('Error:', error);
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, there was an error processing your request.',
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="chat-container">
        <ChatHeader language={language} setLanguage={setLanguage} />
        <ChatWindow messages={messages} loading={loading} />
        <ChatInput onSendMessage={sendMessage} language={language} setLanguage={setLanguage} />
      </div>
    </div>
  );
}

export default App;