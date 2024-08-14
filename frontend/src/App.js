import React from 'react';
import Chat from './Chat';
import Tabs from './Tabs';
import Footer from './Footer';

function App() {
  return (
    <div className="app">
      <header className="header">
        <img src= "./image.png" alt="Flexera Logo" className="logo" />
        <img src="./bot.png" alt="Bot Logo" className="botlogo" />
      </header>
      <Tabs />
      <Chat />
      <Footer />
    </div>
  );
}

export default App;