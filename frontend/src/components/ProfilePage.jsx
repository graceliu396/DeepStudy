import React, { useState } from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';
import { IoPersonCircleOutline, IoSettingsOutline, IoSchoolOutline, IoStatsChartOutline, IoBookOutline } from 'react-icons/io5';

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
  min-height: calc(100vh - 70px);
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: white;
  padding: 2rem;
`;

const ContentWrapper = styled.div`
  width: 100%;
  max-width: 1200px;
  display: flex;
  gap: 2rem;
  animation: ${fadeIn} 1s ease-out;

  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const ProfileSection = styled.div`
  flex: 1;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const ProfileImage = styled.div`
  width: 150px;
  height: 150px;
  border-radius: 75px;
  background: #2a5298;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid #4facfe;
  overflow: hidden;

  svg {
    font-size: 80px;
    color: #4facfe;
  }

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
`;

const ProfileName = styled.h2`
  font-size: 1.8rem;
  color: #4facfe;
  margin-bottom: 0.5rem;
`;

const ProfileRole = styled.h3`
  font-size: 1.2rem;
  color: #ff9966;
  margin-bottom: 1.5rem;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  width: 100%;
  margin-top: 1.5rem;
`;

const StatCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 1rem;
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 1.5rem;
  color: #4facfe;
  margin-bottom: 0.5rem;
`;

const StatLabel = styled.div`
  font-size: 0.9rem;
  color: #e6f0ff;
`;

const DetailsSection = styled.div`
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const Card = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 2rem;
  margin-bottom: 1.5rem;
`;

const CardTitle = styled.h3`
  font-size: 1.3rem;
  color: #4facfe;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
`;

const InfoItem = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 1rem;
`;

const InfoLabel = styled.div`
  font-size: 0.9rem;
  color: #e6f0ff;
  margin-bottom: 0.5rem;
`;

const InfoValue = styled.div`
  font-size: 1.1rem;
  color: #4facfe;
`;

const EditButton = styled.button`
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

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  margin-top: 0.5rem;
  overflow: hidden;
`;

const Progress = styled.div`
  width: ${props => props.value}%;
  height: 100%;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
`;

const CourseList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const CourseItem = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const CourseInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const CourseName = styled.div`
  font-size: 1.1rem;
  color: #4facfe;
`;

const CourseDate = styled.div`
  font-size: 0.9rem;
  color: #e6f0ff;
`;

const CourseStatus = styled.div`
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  background: ${props => props.status === 'dropped' ? 'rgba(255, 99, 99, 0.2)' : 'rgba(79, 172, 254, 0.2)'};
  color: ${props => props.status === 'dropped' ? '#ff6363' : '#4facfe'};
`;

const ProfilePage = () => {
  const [userProfile] = useState({
    name: 'John Doe',
    role: 'Student',
    email: 'john.doe@example.com',
    studentId: 'STU123456',
    department: 'Computer Science',
    joinDate: 'September 2023',
    currentCourses: [
      { name: 'Advanced Mathematics', date: '2024-01-15', status: 'active' },
      { name: 'Physics 101', date: '2024-01-15', status: 'active' }
    ],
    droppedMaterials: [
      { name: 'Introduction to Programming', date: '2023-12-01', status: 'dropped' },
      { name: 'Digital Logic', date: '2023-11-15', status: 'dropped' }
    ]
  });

  return (
    <PageContainer>
      <ContentWrapper>
        <ProfileSection>
          <ProfileImage>
            <IoPersonCircleOutline />
          </ProfileImage>
          <ProfileName>{userProfile.name}</ProfileName>
          <ProfileRole>{userProfile.role}</ProfileRole>
          <EditButton>Edit Profile</EditButton>

          <StatsGrid>
            <StatCard>
              <StatValue>{userProfile.coursesCompleted}</StatValue>
              <StatLabel>Courses Completed</StatLabel>
            </StatCard>
            <StatCard>
              <StatValue>{userProfile.coursesInProgress}</StatValue>
              <StatLabel>Courses in Progress</StatLabel>
            </StatCard>
            <StatCard>
              <StatValue>{userProfile.averageScore}%</StatValue>
              <StatLabel>Average Score</StatLabel>
            </StatCard>
            <StatCard>
              <StatValue>{userProfile.attendanceRate}%</StatValue>
              <StatLabel>Attendance Rate</StatLabel>
            </StatCard>
          </StatsGrid>
        </ProfileSection>

        <DetailsSection>
          <Card>
            <CardTitle>
              <IoPersonCircleOutline />
              Personal Information
            </CardTitle>
            <InfoGrid>
              <InfoItem>
                <InfoLabel>Email</InfoLabel>
                <InfoValue>{userProfile.email}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>Student ID</InfoLabel>
                <InfoValue>{userProfile.studentId}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>Department</InfoLabel>
                <InfoValue>{userProfile.department}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>Join Date</InfoLabel>
                <InfoValue>{userProfile.joinDate}</InfoValue>
              </InfoItem>
            </InfoGrid>
          </Card>

          <Card>
            <CardTitle>
              <IoSchoolOutline />
              Current Courses
            </CardTitle>
            <CourseList>
              {userProfile.currentCourses.map((course, index) => (
                <CourseItem key={index}>
                  <CourseInfo>
                    <CourseName>{course.name}</CourseName>
                    <CourseDate>Started: {course.date}</CourseDate>
                  </CourseInfo>
                  <CourseStatus status={course.status}>Active</CourseStatus>
                </CourseItem>
              ))}
            </CourseList>
          </Card>

          <Card>
            <CardTitle>
              <IoBookOutline />
              Dropped Materials History
            </CardTitle>
            <CourseList>
              {userProfile.droppedMaterials.map((course, index) => (
                <CourseItem key={index}>
                  <CourseInfo>
                    <CourseName>{course.name}</CourseName>
                    <CourseDate>Dropped: {course.date}</CourseDate>
                  </CourseInfo>
                  <CourseStatus status={course.status}>Dropped</CourseStatus>
                </CourseItem>
              ))}
            </CourseList>
          </Card>
        </DetailsSection>
      </ContentWrapper>
    </PageContainer>
  );
};

export default ProfilePage; 