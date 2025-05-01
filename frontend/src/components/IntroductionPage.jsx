import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';
import { startSession, uploadLessonPlan, uploadMaterial } from '../utils/api';

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

const PageContainer = styled.div`
  min-height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
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
`;

const ContentWrapper = styled.div`
  width: 100%;
  max-width: 1200px;
  padding: 2rem;
  padding-top: 70px; /* Add 70px padding to the top of the content */
  margin-top: 70px; /* This accounts for the navbar that is 70px tall */
`;

const Section = styled.div`
  width: 100%;
  margin-bottom: 3rem;
`;

const SectionTitle = styled.h2`
  font-size: 2rem;
  color: #4facfe;
  text-align: center;
  margin-bottom: 2rem;
  animation: ${fadeIn} 1s ease-out;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  color: #ffffff;
  text-align: center;
  margin-bottom: 3rem;
  animation: ${fadeIn} 1s ease-out;
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
`;

const Card = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  animation: ${fadeIn} 1s ease-out;
  transition: transform 0.3s ease;
  cursor: ${props => props.clickable ? 'pointer' : 'default'};

  &:hover {
    transform: translateY(-5px);
  }
`;

const CharacterImage = styled.div`
  width: 120px;
  height: 120px;
  border-radius: 60px;
  background-color: #2a5298;
  margin-bottom: 1rem;
  overflow: hidden;
  border: 3px solid #4facfe;
`;

const RoomImage = styled.div`
  width: 200px;
  height: 120px;
  border-radius: 15px;
  background-color: #2a5298;
  margin-bottom: 1rem;
  overflow: hidden;
  border: 3px solid #4facfe;
`;

const Name = styled.h2`
  font-size: 1.5rem;
  color: #4facfe;
  margin-bottom: 0.5rem;
`;

const Role = styled.h3`
  font-size: 1.2rem;
  color: #ff9966;
  margin-bottom: 1rem;
`;

const Description = styled.p`
  color: #e6f0ff;
  line-height: 1.6;
  font-size: 1rem;
`;

const ContinueButton = styled.button`
  margin-top: 2rem;
  padding: 1rem 2.5rem;
  font-size: 1.2rem;
  font-weight: 600;
  border: none;
  border-radius: 50px;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  animation: ${fadeIn} 1s ease-out;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
  }
`;

const RoomButton = styled.button`
  margin-top: 1rem;
  padding: 0.8rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  border-radius: 25px;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
  }
`;

const FileUploadSection = styled.div`
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: ${fadeIn} 1s ease-out;
`;

const FileDropzone = styled.div`
  width: 100%;
  height: 200px;
  border: 2px dashed ${props => props.isDragActive ? '#4facfe' : 'rgba(255, 255, 255, 0.3)'};
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: ${props => props.isDragActive ? 'rgba(79, 172, 254, 0.1)' : 'transparent'};
  margin-bottom: 1rem;

  &:hover {
    border-color: #4facfe;
    background: rgba(79, 172, 254, 0.1);
  }
`;

const UploadText = styled.p`
  color: #e6f0ff;
  font-size: 1.2rem;
  margin: 1rem 0;
  text-align: center;
`;

const GuidelineCard = styled.div`
  width: 100%;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  margin-top: 2rem;
  animation: ${fadeIn} 1s ease-out;
`;

const GuidelineTitle = styled.h3`
  color: #4facfe;
  font-size: 1.3rem;
  margin-bottom: 1rem;
`;

const GuidelineText = styled.p`
  color: #e6f0ff;
  line-height: 1.6;
`;

const SectionList = styled.div`
  width: 100%;
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const SectionItem = styled.div`
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateX(10px);
  }
`;

const StartButton = styled.button`
  margin-top: 2rem;
  padding: 1rem 2.5rem;
  font-size: 1.2rem;
  font-weight: 600;
  border: none;
  border-radius: 50px;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  width: fit-content;
  align-self: center;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
  }
`;

const LessonPlanContainer = styled.div`
  width: 100%;
  max-width: 1200px;
  margin: 2rem auto;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  animation: ${fadeIn} 1s ease-out;
`;

const OverviewSection = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 2rem;
  margin-bottom: 2rem;
`;

const OverviewTitle = styled.h2`
  color: #4facfe;
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
  text-align: center;
`;

const OverviewGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
`;

const OverviewItem = styled.div`
  text-align: center;
`;

const OverviewLabel = styled.div`
  color: #ff9966;
  font-size: 1rem;
  margin-bottom: 0.5rem;
`;

const OverviewValue = styled.div`
  color: #ffffff;
  font-size: 1.2rem;
  font-weight: bold;
`;

const LessonList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const LessonCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 1.5rem;
`;

const LessonTitle = styled.h3`
  color: #4facfe;
  font-size: 1.4rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  &:before {
    content: "Lesson ${props => props.lessonNumber}:";
    color: #ff9966;
    font-size: 1.2rem;
  }
`;

const KeyConceptsList = styled.ul`
  list-style-type: none;
  padding: 0;
  margin: 0;
`;

const KeyConceptItem = styled.li`
  color: #e6f0ff;
  margin-bottom: 0.5rem;
  padding-left: 1.5rem;
  position: relative;

  &:before {
    content: "•";
    color: #ff9966;
    position: absolute;
    left: 0;
  }
`;

const LoadingSpinner = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 2rem;
  color: #4facfe;
  font-size: 1.2rem;
`;

const Spinner = styled.div`
  width: 50px;
  height: 50px;
  border: 5px solid rgba(79, 172, 254, 0.3);
  border-radius: 50%;
  border-top-color: #4facfe;
  animation: spin 1s ease-in-out infinite;
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

const StartLearningButton = styled.button`
  margin-top: 2rem;
  padding: 1rem 2rem;
  font-size: 1.2rem;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  align-self: center;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
  }
`;

const IntroductionPage = () => {
  const navigate = useNavigate();
  const [isDragActive, setIsDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [guideline, setGuideline] = useState(null);
  const [selectedSection, setSelectedSection] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [fileId, setFileId] = useState(null);
  const [error, setError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const handleDragEnter = (e) => {
    e.preventDefault();
    setIsDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragActive(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragActive(false);
    setError(null);
    setUploadSuccess(false);
    
    const file = e.dataTransfer.files[0];
    if (file) {
      setUploadedFile(file);
      setIsLoading(true);
      try {
        // Upload to Azure Cosmos DB
        const cosmoResponse = await uploadMaterial(file);
        setFileId(cosmoResponse.file_id);
        
        // Then process with lesson plan API
        const lessonResponse = await uploadLessonPlan(file);
        setGuideline(lessonResponse.guideline);
        
        setUploadSuccess(true);
        setIsLoading(false);
      } catch (error) {
        console.error('Error uploading file:', error);
        setIsLoading(false);
        setError('Failed to upload file. Please try again.');
      }
    }
  };

  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    setError(null);
    setUploadSuccess(false);
    
    if (file) {
      setUploadedFile(file);
      setIsLoading(true);
      try {
        // Upload to Azure Cosmos DB
        const cosmoResponse = await uploadMaterial(file);
        setFileId(cosmoResponse.file_id);
        
        // Then process with lesson plan API
        const lessonResponse = await uploadLessonPlan(file);
        setGuideline(lessonResponse.guideline);
        
        setUploadSuccess(true);
        setIsLoading(false);
      } catch (error) {
        console.error('Error uploading file:', error);
        setIsLoading(false);
        setError('Failed to upload file. Please try again.');
      }
    }
  };

  const handleSectionClick = (sectionId) => {
    setSelectedSection(sectionId);
    localStorage.setItem('selectedSection', sectionId);
  };

  const handleStartClass = async () => {
    if (!fileId) {
      setError('Please upload a lesson plan first');
      return;
    }
    
    try {
      setIsLoading(true);
      const sessionData = await startSession(fileId);
      
      // Store session data in localStorage for use across components
      localStorage.setItem('sessionId', sessionData.session_id);
      localStorage.setItem('lessonIndex', sessionData.lesson_index);
      localStorage.setItem('fileId', fileId);
      
      setIsLoading(false);
      navigate('/main-classroom');
    } catch (error) {
      console.error('Error starting session:', error);
      setIsLoading(false);
      setError('Failed to start learning session. Please try again.');
    }
  };

  const handleRoomClick = (roomName) => {
    navigate(`/${roomName.toLowerCase()}`);
  };

  return (
    <PageContainer>
      <ContentWrapper>
        <Title>Welcome to Your 3D Classroom</Title>
        
        <FileUploadSection>
          <FileDropzone
            isDragActive={isDragActive}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => document.getElementById('fileInput').click()}
          >
            <UploadText>Drag and drop your lesson plan file here or click to select</UploadText>
            <input
              id="fileInput"
              type="file"
              accept=".pdf,.json,.docx,.txt"
              style={{ display: 'none' }}
              onChange={handleFileSelect}
            />
          </FileDropzone>
          {uploadSuccess && (
            <div style={{ 
              marginTop: '1rem', 
              padding: '0.75rem', 
              borderRadius: '8px', 
              backgroundColor: 'rgba(46, 204, 113, 0.2)', 
              color: '#2ecc71', 
              textAlign: 'center' 
            }}>
              File uploaded successfully to Azure Cosmos DB!
            </div>
          )}
        </FileUploadSection>

        {isLoading && (
          <LoadingSpinner>
            <Spinner />
            <p>Analyzing your lesson plan...</p>
          </LoadingSpinner>
        )}

        {guideline && !isLoading && (
          <GuidelineCard>
            <GuidelineTitle>{guideline.title}</GuidelineTitle>
            <GuidelineText>{guideline.content}</GuidelineText>
            
            {guideline.overview && (
              <div style={{ marginTop: '2rem', marginBottom: '2rem' }}>
                <h3 style={{ color: '#4facfe', marginBottom: '1rem', textAlign: 'center' }}>Overview</h3>
                <div style={{ 
                  display: 'flex', 
                  flexWrap: 'wrap', 
                  gap: '1rem', 
                  alignItems: 'center',
                  color: '#e6f0ff',
                  fontSize: '1.1rem',
                  justifyContent: 'center'
                }}>
                  <span><strong>Subject:</strong> {guideline.overview.subject}</span>
                  <span style={{ color: '#4facfe' }}>•</span>
                  <span><strong>Grade:</strong> {guideline.overview.grade}</span>
                  <span style={{ color: '#4facfe' }}>•</span>
                  <span><strong>Topic:</strong> {guideline.overview.topic}</span>
                  <span style={{ color: '#4facfe' }}>•</span>
                  <span><strong>Total Lessons:</strong> {guideline.overview.totalLessons}</span>
                </div>
              </div>
            )}

            <SectionList>
              {guideline.sections.map((section) => (
                <SectionItem key={section.id} onClick={() => handleSectionClick(section.id)}>
                  <h3 style={{ color: '#4facfe', marginBottom: '0.5rem' }}>{section.title}</h3>
                  <p style={{ color: '#e6f0ff', marginBottom: '0.5rem' }}>{section.description}</p>
                  {section.keyPoints && (
                    <ul style={{ marginLeft: '1.5rem', color: '#e6f0ff' }}>
                      {section.keyPoints.map((point, index) => (
                        <KeyConceptItem key={index}>{point}</KeyConceptItem>
                      ))}
                    </ul>
                  )}
                </SectionItem>
              ))}
            </SectionList>

            <div style={{ display: 'flex', justifyContent: 'center', marginTop: '2rem' }}>
              <StartLearningButton onClick={handleStartClass}>
                Start Learning
              </StartLearningButton>
            </div>
          </GuidelineCard>
        )}

        <Section>
          <SectionTitle>Available Rooms</SectionTitle>
          <Grid>
            <Card onClick={() => handleRoomClick('main-classroom')}>
              <RoomImage style={{ backgroundImage: "url('/classroom-bg.jpg')" }} />
              <Name>Main Classroom</Name>
              <Description>Enter the main virtual classroom for an immersive learning experience.</Description>
              <RoomButton>Enter Room</RoomButton>
            </Card>
            <Card onClick={() => handleRoomClick('Discussion')}>
              <RoomImage style={{ backgroundImage: "url('/discussion-room-bg.png')" }} />
              <Name>Discussion Room</Name>
              <Description>Join interactive discussions with your virtual classmates and teacher.</Description>
              <RoomButton>Enter Room</RoomButton>
            </Card>
            <Card onClick={() => handleRoomClick('Quiz')}>
              <RoomImage style={{ backgroundImage: "url('/quiz-room-bg.png')" }} />
              <Name>Quiz Room</Name>
              <Description>Test your knowledge and get instant feedback on your progress.</Description>
              <RoomButton>Enter Room</RoomButton>
            </Card>
          </Grid>
        </Section>
      </ContentWrapper>
    </PageContainer>
  );
};

export default IntroductionPage; 