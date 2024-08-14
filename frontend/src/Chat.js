

import React, { useState } from 'react';
import styled from 'styled-components';

const ChatContainer = styled.div`
  width: 100%;
  max-width: 600px;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin-bottom: 20px;
`;

const ChatBox = styled.div`
  flex-grow: 1;
  padding: 10px;
  overflow-y: auto;
  border-bottom: 1px solid #ddd;
  max-height: 500px;
`;

const Message = styled.div`
  margin: 10px 0;
  padding: 10px;
  border-radius: 5px;
  max-width: 80%;
  word-wrap: break-word;
  align-self: ${props => (props.type === 'user-message' ? 'flex-end' : 'flex-start')};
  background-color: ${props => (props.type === 'user-message' ? '#007bff' : '#e5e5ea')};
  color: ${props => (props.type === 'user-message' ? 'white' : 'black')};
`;

const InputContainer = styled.div`
  display: flex;
  padding: 10px;
  border-top: 1px solid #ddd;
  background-color: white;
`;

const InputField = styled.input`
  flex-grow: 1;
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 10px;
  font-size: 16px;
`;

const SendButton = styled.button`
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 10px 15px;
  cursor: pointer;
  margin-left: 10px;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: #0056b3;
  }
`;

function Chat() {
  const [messages, setMessages] = useState([{ text: 'Hello! How can I assist you today?', type: 'bot-message' }]);
  const [input, setInput] = useState('');

  const handleSend = async () => {
    if (input.trim()) {
      setMessages([...messages, { text: input, type: 'user-message' }]);
      setInput('');

      try {
        // Fetch response from the Flask backend
        const response = await fetch('http://localhost:5000/get-response', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: input }),
        });
        const data = await response.json();
        setMessages([...messages, { text: input, type: 'user-message' }, { text: data.response, type: 'bot-message' }]);
      } catch (error) {
        console.error('Error:', error);
        setMessages([...messages, { text: "Sorry, there was an error. Please try again later.", type: 'bot-message' }]);
      }
    }
  };

  return (
    <ChatContainer>
      <ChatBox>
        {messages.map((msg, index) => (
          <Message key={index} type={msg.type}>
            {msg.text}
          </Message>
        ))}
      </ChatBox>
      <InputContainer>
        <InputField
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Please type your question here..."
        />
        <SendButton onClick={handleSend}>Send</SendButton>
      </InputContainer>
    </ChatContainer>
  );
}

export default Chat;

