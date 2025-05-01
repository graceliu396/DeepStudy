import React from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';

const fadeIn = keyframes`
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
`;

const ClassroomContainer = styled.div`
  min-height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  background: linear-gradient(
    to bottom,
    #2c3e50 0%,
    #3498db 100%
  );
  color: white;
  position: fixed;
  top: 0;
  left: 0;
  overflow-y: auto;
  animation: ${fadeIn} 1s ease-out;
`;

const ClassroomContent = styled.div`
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  z-index: 1;
  width: 100%;
  height: 100vh;
`;

const ClassroomBackground = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url('/classroom-bg.jpg');
  background-size: cover;
  background-position: center;
  opacity: 0.3;
  pointer-events: none;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  margin-bottom: 1rem;
`;

const ChatContainer = styled.div`
  width: 90%;
  height: 70vh;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  border: 1px solid rgba(255, 255, 255, 0.18);
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const ChatIframe = styled.iframe`
  width: 100%;
  height: 100%;
  border: none;
  background: white;
`;

const ClassroomPage = () => {
  return (
    <ClassroomContainer>
      <ClassroomBackground />
      <ClassroomContent>
        <Title>Welcome to Your Virtual Classroom</Title>
        <ChatContainer>
          <ChatIframe
            src="http://localhost:8000" // Update this URL to your Chainlit deployment
            title="Learning AI Chat"
            allow="microphone *; camera *; display-capture *"
          />
        </ChatContainer>
      </ClassroomContent>
    </ClassroomContainer>
  );
};

export default ClassroomPage; 