import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';
import AuthForms from './AuthForms';

const fadeIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const Container = styled.div`
  min-height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #ff9966 0%, #ff5e62 100%);
  color: white;
  padding: 2rem;
  position: fixed;
  top: 0;
  left: 0;
  overflow-y: auto;
  max-width: 100%;
  box-sizing: border-box;
`;

const Title = styled.h1`
  font-size: 3.5rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
  animation: ${fadeIn} 1s ease-out;
  text-align: center;
  background: linear-gradient(90deg, #fff3e6 0%, #ffffff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

  @media (max-width: 768px) {
    font-size: 2.5rem;
  }
`;

const Subtitle = styled.p`
  font-size: 1.5rem;
  text-align: center;
  max-width: 600px;
  margin-bottom: 2rem;
  animation: ${fadeIn} 1s ease-out 0.3s both;
  line-height: 1.6;
  color: #fff3e6;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
`;

const StartButton = styled.button`
  padding: 1rem 2.5rem;
  font-size: 1.2rem;
  font-weight: 600;
  border: none;
  border-radius: 50px;
  background: linear-gradient(90deg, #ffffff 0%, #fff3e6 100%);
  color: #ff5e62;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  animation: ${fadeIn} 1s ease-out 0.6s both;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(255, 255, 255, 0.4);
  }
`;

const WelcomePage = () => {
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleStartLearning = () => {
    navigate('/introduction');
  };

  const handleAuthSuccess = () => {
    setIsAuthenticated(true);
  };

  return (
    <Container>
      <Title>Welcome to DeepStudy</Title>
      <Subtitle>
        Embark on an innovative learning journey where artificial intelligence meets education.
        Discover a new way of learning that adapts to your unique needs.
      </Subtitle>
      
      {!isAuthenticated ? (
        <AuthForms onAuthSuccess={handleAuthSuccess} />
      ) : (
        <StartButton onClick={handleStartLearning}>Start Learning</StartButton>
      )}
    </Container>
  );
};

export default WelcomePage; 