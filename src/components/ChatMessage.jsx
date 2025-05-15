function ChatMessage({ message }) {
    return (
      <div className={`message ${message.sender === 'user' ? 'sent' : 'received'}`}>
        <div className="message-content">
          <p>{message.text}</p>
          <span className="timestamp">{message.timestamp}</span>
        </div>
      </div>
    );
  }
  
  export default ChatMessage;