import React from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';

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
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: white;
  padding: 2rem;
`;

const Title = styled.h1`
  font-size: 3.5rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
  animation: ${fadeIn} 1s ease-out;
  text-align: center;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;

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
  color: #e0e0e0;
`;

const StartButton = styled.button`
  padding: 1rem 2.5rem;
  font-size: 1.2rem;
  font-weight: 600;
  border: none;
  border-radius: 50px;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  animation: ${fadeIn} 1s ease-out 0.6s both;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
  }
`;

const WelcomePage: React.FC = () => {
  return (
    <Container>
      <Title>Welcome to Learning.AI</Title>
      <Subtitle>
        Embark on an innovative learning journey where artificial intelligence meets education.
        Discover a new way of learning that adapts to your unique needs.
      </Subtitle>
      <StartButton>Start Learning</StartButton>
    </Container>
  );
};

export default WelcomePage; 