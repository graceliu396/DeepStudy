import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled from '@emotion/styled';
import NavBar from './components/NavBar';
import WelcomePage from './components/WelcomePage';
import IntroductionPage from './components/IntroductionPage';
import ClassroomPage from './components/ClassroomPage';
import MainClassroomPage from './components/MainClassroomPage';
import QuizRoom from './components/QuizRoom';
import DiscussionRoom from './components/DiscussionRoom';
import ProfilePage from './components/ProfilePage';
import VoiceInteractionPage from './components/VoiceInteractionPage';
import './App.css';

const AppContainer = styled.div`
  min-height: 100vh;
  width: 100vw;
  position: relative;
`;

const PageWrapper = styled.div`
  margin-top: 70px;
  min-height: calc(100vh - 70px);
  width: 100;
`;

function App() {
  return (
    <Router>
      <AppContainer>
        <NavBar />
        <PageWrapper>
          <Routes>
            <Route path="/" element={<WelcomePage />} />
            <Route path="/introduction" element={<IntroductionPage />} />
            <Route path="/classroom" element={<ClassroomPage />} />
            <Route path="/main-classroom" element={<MainClassroomPage />} />
            <Route path="/quiz" element={<QuizRoom />} />
            <Route path="/discussion" element={<DiscussionRoom />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/voice-interaction" element={<VoiceInteractionPage />} />
          </Routes>
        </PageWrapper>
      </AppContainer>
    </Router>
  );
}

export default App;
