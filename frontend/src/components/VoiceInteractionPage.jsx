import React, { useState, useEffect } from 'react';
import styled from '@emotion/styled';
import { useNavigate } from 'react-router-dom';
import { IoExitOutline, IoMicOutline, IoMicOffOutline } from 'react-icons/io5';
import { keyframes } from '@emotion/react';

const PageContainer = styled.div`
  min-height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: linear-gradient(135deg, rgba(26, 26, 46, 0.75) 0%, rgba(22, 33, 62, 0.75) 100%);
  color: white;
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  overflow-y: auto;
  
  /* Customize scrollbar */
  &::-webkit-scrollbar {
    width: 10px;
  }

  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 5px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.5);
  }

  &::before {
    content: '';
    position: fixed;
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

const BackButton = styled.button`
  position: absolute;
  top: 2rem;
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

const ContentWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  gap: 2rem;
  padding: 2rem;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  margin-top: 4rem;
  margin-bottom: 4rem;
`;

const TeacherSection = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const TeacherImage = styled.div`
  width: 250px;
  height: 500px;
  border-radius: 15px;
  margin-bottom: 2rem;
  background-image: url('/teacher-avatar.png');
  background-size: cover;
  background-position: center;
  transition: all 0.3s ease;
`;

const TeacherImageListening = styled(TeacherImage)`
  background-image: url('/teacher-listening.png');
  transform: scale(1.05);
  filter: brightness(1.1);
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

const VoiceContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  padding: 2rem;
  background: rgba(26, 26, 46, 0.85);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  width: calc(100% - 4rem);
  max-width: 1000px;
  margin: 0 2rem;
`;

const VoiceButton = styled.button`
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: none;
  background: ${props => props.isListening ? 
    'linear-gradient(90deg, #ff9966 0%, #ff5e62 100%)' : 
    'linear-gradient(90deg, #4facfe 0%, #00f2fe 100%)'};
  color: white;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    transform: scale(1.05);
    box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
  }

  svg {
    font-size: 2.5rem;
  }
`;

const StatusText = styled.p`
  font-size: 1.2rem;
  color: ${props => props.isListening ? '#ff9966' : '#4facfe'};
  text-align: center;
`;

const ResponseContainer = styled.div`
  width: 100%;
  min-height: 200px;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  margin-top: 1rem;
  word-wrap: break-word;
  overflow-wrap: break-word;
`;

const VoiceInteractionPage = () => {
  const navigate = useNavigate();
  const [isListening, setIsListening] = useState(false);
  const [response, setResponse] = useState('');

  const handleBack = () => {
    navigate('/main-classroom');
  };

  const toggleListening = async () => {
    if (!isListening) {
      // Start voice recognition
      try {
        const recognition = new window.webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        
        recognition.onresult = async (event) => {
          const transcript = Array.from(event.results)
            .map(result => result[0].transcript)
            .join('');
          
          // Send transcript to OpenAI API
          try {
            const response = await fetch('http://localhost:8000/api/voice-interaction', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ transcript }),
            });
            
            const data = await response.json();
            setResponse(data.response);
          } catch (error) {
            console.error('Error sending to OpenAI:', error);
          }
        };

        recognition.start();
        setIsListening(true);
      } catch (error) {
        console.error('Error starting voice recognition:', error);
      }
    } else {
      // Stop voice recognition
      const recognition = new window.webkitSpeechRecognition();
      recognition.stop();
      setIsListening(false);
    }
  };

  return (
    <PageContainer>
      <BackButton onClick={handleBack}>
        <IoExitOutline /> Back to UI Mode
      </BackButton>
      <ContentWrapper>
        <TeacherSection>
          {isListening ? (
            <TeacherImageListening />
          ) : (
            <TeacherImage />
          )}
          <TeacherInfoContainer>
            <TeacherName>Miss Wood</TeacherName>
            <TeacherRole>Virtual Teacher</TeacherRole>
          </TeacherInfoContainer>
        </TeacherSection>
        <VoiceContainer>
          <VoiceButton 
            onClick={toggleListening}
            isListening={isListening}
          >
            {isListening ? <IoMicOffOutline /> : <IoMicOutline />}
          </VoiceButton>
          <StatusText isListening={isListening}>
            {isListening ? 'Listening...' : 'Click to start speaking'}
          </StatusText>
          <ResponseContainer>
            {response}
          </ResponseContainer>
        </VoiceContainer>
      </ContentWrapper>
    </PageContainer>
  );
};

export default VoiceInteractionPage; 