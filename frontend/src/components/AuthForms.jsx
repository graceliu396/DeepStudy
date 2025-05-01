import React, { useState } from 'react';
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

const AuthContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2rem;
  width: 100%;
  max-width: 1200px;
  animation: ${fadeIn} 0.5s ease-out;
  padding: 2rem;
  margin: 0 auto;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 3rem;
  border-radius: 15px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
`;

const Title = styled.h2`
  color: #ffffff;
  text-align: center;
  margin-bottom: 1.5rem;
  font-size: 2rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
`;

const Input = styled.input`
  padding: 1rem;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
  width: 100%;

  &:focus {
    outline: none;
    background: rgba(255, 255, 255, 0.15);
  }

  &::placeholder {
    color: rgba(255, 255, 255, 0.6);
  }
`;

const Button = styled.button`
  padding: 1rem;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  margin-top: 1rem;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.3);

  &:hover {
    transform: translateY(-2px);
    background: rgba(255, 255, 255, 0.3);
    box-shadow: 0 5px 15px rgba(255, 255, 255, 0.2);
  }
`;

const ToggleText = styled.p`
  text-align: center;
  color: #ffffff;
  cursor: pointer;
  transition: color 0.3s ease;
  font-size: 1rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);

  &:hover {
    color: #ffd700;
  }
`;

const ErrorMessage = styled.p`
  color: #ff5e62;
  text-align: center;
  font-size: 0.9rem;
  margin-top: -1rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
`;

const AuthForms = ({ onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
  });
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
  };

  const validateForm = () => {
    if (!formData.email || !formData.password) {
      setError('Please fill in all required fields');
      return false;
    }
    if (!isLogin && !formData.name) {
      setError('Please fill in all required fields');
      return false;
    }
    if (!formData.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      setError('Please enter a valid email address');
      return false;
    }
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return false;
    }
    return true;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    // TODO: Replace with actual API call
    // Simulate successful authentication
    setTimeout(() => {
      onAuthSuccess();
    }, 1000);
  };

  return (
    <AuthContainer>
      <Form onSubmit={handleSubmit}>
        <Title>{isLogin ? 'Login' : 'Register'}</Title>
        
        {!isLogin && (
          <Input
            type="text"
            name="name"
            placeholder="Full Name"
            value={formData.name}
            onChange={handleChange}
            required
          />
        )}
        
        <Input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleChange}
          required
        />
        
        <Input
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleChange}
          required
        />
        
        {error && <ErrorMessage>{error}</ErrorMessage>}
        
        <Button type="submit">
          {isLogin ? 'Login' : 'Register'}
        </Button>
      </Form>
      
      <ToggleText onClick={() => setIsLogin(!isLogin)}>
        {isLogin 
          ? "Don't have an account? Register here" 
          : "Already have an account? Login here"}
      </ToggleText>
    </AuthContainer>
  );
};

export default AuthForms; 