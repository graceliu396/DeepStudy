import React, { useState, useRef, useEffect } from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';
import { useNavigate } from 'react-router-dom';
import { IoExitOutline, IoCheckmarkCircle, IoCloseCircle } from 'react-icons/io5';
import { getLessonSummary } from '../utils/api';

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
    background-image: url('/quiz-room-bg.png');
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
  padding-bottom: 40px;
  gap: 2rem;
  z-index: 1;
`;

const CharacterSection = styled.div`
  flex: 0.5;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 20px;
  backdrop-filter: blur(5px);
  padding: 2rem;
`;

const ChatSection = styled.div`
  flex: 1;
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
  height: calc(100% - 80px);
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

const QuestionContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1rem;
`;

const OptionButton = styled.button`
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  background: ${props => 
    props.isSelected && props.isCorrect ? 'rgba(39, 174, 96, 0.2)' : 
    props.isSelected && !props.isCorrect ? 'rgba(231, 76, 60, 0.2)' : 
    'rgba(255, 255, 255, 0.1)'
  };
  color: ${props => 
    props.isSelected && props.isCorrect ? '#2ecc71' : 
    props.isSelected && !props.isCorrect ? '#e74c3c' : 
    '#e6f0ff'
  };
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: space-between;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  &:disabled {
    cursor: default;
    opacity: ${props => props.isSelected ? 1 : 0.6};
  }
`;

const FeedbackIcon = styled.div`
  font-size: 1.25rem;
  display: flex;
  align-items: center;
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

const SubmitButton = styled.button`
  width: 100%;
  padding: 1rem;
  margin-top: 1rem;
  font-size: 1.1rem;
  font-weight: 600;
  border: none;
  border-radius: 15px;
  background: linear-gradient(90deg, #FF9966 0%, #FF5E62 100%);
  color: white;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  text-align: center;
  box-shadow: 0 5px 15px rgba(255, 94, 98, 0.3);

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(255, 94, 98, 0.4);
  }

  &:active {
    transform: translateY(-1px);
  }
`;

const TeacherImage = styled.div`
  width: 300px;
  height: 600px;
  border-radius: 15px;
  margin-bottom: 2rem;
  background-image: url('/quiz-teacher-avatar.png');
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

const NextButton = styled.button`
  align-self: flex-end;
  padding: 0.75rem 1.5rem;
  margin-top: 1rem;
  border: none;
  border-radius: 12px;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4);
  }
`;

const QuizRoom = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Welcome to the Quiz! I'm loading your questions based on what you've learned...",
      isUser: false
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [quizStarted, setQuizStarted] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [selectedOption, setSelectedOption] = useState(null);
  const [optionsDisabled, setOptionsDisabled] = useState(false);
  const [score, setScore] = useState(0);
  const [sessionId, setSessionId] = useState(null);
  const [lessonIndex, setLessonIndex] = useState(0);
  const [quizQuestions, setQuizQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Load quiz questions when component mounts
  useEffect(() => {
    // Retrieve session data from localStorage
    const storedSessionId = localStorage.getItem('sessionId');
    const storedLessonIndex = localStorage.getItem('lessonIndex');
    
    if (storedSessionId && storedLessonIndex) {
      setSessionId(storedSessionId);
      setLessonIndex(parseInt(storedLessonIndex, 10));
      
      // Fetch quiz questions from the backend
      fetchQuizQuestions(storedSessionId, parseInt(storedLessonIndex, 10));
    } else {
      setIsLoading(false);
      setError('No active session found. Please start a new session from the introduction page.');
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: "Error: No active session found. Please start a new session from the introduction page.",
        isUser: false
      }]);
    }
  }, []);

  const fetchQuizQuestions = async (sessionId, lessonIndex) => {
    try {
      setIsLoading(true);
      
      // Get the summary which includes exercises/questions
      const summaryData = await getLessonSummary(sessionId, lessonIndex);
      
      if (summaryData.exercise && Array.isArray(summaryData.exercise)) {
        // Transform the exercise data into the format our quiz component expects
        const formattedQuestions = summaryData.exercise.map(exercise => ({
          question: exercise.question,
          options: exercise.options.map(opt => ({
            text: opt.text,
            isCorrect: opt.isCorrect
          }))
        }));
        
        setQuizQuestions(formattedQuestions);
        
        // Update messages to show quiz is ready
        setMessages(prev => [...prev, {
          id: Date.now(),
          text: `Great! I have ${formattedQuestions.length} questions prepared for you based on your recent lesson. Ready to start?`,
          isUser: false
        }]);
      } else {
        throw new Error('No quiz questions found');
      }
      
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching quiz questions:', error);
      setError('Failed to load quiz questions. Please try again later.');
      setIsLoading(false);
      
      // Add fallback questions in case API fails
      setQuizQuestions([
        {
          question: "Fill in the blank: Multiplication is a shortcut for _____ when all groups have the same number of items.",
          options: [
            { text: "repeated addition", isCorrect: true },
            { text: "division", isCorrect: false },
            { text: "subtraction", isCorrect: false },
            { text: "equal sharing", isCorrect: false }
          ]
        },
        {
          question: "Fill in the blank: The expression for 5 groups of 7 items is written as _____.",
          options: [
            { text: "5 x 7", isCorrect: true },
            { text: "7 ÷ 5", isCorrect: false },
            { text: "7 + 5", isCorrect: false },
            { text: "5 + 5 + 5 + 5 + 5 + 5 + 5", isCorrect: false }
          ]
        }
      ]);
      
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: "I'm having trouble loading your personalized questions, but I've prepared some general questions about multiplication. Ready to start?",
        isUser: false
      }]);
    }
  };

  const handleQuit = () => {
    navigate('/introduction');
  };

  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      const newMessage = {
        id: Date.now(),
        text: inputMessage,
        isUser: true
      };
      setMessages(prev => [...prev, newMessage]);

      // Process user's message
      if (!quizStarted) {
        if (inputMessage.toLowerCase().includes("yes") || 
            inputMessage.toLowerCase().includes("ready") || 
            inputMessage.toLowerCase().includes("start") ||
            inputMessage.toLowerCase().includes("begin")) {
          startQuiz();
        } else {
          setTimeout(() => {
            setMessages(prev => [...prev, {
              id: Date.now(),
              text: "Whenever you're ready, just let me know by saying 'yes' or 'ready'.",
              isUser: false
            }]);
          }, 1000);
        }
      }

      setInputMessage('');
    }
  };

  const startQuiz = () => {
    if (quizQuestions.length === 0) {
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: "Sorry, I don't have any questions prepared. Please try again later.",
        isUser: false
      }]);
      return;
    }
    
    setQuizStarted(true);
    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: `Great! Let's begin the quiz. I'll present ${quizQuestions.length} multiple choice questions about what you've learned. Select the best answer for each.`,
        isUser: false
      }]);
      
      // Ask first question after a delay
      setTimeout(() => {
        setMessages(prev => [...prev, {
          id: Date.now(),
          text: `Question 1: ${quizQuestions[0].question}`,
          isUser: false,
          options: quizQuestions[0].options,
          questionIndex: 0
        }]);
        setCurrentQuestion(0);
      }, 2000);
    }, 1000);
  };

  const handleOptionSelect = (option, questionIndex) => {
    setSelectedOption(option);
    setOptionsDisabled(true);

    // Check if answer is correct
    setTimeout(() => {
      if (option.isCorrect) {
        setScore(prev => prev + 1);
        setMessages(prev => [...prev, {
          id: Date.now(),
          text: "Correct! Well done.",
          isUser: false
        }]);
      } else {
        // Find the correct answer
        const correctOption = quizQuestions[questionIndex].options.find(opt => opt.isCorrect);
        setMessages(prev => [...prev, {
          id: Date.now(),
          text: `That's not quite right. The correct answer is "${correctOption.text}".`,
          isUser: false
        }]);
      }
    }, 1000);
  };

  const handleNextQuestion = () => {
    setSelectedOption(null);
    setOptionsDisabled(false);
    
    if (currentQuestion < quizQuestions.length - 1) {
      const nextQuestionIndex = currentQuestion + 1;
      const nextQuestionNum = nextQuestionIndex + 1;
      
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: `Question ${nextQuestionNum}: ${quizQuestions[nextQuestionIndex].question}`,
        isUser: false,
        options: quizQuestions[nextQuestionIndex].options,
        questionIndex: nextQuestionIndex
      }]);
      
      setCurrentQuestion(nextQuestionIndex);
    } else {
      // End of quiz
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: `You've completed the quiz! Your score: ${score} out of ${quizQuestions.length}.`,
        isUser: false
      }]);
      
      setTimeout(() => {
        setMessages(prev => [...prev, {
          id: Date.now(),
          text: "You've shown a good understanding of multiplication and arrays. Would you like to return to the classroom?",
          isUser: false
        }]);
        setQuizCompleted(true);
      }, 2000);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  const handleReturnToClassroom = () => {
    navigate('/main-classroom');
  };

  const QuizMessageContent = ({ message }) => {
    if (!message.options) {
      return <>{message.text}</>;
    }
    
    return (
      <>
        <div>{message.text}</div>
        <QuestionContainer>
          {message.options.map((option, index) => (
            <OptionButton
              key={index}
              onClick={() => handleOptionSelect(option, message.questionIndex)}
              isSelected={selectedOption === option}
              isCorrect={option.isCorrect}
              disabled={optionsDisabled}
            >
              {option.text}
              {selectedOption === option && (
                <FeedbackIcon>
                  {option.isCorrect ? 
                    <IoCheckmarkCircle color="#2ecc71" /> : 
                    <IoCloseCircle color="#e74c3c" />
                  }
                </FeedbackIcon>
              )}
            </OptionButton>
          ))}
        </QuestionContainer>
        {selectedOption && (
          <NextButton onClick={handleNextQuestion}>
            Next Question
          </NextButton>
        )}
      </>
    );
  };

  return (
    <PageContainer>
      <QuitButton onClick={handleQuit}>
        <IoExitOutline /> Exit Quiz
      </QuitButton>
      <ContentContainer>
        <CharacterSection>
          <TeacherImage />
          <TeacherInfoContainer>
            <TeacherName>Mr. Quiz</TeacherName>
            <TeacherRole>Quiz Master</TeacherRole>
          </TeacherInfoContainer>
        </CharacterSection>
        <ChatSection>
          <ChatMessages>
            {messages.map(message => (
              <Message 
                key={message.id} 
                isUser={message.isUser}
              >
                {message.isUser ? 
                  message.text : 
                  <QuizMessageContent message={message} />
                }
              </Message>
            ))}
            {isLoading && (
              <Message isUser={false}>
                <div style={{ display: 'flex', justifyContent: 'center', padding: '1rem' }}>
                  <div style={{ 
                    width: '30px', 
                    height: '30px', 
                    borderRadius: '50%', 
                    border: '3px solid rgba(79, 172, 254, 0.3)',
                    borderTopColor: '#4facfe',
                    animation: 'spin 1s linear infinite'
                  }}></div>
                </div>
              </Message>
            )}
            {error && (
              <Message isUser={false}>
                <div style={{ color: '#ff5e62' }}>{error}</div>
              </Message>
            )}
            {quizCompleted && (
              <Message isUser={false}>
                <div>Ready to go back to the main classroom?</div>
                <SubmitButton onClick={handleReturnToClassroom}>
                  Return to Classroom
                </SubmitButton>
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
              disabled={quizStarted || isLoading}
            />
            <SendButton 
              onClick={handleSendMessage}
              disabled={quizStarted || isLoading}
            >
              Send
            </SendButton>
          </ChatInput>
        </ChatSection>
      </ContentContainer>
    </PageContainer>
  );
};

export default QuizRoom; 