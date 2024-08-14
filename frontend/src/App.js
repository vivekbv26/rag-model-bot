import React from 'react';
import Chat from './Chat';
import Tabs from './Tabs';
import Footer from './Footer';
import "../src/App.css"
function App() {
  return (
    
    <div className="app">
      <div className='appWrapper'>
        
<div className='innerWrapper'>

      <header className="header">
        <img src= "./image.png" alt="Flexera Logo" className="logo" />
        <img src="./bot.png" alt="Bot Logo" className="botlogo" />
      </header>
      <Tabs />
      <Chat />
      <Footer />
        
</div>
    </div>
    </div>
  );
}

export default App;