import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import config from '../config/config';
import theme from '../config/theme';

// Styled components for the Calendar with updated Journey themed colors
const CalendarContainer = styled.div`
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 100;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
`;

const CalendarButton = styled.button`
  padding: 10px 20px;
  background-color: ${theme.COLORS.PRIMARY}; /* New green color from the logo */
  color: ${theme.COLORS.TEXT_LIGHT};
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: ${theme.FONT_WEIGHTS.SEMI_BOLD};
  box-shadow: ${theme.SHADOWS.MEDIUM};
  transition: all 0.3s ease;
  font-family: ${theme.FONTS.PRIMARY};

  &:hover {
    background-color: ${theme.COLORS.PRIMARY_DARK}; /* Darker green for hover state */
    transform: translateY(-2px);
    box-shadow: ${theme.SHADOWS.LARGE};
  }

  &:active {
    transform: translateY(0);
    box-shadow: ${theme.SHADOWS.SMALL};
  }
`;

const CalendarPanel = styled.div`
  margin-top: 10px;
  background: white; /* Changed to white as requested */
  border-radius: 10px;
  box-shadow: ${theme.SHADOWS.LARGE};
  overflow: hidden;
  width: 300px;
  max-height: ${props => (props.$isOpen ? '500px' : '0')};
  opacity: ${props => (props.$isOpen ? '1' : '0')};
  transition: all 0.3s ease-in-out;
  transform-origin: top right;
  transform: ${props => (props.$isOpen ? 'scaleY(1)' : 'scaleY(0)')};
  font-family: ${theme.FONTS.PRIMARY};
`;

const CalendarHeader = styled.div`
  background: ${theme.COLORS.PRIMARY}; /* New green color from the logo */
  color: ${theme.COLORS.TEXT_LIGHT};
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const MonthNavigation = styled.div`
  display: flex;
  gap: 10px;
`;

const NavButton = styled.button`
  background: transparent;
  border: none;
  color: ${theme.COLORS.TEXT_LIGHT};
  cursor: pointer;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  transition: background 0.2s;
  font-family: ${theme.FONTS.PRIMARY};

  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }
`;

const MonthYear = styled.h3`
  margin: 0;
  font-size: 1.2rem;
  font-weight: ${theme.FONT_WEIGHTS.MEDIUM};
  font-family: ${theme.FONTS.PRIMARY};
`;

const CalendarGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  padding: 10px;
  font-family: ${theme.FONTS.PRIMARY};
`;

const WeekDay = styled.div`
  text-align: center;
  font-weight: ${theme.FONT_WEIGHTS.SEMI_BOLD};
  color: ${theme.COLORS.PRIMARY}; /* New green color from the logo */
  padding: 10px 0;
  font-size: 0.8rem;
  font-family: ${theme.FONTS.PRIMARY};
`;

const Day = styled.div`
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  color: ${props => props.$isCurrentMonth ? theme.COLORS.TEXT_DARK : '#ccc'};
  font-weight: ${props => props.$isToday ? theme.FONT_WEIGHTS.BOLD : theme.FONT_WEIGHTS.REGULAR};
  background: ${props => props.$isToday ? `rgba(42, 125, 79, 0.2)` : 'transparent'}; /* Updated highlight color */
  position: relative;
  font-family: ${theme.FONTS.PRIMARY};

  &:hover {
    background: ${props => (props.$isCurrentMonth ? 'rgba(42, 125, 79, 0.1)' : 'transparent')}; /* Updated hover color */
  }
`;

const Emoji = styled.span`
  position: absolute;
  top: -5px;
  right: -5px;
  font-size: 14px;
  animation: pulse 2s infinite;

  @keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.2); }
    100% { transform: scale(1); }
  }
`;

const Overlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.4);
  z-index: 90;
  opacity: ${props => (props.$isOpen ? '1' : '0')};
  visibility: ${props => (props.$isOpen ? 'visible' : 'hidden')};
  transition: all 0.3s ease-in-out;
`;

const MemoryPanel = styled.div`
  position: absolute;
  top: 70%;
  right: 320px;
  z-index: 110;
  background: white; /* Explicitly setting white background */
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  padding: 15px;
  width: 300px;
  max-height: 400px;
  opacity: ${props => (props.$isOpen ? '1' : '0')};
  overflow-y: auto;
  transition: all 0.3s ease-in-out;
  transform-origin: top right;
  transform: ${props => (props.$isOpen ? 'translateY(-30%)' : 'translateY(-10%)')};
  pointer-events: ${props => (props.$isOpen ? 'auto' : 'none')};
  font-family: 'Montserrat', sans-serif;
  border-left: 4px solid #2A7D4F; /* Adding a green accent */
`;

const MemoryDate = styled.h3`
  margin: 0 0 10px 0;
  color: #2A7D4F; /* New green color from the logo */
  font-weight: 500;
  font-family: 'Montserrat', sans-serif;
`;

const MemoryText = styled.p`
  margin: 0;
  white-space: pre-wrap;
  line-height: 1.5;
  color: #333;
  font-family: 'Montserrat', sans-serif;
`;

const LoadingSpinner = styled.div`
  display: ${props => props.$isLoading ? 'flex' : 'none'};
  justify-content: center;
  padding: 10px;
  color: #2A7D4F; /* New green color from the logo */
  font-size: 0.9rem;
  font-family: 'Montserrat', sans-serif;
`;

const ErrorMessage = styled.div`
  padding: 10px;
  color: #ff6b6b;
  text-align: center;
  font-size: 0.9rem;
  font-family: 'Montserrat', sans-serif;
`;

const EmptyState = styled.div`
  padding: 15px;
  text-align: center;
  color: #888;
  font-size: 0.9rem;
  display: ${props => props.$show ? 'block' : 'none'};
  font-family: 'Montserrat', sans-serif;
`;

const Calendar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [displayedMonth, setDisplayedMonth] = useState(new Date());
  const [memories, setMemories] = useState([]);
  const [selectedMemory, setSelectedMemory] = useState(null);
  const [showMemoryPanel, setShowMemoryPanel] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Function to force a refresh of the calendar login status
  const forceRefreshCalendar = () => {
    console.log('Force refreshing calendar login status');
    checkLoginStatus();
  };

  // Expose the refresh function to window so it can be called from other components
  useEffect(() => {
    window.forceRefreshCalendar = forceRefreshCalendar;

    return () => {
      delete window.forceRefreshCalendar;
    };
  }, []);

  // Check if user is logged in when component mounts
  useEffect(() => {
    checkLoginStatus();

    // Listen for authentication status changes
    const handleAuthStatusChange = () => {
      console.log('Auth status change detected in Calendar');
      checkLoginStatus();
    };

    // Listen for the custom event from Login component
    window.addEventListener('auth_status_changed', handleAuthStatusChange);

    // Also listen for changes to the auth_timestamp in localStorage
    const handleStorageChange = (e) => {
      if (e.key === 'auth_timestamp' || e.key === 'backendToken') {
        console.log('Storage change detected for auth data');
        checkLoginStatus();
      }
    };

    window.addEventListener('storage', handleStorageChange);

    // Clean up event listeners
    return () => {
      window.removeEventListener('auth_status_changed', handleAuthStatusChange);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  // Check for valid authentication token
  const checkLoginStatus = () => {
    try {
      const savedBackendToken = localStorage.getItem('backendToken');

      if (savedBackendToken) {
        // Try parsing the token and checking its validity
        try {
          const parsedToken = JSON.parse(savedBackendToken);
          if (parsedToken && (parsedToken.access_token || parsedToken.token)) {
            // Accept either access_token or token property
            setIsLoggedIn(true);
            console.log('User is logged in, calendar should display');
            return;
          }
        } catch (parseError) {
          // If it's not JSON, see if it's a direct token string
          if (typeof savedBackendToken === 'string' && savedBackendToken.length > 10) {
            setIsLoggedIn(true);
            console.log('User is logged in with direct token');
            return;
          }
        }
      }

      // Also check for other possible auth tokens that might be used
      const authToken = localStorage.getItem('authToken');
      if (authToken) {
        setIsLoggedIn(true);
        console.log('User is logged in with authToken');
        return;
      }

      console.log('No valid token found, calendar will not display');
      setIsLoggedIn(false);
    } catch (error) {
      console.error('Error checking login status:', error);
      setIsLoggedIn(false);
    }
  };

  // Fetch memories when calendar opens or month changes
  useEffect(() => {
    if (isOpen && isLoggedIn) {
      fetchMemories();
    }
  }, [isOpen, displayedMonth, isLoggedIn]);

  // Add this new useEffect to fetch memories when user logs in
  useEffect(() => {
    if (isLoggedIn) {
      console.log('User logged in, making sure calendar is ready');
      // Pre-fetch memories so they're ready when the user opens the calendar
      fetchMemories();
    }
  }, [isLoggedIn]);

  // Close calendar when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (isOpen && !event.target.closest('.calendar-container')) {
        setIsOpen(false);
        setShowMemoryPanel(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  // Fetch memories from API
  const fetchMemories = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Get the authentication token from localStorage - stored as a JSON string
      const savedBackendToken = localStorage.getItem('backendToken');

      if (!savedBackendToken) {
        setError('You need to be logged in to view memories');
        setIsLoading(false);
        return;
      }

      // Parse the backend token - it contains the actual access_token
      const parsedToken = JSON.parse(savedBackendToken);
      const token = parsedToken.access_token;

      if (!token) {
        setError('Invalid authentication token');
        setIsLoading(false);
        return;
      }

      // Use the API base URL from config
      const response = await fetch(`${config.API_BASE_URL}/memory/get_all`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        },
        credentials: 'include',
        mode: 'cors'
      });

      if (!response.ok) {
        throw new Error(`Error fetching memories: ${response.statusText}`);
      }

      const data = await response.json();
      setMemories(data.memories || []);
    } catch (error) {
      console.error('Error fetching memories:', error);
      setError('Failed to load memories. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  // Convert Unicode string to emoji
  const unicodeToEmoji = (unicodeString) => {
    if (!unicodeString) return '';

    // Remove the "U+" prefix and convert to a code point
    const codePoint = unicodeString.replace('U+', '0x');

    try {
      // Convert the hexadecimal code point to an actual emoji
      return String.fromCodePoint(parseInt(codePoint, 16));
    } catch (error) {
      console.error('Error converting Unicode to emoji:', error);
      return '';
    }
  };

  // Toggle calendar visibility
  const toggleCalendar = () => {
    setIsOpen(!isOpen);
    if (showMemoryPanel) {
      setShowMemoryPanel(false);
    }
  };

  // Navigate to previous month
  const prevMonth = () => {
    setDisplayedMonth(new Date(displayedMonth.getFullYear(), displayedMonth.getMonth() - 1, 1));
  };

  // Navigate to next month
  const nextMonth = () => {
    setDisplayedMonth(new Date(displayedMonth.getFullYear(), displayedMonth.getMonth() + 1, 1));
  };

  // Handle day click to show memories
  const handleDayClick = (day, isCurrentMonth) => {
    if (!isCurrentMonth) return;

    const year = displayedMonth.getFullYear();
    const month = displayedMonth.getMonth();
    const selectedDate = new Date(year, month, day);

    // Create a date string in YYYY-MM-DD format
    const selectedMonth = String(month + 1).padStart(2, '0');
    const selectedDay = String(day).padStart(2, '0');
    const dateStr = `${year}-${selectedMonth}-${selectedDay}`;

    // Find memory for the selected day - check if the timestamp starts with our date string
    const dayMemory = memories.find(memory => {
      // Handle both ISO format and YYYY-MM-DD format
      return memory.day_timestamp.startsWith(dateStr);
    });

    if (dayMemory) {
      setSelectedMemory(dayMemory);
      setShowMemoryPanel(true);
    } else {
      setSelectedMemory(null);
      setShowMemoryPanel(false);
    }
  };

  // Get days in a month
  const getDaysInMonth = (year, month) => {
    return new Date(year, month + 1, 0).getDate();
  };

  // Get first day of month (0 = Sunday, 1 = Monday, ...)
  const getFirstDayOfMonth = (year, month) => {
    return new Date(year, month, 1).getDay();
  };

  // Generate calendar days
  const renderCalendarDays = () => {
    const year = displayedMonth.getFullYear();
    const month = displayedMonth.getMonth();

    const daysInMonth = getDaysInMonth(year, month);
    const firstDayOfMonth = getFirstDayOfMonth(year, month);

    // Get days from previous month
    const daysInPrevMonth = getDaysInMonth(year, month - 1);
    const prevMonthDays = Array.from({ length: firstDayOfMonth }, (_, i) => ({
      day: daysInPrevMonth - firstDayOfMonth + i + 1,
      isCurrentMonth: false,
      isToday: false
    }));

    // Current month days
    const currentMonthDays = Array.from({ length: daysInMonth }, (_, i) => {
      const day = i + 1;
      const isToday =
        day === currentDate.getDate() &&
        month === currentDate.getMonth() &&
        year === currentDate.getFullYear();

      // Check if this day has memories with proper date format handling
      const formattedMonth = String(month + 1).padStart(2, '0');
      const formattedDay = String(day).padStart(2, '0');
      const dateStr = `${year}-${formattedMonth}-${formattedDay}`;

      const dayMemory = memories.find(memory => {
        return memory.day_timestamp.startsWith(dateStr);
      });

      return {
        day,
        isCurrentMonth: true,
        isToday,
        memory: dayMemory
      };
    });

    // Calculate remaining days needed for the grid
    const totalDaysDisplayed = prevMonthDays.length + currentMonthDays.length;
    const remainingDays = 42 - totalDaysDisplayed; // 6 rows x 7 columns = 42 cells

    // Next month days
    const nextMonthDays = Array.from({ length: remainingDays }, (_, i) => ({
      day: i + 1,
      isCurrentMonth: false,
      isToday: false
    }));

    // Combine all days
    return [...prevMonthDays, ...currentMonthDays, ...nextMonthDays];
  };

  // Format month name
  const formatMonth = (date) => {
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  };

  // Format date for memory panel
  const formatDate = (dateString) => {
    // Extract date part if timestamp contains spaces
    const datePart = dateString.includes(' ') ? dateString.split(' ')[0] : dateString.split('T')[0];
    return new Date(datePart).toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
  };

  // Week day labels
  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  // If user is not logged in, don't render the calendar at all
  if (!isLoggedIn) {
    console.log('Calendar not rendering - user not logged in');
    return null;
  }

  // Log when the calendar is rendering
  console.log('Calendar rendering - user is logged in');

  return (
    <CalendarContainer className="calendar-container">
      <CalendarButton onClick={toggleCalendar}>
        Show Calendar
      </CalendarButton>

      <CalendarPanel $isOpen={isOpen}>
        <CalendarHeader>
          <MonthYear>{formatMonth(displayedMonth)}</MonthYear>
          <MonthNavigation>
            <NavButton onClick={prevMonth}>&lt;</NavButton>
            <NavButton onClick={nextMonth}>&gt;</NavButton>
          </MonthNavigation>
        </CalendarHeader>

        <LoadingSpinner $isLoading={isLoading}>Loading memories...</LoadingSpinner>

        {error && <ErrorMessage>{error}</ErrorMessage>}

        <EmptyState $show={!isLoading && !error && memories.length === 0}>
          No memories found for this month.
        </EmptyState>

        <CalendarGrid>
          {weekDays.map(day => (
            <WeekDay key={day}>{day}</WeekDay>
          ))}

          {renderCalendarDays().map((day, index) => (
            <Day
              key={index}
              $isCurrentMonth={day.isCurrentMonth}
              $isToday={day.isToday}
              onClick={() => handleDayClick(day.day, day.isCurrentMonth)}
            >
              {day.day}
              {day.memory && (
                <Emoji>{unicodeToEmoji(day.memory.mood)}</Emoji>
              )}
            </Day>
          ))}
        </CalendarGrid>
      </CalendarPanel>

      <Overlay $isOpen={showMemoryPanel} onClick={() => setShowMemoryPanel(false)} />

      {selectedMemory && (
        <MemoryPanel $isOpen={showMemoryPanel}>
          <MemoryDate>{formatDate(selectedMemory.day_timestamp)}</MemoryDate>
          <MemoryText>{selectedMemory.memory_text}</MemoryText>
        </MemoryPanel>
      )}
    </CalendarContainer>
  );
};

export default Calendar;
