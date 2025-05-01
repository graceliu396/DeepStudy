import React, { useState, useEffect, useRef } from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';
import { useNavigate } from 'react-router-dom';
import { IoExitOutline, IoHeadsetOutline } from 'react-icons/io5';
import { createTeachingWebSocket, exitSession, getLessonSummary, startNextLesson } from '../utils/api';

// Blinking cursor animation
const blink = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
`;

const PageContainer = styled.div`
  min-height: 100vh;
  width: 100vw;
  display: flex;
  background: linear-gradient(135deg, rgba(26, 26, 46, 0.75) 0%, rgba(22, 33, 62, 0.75) 100%);
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
    background-image: url('/classroom-bg.jpg');
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
  gap: 2rem;
  z-index: 1;
  overflow: hidden;
`;

const CharacterSection = styled.div`
  flex: 0.5;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  // background: rgba(26, 26, 46, 0.85);
  border-radius: 20px;
  backdrop-filter: blur(5px);
  padding: 2rem;
  // box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
`;

const ChatSection = styled.div`
  flex: 1;
  height: 100%;
  background: rgba(26, 26, 46, 0.65);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  overflow: hidden;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  display: flex;
  flex-direction: column;
`;

const ChatMessages = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: calc(100% - 80px); // Account for the input area height
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

const SummaryMessage = styled(Message)`
  max-width: 90%;
  color: #e6f0ff;
  line-height: 1.6;
  font-family: 'Consolas', monospace;
  white-space: pre-wrap;
  position: relative;

  /* For typewriter effect */
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

const TeacherImage = styled.div`
  width: 300px;
  height: 600px;
  border-radius: 15px;
  margin-bottom: 2rem;
  background-image: url('/teacher-avatar.png');
  background-size: cover;
  background-position: center;
  
`;

const TeacherInfoContainer = styled.div`
  background: rgba(26, 26, 46, 0.7);
  padding: 1.5rem 2rem;
  border-radius: 15px;
  backdrop-filter: blur(5px);
  text-align: center;
`;

const TeacherName = styled.h2`
  font-size: 2rem;
  color: #4facfe;
  margin-bottom: 1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
`;

const TeacherRole = styled.h3`
  font-size: 1.2rem;
  color: #ff9966;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
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

// Add a more noticeable immersive mode button
const ImmersiveModeCTA = styled.button`
  padding: 0.8rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  border-radius: 25px;
  background: linear-gradient(90deg, #ff9966 0%, #ff5e62 100%);
  color: white;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(255, 94, 98, 0.4);
  }

  svg {
    font-size: 1.2rem;
  }
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

const TypewriterEffect = ({ text }) => {
  const [displayText, setDisplayText] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  const textSpeed = 10; // milliseconds per character

  useEffect(() => {
    let i = 0;
    const typingInterval = setInterval(() => {
      if (i < text.length) {
        setDisplayText(text.substring(0, i + 1));
        i++;
      } else {
        clearInterval(typingInterval);
        setIsComplete(true);
      }
    }, textSpeed);

    return () => clearInterval(typingInterval);
  }, [text]);

  return (
    <SummaryMessage isUser={false} isTyping={!isComplete}>
      {displayText}
    </SummaryMessage>
  );
};

const MainClassroomPage = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Welcome to class! I'm preparing your personalized lesson...",
      isUser: false
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [teacherImageUrl, setTeacherImageUrl] = useState('/teacher-avatar.png');
  const [sessionId, setSessionId] = useState(null);
  const [lessonIndex, setLessonIndex] = useState(0);
  const [lessonComplete, setLessonComplete] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [lessonSummary, setLessonSummary] = useState('');
  const [socket, setSocket] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, showSummary]);

  // Initialize WebSocket connection when component mounts
  useEffect(() => {
    // Retrieve session data from localStorage
    const storedSessionId = localStorage.getItem('sessionId');
    const storedLessonIndex = localStorage.getItem('lessonIndex');
    
    if (storedSessionId && storedLessonIndex) {
      setSessionId(storedSessionId);
      setLessonIndex(parseInt(storedLessonIndex, 10));
      
      // Create WebSocket connection
      const newSocket = createTeachingWebSocket(
        storedSessionId,
        storedLessonIndex,
        handleSocketMessage,
        handleSocketError
      );
      
      setSocket(newSocket);
      
      // Send initial message to start the teaching session
      setTimeout(() => {
        if (newSocket.readyState === WebSocket.OPEN) {
          newSocket.send(JSON.stringify({ action: 'start_teaching' }));
        }
      }, 1000);
    } else {
      setError('No active session found. Please start a new session from the introduction page.');
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
      
      // Update teacher image if provided
      if (data.image_url) {
        setTeacherImageUrl(data.image_url);
      }
      
      // Check if this is a completion message
      if (data.text.includes('lesson completed') || data.text.includes('completed the lesson')) {
        setLessonComplete(true);
        fetchLessonSummary();
      }
    }
  };
  
  const handleSocketError = (error) => {
    console.error('WebSocket error:', error);
    setError('Connection error. Please try refreshing the page.');
  };
  
  const fetchLessonSummary = async () => {
    try {
      setIsLoading(true);
      const summaryData = await getLessonSummary(sessionId, lessonIndex);
      setLessonSummary(summaryData.report);
      setShowSummary(true);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching lesson summary:', error);
      setError('Failed to fetch lesson summary');
      setIsLoading(false);
    }
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

  const handleImmersiveMode = () => {
    navigate('/voice-interaction');
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
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  const handleStartNextLesson = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const fileId = localStorage.getItem('fileId');
      if (!fileId) {
        throw new Error('File ID not found. Please upload a lesson plan again.');
      }
      
      // Call the API to prepare the next lesson
      const response = await startNextLesson(sessionId, fileId);
      
      // Update lesson index in localStorage
      const newLessonIndex = response.lesson_index;
      localStorage.setItem('lessonIndex', newLessonIndex);
      setLessonIndex(newLessonIndex);
      
      // Close current socket
      if (socket) {
        socket.close();
      }
      
      // Create new socket for the next lesson
      const newSocket = createTeachingWebSocket(
        sessionId,
        newLessonIndex,
        handleSocketMessage,
        handleSocketError
      );
      
      setSocket(newSocket);
      
      // Reset UI state
      setMessages([{
        id: Date.now(),
        text: `Welcome to Lesson ${parseInt(newLessonIndex) + 1}! I'm preparing your personalized content...`,
        isUser: false
      }]);
      setLessonComplete(false);
      setShowSummary(false);
      
      // Send initial message to start the teaching session
      setTimeout(() => {
        if (newSocket.readyState === WebSocket.OPEN) {
          newSocket.send(JSON.stringify({ action: 'start_teaching' }));
        }
      }, 1000);
      
      setIsLoading(false);
    } catch (error) {
      console.error('Error starting next lesson:', error);
      setError('Failed to start the next lesson. Please try again.');
      setIsLoading(false);
    }
  };

  return (
    <PageContainer>
      <QuitButton onClick={handleQuit}>
        <IoExitOutline /> Exit Classroom
      </QuitButton>
      <ContentContainer>
        <CharacterSection>
          <TeacherImage style={{ backgroundImage: `url(${teacherImageUrl})` }} />
          <TeacherInfoContainer>
            <TeacherName>Miss Wood</TeacherName>
            <TeacherRole>Virtual Teacher</TeacherRole>
          </TeacherInfoContainer>
          <ImmersiveModeCTA onClick={handleImmersiveMode}>
            <IoHeadsetOutline /> Immersive Mode
          </ImmersiveModeCTA>
        </CharacterSection>
        <ChatSection>
          <ChatMessages>
            {messages.map(message => (
              <TypewriterMessage 
                key={message.id} 
                message={message} 
                isUser={message.isUser} 
              />
            ))}
            {showSummary && <TypewriterEffect text={lessonSummary} />}
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
              placeholder="Type your message..."
              disabled={!socket || socket.readyState !== WebSocket.OPEN || lessonComplete}
            />
            <SendButton 
              onClick={handleSendMessage}
              disabled={!socket || socket.readyState !== WebSocket.OPEN || lessonComplete}
            >
              Send
            </SendButton>
            {lessonComplete && (
              <SendButton 
                onClick={handleStartNextLesson}
                style={{ 
                  background: 'linear-gradient(90deg, #FF9966 0%, #FF5E62 100%)',
                  marginLeft: '0.5rem'
                }}
              >
                Next Lesson
              </SendButton>
            )}
          </ChatInput>
        </ChatSection>
      </ContentContainer>
    </PageContainer>
  );
};

export default MainClassroomPage;