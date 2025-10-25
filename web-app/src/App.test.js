import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';
import { AuthProvider } from './services/auth';

// Mock the AuthProvider for testing
const MockAuthProvider = ({ children }) => {
  const mockAuth = {
    user: { name: 'Test User', email: 'test@example.com' },
    isAuthenticated: true,
    login: jest.fn(),
    logout: jest.fn()
  };
  
  return (
    <AuthProvider.Provider value={mockAuth}>
      {children}
    </AuthProvider.Provider>
  );
};

test('renders AWS Cost Optimizer title', () => {
  render(
    <MockAuthProvider>
      <App />
    </MockAuthProvider>
  );
  const titleElement = screen.getByText(/AWS Cost Optimizer/i);
  expect(titleElement).toBeInTheDocument();
});

test('renders dashboard component', () => {
  render(
    <MockAuthProvider>
      <App />
    </MockAuthProvider>
  );
  const dashboardElement = screen.getByText(/Dashboard/i);
  expect(dashboardElement).toBeInTheDocument();
});

test('renders navigation menu', () => {
  render(
    <MockAuthProvider>
      <App />
    </MockAuthProvider>
  );
  const navElement = screen.getByRole('navigation');
  expect(navElement).toBeInTheDocument();
});
