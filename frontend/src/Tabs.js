

import React, { useState } from 'react';

function Tabs() {
  const [activeTab, setActiveTab] = useState('Flexhack'); // Set the default active tab

  const handleClick = (tabName) => {
    setActiveTab(tabName); // Update the active tab when a tab is clicked
  };

  const tabContainerStyle = {
    display: 'flex',
    justifyContent: 'center',
    margin: '20px 0',
  };

  const tabStyle = {
    padding: '10px 20px',
    margin: '0 5px',
    border: '1px solid #ddd',
    borderRadius: '5px',
    cursor: 'pointer',
    backgroundColor: '#f8f9fa',
    color: '#333',
    transition: 'background-color 0.3s, color 0.3s',
  };

  const activeTabStyle = {
    backgroundColor: '#007bff', // Blue background for active tab
    color: 'white',
  };

  return (
    <div className="tabs-container" style={tabContainerStyle}>
      <div
        className="tab"
        style={activeTab === 'Flexhack' ? { ...tabStyle, ...activeTabStyle } : tabStyle}
        onClick={() => handleClick('Flexhack')}
      >
        Flexhack
      </div>
      <div
        className="tab"
        style={activeTab === 'Flexera' ? { ...tabStyle, ...activeTabStyle } : tabStyle}
        onClick={() => handleClick('Flexera')}
      >
        Flexera
      </div>
      <div
        className="tab"
        style={activeTab === 'Gemini' ? { ...tabStyle, ...activeTabStyle } : tabStyle}
        onClick={() => handleClick('Gemini')}
      >
        Gemini
      </div>
    </div>
  );
}

export default Tabs;

