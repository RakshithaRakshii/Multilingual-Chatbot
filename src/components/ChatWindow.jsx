import ChatMessage from './ChatMessage';

function ChatWindow({ messages, loading }) {
  return (
    <div className="chat-window">
      <div className="messages-container">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        {loading && (
          <div className="message received">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatWindow;