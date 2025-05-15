import { useState, useEffect } from 'react';

function SuggestionBar({ suggestions, onSuggestionClick, isVisible }) {
  if (!isVisible || suggestions.length === 0) {
    return null;
  }

  return (
    <div className="suggestion-bar">
      {suggestions.map((suggestion, index) => (
        <div 
          key={index} 
          className="suggestion-item"
          onClick={() => onSuggestionClick(suggestion)}
        >
          {suggestion}
        </div>
      ))}
    </div>
  );
}

export default SuggestionBar;