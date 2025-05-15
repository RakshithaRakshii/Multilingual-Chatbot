import { useState } from 'react';
import LanguageSelector from './LanguageSelector';

function ChatHeader({ language, setLanguage }) {
  return (
    <div className="chat-header">
      <div className="user-info">
        <div className="avatar">
          <img src="/ghost.png" alt="Avatar" />
        </div>
        <div className="user-name">
          <h3>Multilingual Chatbot</h3>
        </div>
      </div>
      <LanguageSelector language={language} setLanguage={setLanguage} />
    </div>
  );
}

export default ChatHeader;