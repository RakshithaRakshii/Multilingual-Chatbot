import { useState } from 'react';

function LanguageSelector({ language, setLanguage }) {
  const [isOpen, setIsOpen] = useState(false);
  
  const languages = [
    { code: 'english', name: 'English' },
    { code: 'tamil', name: 'தமிழ்' },
    { code: 'telugu', name: 'తెలుగు' },
    { code: 'hindi', name: 'हिंदी' },
    { code: 'malayalam', name: 'മലയാളം' }
  ];

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  const selectLanguage = (langCode) => {
    setLanguage(langCode);
    setIsOpen(false);
  };

  const getCurrentLanguageName = () => {
    const currentLang = languages.find(lang => lang.code === language);
    return currentLang ? currentLang.name : 'English';
  };

  return (
    <div className="language-selector">
      <button onClick={toggleDropdown} className="language-button">
        {getCurrentLanguageName()}
        <span className="dropdown-icon">▼</span>
      </button>
      
      {isOpen && (
        <div className="language-dropdown">
          {languages.map((lang) => (
            <div 
              key={lang.code} 
              className={`language-option ${language === lang.code ? 'active' : ''}`}
              onClick={() => selectLanguage(lang.code)}
            >
              {lang.name}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default LanguageSelector;
