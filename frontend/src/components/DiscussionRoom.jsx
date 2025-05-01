import React, { useState, useRef, useEffect } from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';
import { useNavigate } from 'react-router-dom';
import { IoExitOutline } from 'react-icons/io5';
import { createDiscussionWebSocket, exitSession } from '../utils/api';

const PageContainer = styled.div`
  min-height: 100vh;
  width: 100vw;
  display: flex;
  background: linear-gradient(135deg, rgba(26, 26, 46, 0.2) 0%, rgba(22, 33, 62, 0.75) 100%);
  color: white;
  position: fixed;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: url('/discussion-room-bg.png');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    z-index: -1;
    opacity: 0.9;
    filter: contrast(1.1) brightness(1.1);
  }
`;

const ContentContainer = styled.div`
  display: flex;
  width: 100%;
  height: 100%;
  padding: 2rem;
  padding-top: 110px;
  padding-bottom: 40px;
  gap: 2rem;
  z-index: 1;
`;

const CharactersSection = styled.div`
  flex: 0.8;
  display: flex;
  flex-direction: row;
  gap: 2rem;
  justify-content: center;
  align-items: center;
  padding: 1rem;
`;

const CharacterCard = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  background: rgba(26, 26, 46, 0);
  border-radius: 20px;
  padding: 1.5rem;
  transition: transform 0.2s ease;

  &:hover {
    transform: translateY(-10px);
  }
`;

const CharacterImage = styled.div`
  width: 180px;
  height: 250px;
  border-radius: 15px;
  background-image: url(${props => props.image});
  background-size: cover;
  background-position: center;
`;

const CharacterInfo = styled.div`
  text-align: center;
  background: rgba(26, 26, 46, 0.7);
  padding: 1rem;
  border-radius: 15px;
  backdrop-filter: blur(5px);
  width: 100%;
`;

const CharacterName = styled.div`
  font-size: 1.5rem;
  color: #4facfe;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
`;

const FirstName = styled.span`
  font-weight: bold;
`;

const LastName = styled.span`
  font-weight: bold;
`;

const CharacterRole = styled.h3`
  font-size: 1rem;
  color: #ff9966;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
`;

const ChatSection = styled.div`
  flex: 1;
  background: rgba(26, 26, 46, 0.65);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  overflow: hidden;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  display: flex;
  flex-direction: column;
`;

const QuitButton = styled.button`
  position: absolute;
  top: 110px;
  left: 2rem;
  padding: 0.8rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  border-radius: 25px;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
  }

  svg {
    font-size: 1.2rem;
  }
`;

const classmates = [
  {
    firstName: "Alex",
    lastName: "Chen",
    role: "Group Leader",
    image: "/classmate1-avatar.png"
  },
  {
    firstName: "Sarah",
    lastName: "Johnson",
    role: "Note Taker",
    image: "/classmate2-avatar.png"
  },
  {
    firstName: "Michael",
    lastName: "Rodriguez",
    role: "Time Keeper",
    image: "/classmate3-avatar.png"
  }
];

const ChatMessages = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: calc(100% - 80px);
`;

// Blinking cursor animation
const blink = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
`;

const Message = styled.div`
  max-width: 80%;
  padding: 1rem;
  border-radius: 15px;
  background: ${props => props.isUser ? 'rgba(79, 172, 254, 0.2)' : 'rgba(255, 255, 255, 0.1)'};
  align-self: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  color: #e6f0ff;
  text-align: ${props => props.isUser ? 'right' : 'left'};
  position: relative;

  /* Blinking cursor for messages being typed */
  ${props => props.isTyping && `
    &::after {
      content: '|';
      display: inline-block;
      margin-left: 2px;
      animation: ${blink} 1s infinite;
      position: absolute;
    }
  `}
`;

const TypewriterMessage = ({ message, isUser }) => {
  const [displayText, setDisplayText] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  const fullText = message.text;
  const textSpeed = 25; // milliseconds per character

  useEffect(() => {
    // If user message, show immediately
    if (isUser) {
      setDisplayText(fullText);
      setIsComplete(true);
      return;
    }

    // For AI messages, use typewriter effect
    let i = 0;
    const typingInterval = setInterval(() => {
      if (i < fullText.length) {
        setDisplayText(fullText.substring(0, i + 1));
        i++;
      } else {
        clearInterval(typingInterval);
        setIsComplete(true);
      }
    }, textSpeed);

    return () => clearInterval(typingInterval);
  }, [fullText, isUser]);

  return (
    <Message isUser={isUser} isTyping={!isComplete && !isUser}>
      {displayText}
    </Message>
  );
};

const ChatInput = styled.div`
  padding: 1rem;
  background: rgba(26, 26, 46, 0.95);
  display: flex;
  gap: 1rem;
  align-items: center;
`;

const Input = styled.input`
  flex: 1;
  padding: 0.8rem 1rem;
  border: none;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.1);
  color: #e6f0ff;
  font-size: 1rem;

  &:focus {
    outline: none;
    background: rgba(255, 255, 255, 0.15);
  }
`;

const SendButton = styled.button`
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 15px;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
  }
`;

// Remove the floating StartQuizButton styled component
// Instead, style a button specifically for the chat area
const ChatQuizButton = styled.button`
  width: 100%;
  padding: 1rem;
  margin-top: 1rem;
  font-size: 1.1rem;
  font-weight: 600;
  border: none;
  border-radius: 15px;
  background: linear-gradient(90deg, #FF9966 0%, #FF5E62 100%);
  color: white;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  text-align: center;
  box-shadow: 0 5px 15px rgba(255, 94, 98, 0.3);

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(255, 94, 98, 0.4);
  }

  &:active {
    transform: translateY(-1px);
  }
`;

const DiscussionRoom = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [lessonIndex, setLessonIndex] = useState(0);
  const [socket, setSocket] = useState(null);
  const [waitingForUserInput, setWaitingForUserInput] = useState(false);
  const [discussionCompleted, setDiscussionCompleted] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Initialize WebSocket connection when component mounts
  useEffect(() => {
    // Retrieve session data from localStorage
    const storedSessionId = localStorage.getItem('sessionId');
    const storedLessonIndex = localStorage.getItem('lessonIndex');
    
    if (storedSessionId && storedLessonIndex) {
      setSessionId(storedSessionId);
      setLessonIndex(parseInt(storedLessonIndex, 10));
      
      // Create WebSocket connection
      const newSocket = createDiscussionWebSocket(
        storedSessionId,
        storedLessonIndex,
        handleSocketMessage,
        handleSocketError
      );
      
      setSocket(newSocket);
      
      // Send initial welcome message
      setMessages([{
        id: Date.now(),
        text: "Welcome to the group discussion! Your classmates will join in shortly. Say 'Hi everyone!' to start.",
        isUser: false
      }]);
    } else {
      setError('No active session found. Please start a new session from the introduction page.');
      setMessages([{
        id: Date.now(),
        text: "Error: No active session found. Please start a new session from the introduction page.",
        isUser: false
      }]);
    }
    
    // Clean up function
    return () => {
      if (socket) {
        socket.close();
      }
    };
  }, []);

  const handleSocketMessage = (data) => {
    if (data.type === 'message') {
      const newMessage = {
        id: Date.now(),
        text: data.text,
        isUser: false
      };
      
      setMessages(prev => [...prev, newMessage]);
      
      // Check if the message indicates waiting for user input
      if (data.text.includes('?') || data.text.includes('What do you think')) {
        setWaitingForUserInput(true);
      }
      
      // Check if this is a completion message
      if (data.text.includes('discussion completed') || data.text.includes('Great job everyone')) {
        setDiscussionCompleted(true);
        setWaitingForUserInput(false);
      }
    }
  };
  
  const handleSocketError = (error) => {
    console.error('WebSocket error:', error);
    setError('Connection error. Please try refreshing the page.');
  };

  const handleQuit = async () => {
    if (sessionId) {
      try {
        await exitSession(sessionId);
      } catch (error) {
        console.error('Error ending session:', error);
      }
    }
    navigate('/introduction');
  };
  
  const handleSendMessage = () => {
    if (inputMessage.trim() && socket && socket.readyState === WebSocket.OPEN) {
      // Add user message to chat
      const newMessage = {
        id: Date.now(),
        text: inputMessage,
        isUser: true
      };
      setMessages(prev => [...prev, newMessage]);
      
      // Send message to server through WebSocket
      socket.send(inputMessage);
      setInputMessage('');
      
      // Reset waiting state as user has responded
      setWaitingForUserInput(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  const handleStartQuiz = () => {
    navigate('/quiz');
  };

  return (
    <PageContainer>
      <QuitButton onClick={handleQuit}>
        <IoExitOutline /> Exit Discussion
      </QuitButton>
      <ContentContainer>
        <CharactersSection>
          {classmates.map((classmate, index) => (
            <CharacterCard key={index}>
              <CharacterImage image={classmate.image} />
              <CharacterInfo>
                <CharacterName>
                  <FirstName>{classmate.firstName}</FirstName>
                  <LastName>{classmate.lastName}</LastName>
                </CharacterName>
                <CharacterRole>{classmate.role}</CharacterRole>
              </CharacterInfo>
            </CharacterCard>
          ))}
        </CharactersSection>
        <ChatSection>
          <ChatMessages>
            {messages.map(message => (
              <TypewriterMessage 
                key={message.id} 
                message={message} 
                isUser={message.isUser} 
              />
            ))}
            {error && (
              <Message isUser={false}>
                <div style={{ color: '#ff5e62' }}>{error}</div>
              </Message>
            )}
            <div ref={messagesEndRef} />
          </ChatMessages>
          <ChatInput>
            <Input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={waitingForUserInput ? "Your turn to respond..." : "Type your message..."}
              disabled={!socket || socket.readyState !== WebSocket.OPEN}
            />
            <SendButton 
              onClick={handleSendMessage}
              disabled={!socket || socket.readyState !== WebSocket.OPEN}
            >
              Send
            </SendButton>
          </ChatInput>
          {discussionCompleted && (
            <ChatQuizButton onClick={handleStartQuiz}>
              Start Quiz
            </ChatQuizButton>
          )}
        </ChatSection>
      </ContentContainer>
    </PageContainer>
  );
};

export default DiscussionRoom; 