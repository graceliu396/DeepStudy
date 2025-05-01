import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from '@emotion/styled';
import { 
  IoHomeOutline, 
  IoBookOutline, 
  IoChatbubbleOutline, 
  IoSchoolOutline,
  IoPersonCircleOutline,
  IoLogOutOutline,
  IoCheckboxOutline
} from 'react-icons/io5';

const NavContainer = styled.nav`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 70px;
  background: rgba(26, 26, 46, 0.95);
  backdrop-filter: blur(10px);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  z-index: 1000;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  width: 100%;
  flex: 1;
  max-width: 100%;
  box-sizing: border-box;
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  flex: 0 0 auto;
`;

const LogoText = styled.h1`
  color: #4facfe;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
`;

const NavLinks = styled.div`
  display: flex;
  gap: 2rem;
  align-items: center;
  flex: 1;
  justify-content: center;
`;

const NavLink = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: ${props => props.active ? '#4facfe' : '#ffffff'};
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 500;

  &:hover {
    color: #4facfe;
    background: rgba(79, 172, 254, 0.1);
  }

  svg {
    font-size: 1.2rem;
  }
`;

const AccountSection = styled.div`
  position: relative;
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 0 0 auto;
`;

const AccountIcon = styled.div`
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 8px;
  color: #ffffff;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  svg {
    font-size: 1.8rem;
  }
`;

const AccountMenu = styled.div`
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background: rgba(26, 26, 46, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  padding: 0.5rem;
  min-width: 200px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  display: ${props => props.isOpen ? 'block' : 'none'};
`;

const MenuItem = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  color: #ffffff;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(79, 172, 254, 0.1);
    color: #4facfe;
  }

  svg {
    font-size: 1.2rem;
  }
`;

const NavBar = () => {
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState('home');
  const [isAccountMenuOpen, setIsAccountMenuOpen] = useState(false);

  const handleNavigation = (page) => {
    setCurrentPage(page);
    switch (page) {
      case 'home':
        navigate('/introduction');
        break;
      case 'classroom':
        navigate('/main-classroom');
        break;
      case 'discussion':
        navigate('/discussion');
        break;
      case 'quiz':
        navigate('/quiz');
        break;
      case 'profile':
        navigate('/profile');
        break;
      default:
        navigate('/introduction');
    }
    setIsAccountMenuOpen(false);
  };

  const handleLogout = () => {
    // TODO: Implement logout logic
    navigate('/');
    setIsAccountMenuOpen(false);
  };

  return (
    <NavContainer>
      <Logo onClick={() => handleNavigation('home')}>
        <IoSchoolOutline size={24} color="#4facfe" />
        <LogoText>DeepStudy</LogoText>
      </Logo>

      <NavLinks>
        <NavLink 
          active={currentPage === 'home'} 
          onClick={() => handleNavigation('home')}
        >
          <IoHomeOutline />
          Home
        </NavLink>
        <NavLink 
          active={currentPage === 'classroom'} 
          onClick={() => handleNavigation('classroom')}
        >
          <IoBookOutline />
          Classroom
        </NavLink>
        <NavLink 
          active={currentPage === 'discussion'} 
          onClick={() => handleNavigation('discussion')}
        >
          <IoChatbubbleOutline />
          Discussion
        </NavLink>
        <NavLink 
          active={currentPage === 'quiz'} 
          onClick={() => handleNavigation('quiz')}
        >
          <IoCheckboxOutline />
          Quiz
        </NavLink>
      </NavLinks>

      <AccountSection>
        <AccountIcon onClick={() => setIsAccountMenuOpen(!isAccountMenuOpen)}>
          <IoPersonCircleOutline />
        </AccountIcon>
        <AccountMenu isOpen={isAccountMenuOpen}>
          <MenuItem onClick={() => handleNavigation('profile')}>
            <IoPersonCircleOutline />
            Profile
          </MenuItem>
          <MenuItem onClick={handleLogout}>
            <IoLogOutOutline />
            Logout
          </MenuItem>
        </AccountMenu>
      </AccountSection>
    </NavContainer>
  );
};

export default NavBar; 