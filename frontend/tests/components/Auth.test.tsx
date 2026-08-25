import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import authReducer from '@/store/slices/authSlice';
import { ToastProvider } from '@/components/providers/ToastProvider';
import LoginPage from '@/app/login/page';
import RegisterPage from '@/app/register/page';
import {
  setStorageToken,
  getStorageToken,
  setStorageRefreshToken,
  getStorageRefreshToken,
  clearStorageAuth,
} from '@/lib/helpers';

const createMockStore = () =>
  configureStore({
    reducer: {
      auth: authReducer,
    },
  });

describe('Authentication Pages', () => {
  it('renders login page with email and password inputs', () => {
    const store = createMockStore();
    render(
      <Provider store={store}>
        <ToastProvider>
          <LoginPage />
        </ToastProvider>
      </Provider>
    );

    expect(screen.getByText('Sign In')).toBeInTheDocument();
    expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /Sign In to Platform/i })
    ).toBeInTheDocument();
  });

  it('displays validation errors on submitting empty login form', async () => {
    const store = createMockStore();
    render(
      <Provider store={store}>
        <ToastProvider>
          <LoginPage />
        </ToastProvider>
      </Provider>
    );

    const submitBtn = screen.getByRole('button', {
      name: /Sign In to Platform/i,
    });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(
        screen.getByText(/Please enter a valid email address/i)
      ).toBeInTheDocument();
    });
  });

  it('renders registration page with role dropdown and fields', () => {
    const store = createMockStore();
    render(
      <Provider store={store}>
        <ToastProvider>
          <RegisterPage />
        </ToastProvider>
      </Provider>
    );

    expect(screen.getByText('Create Account')).toBeInTheDocument();
    expect(screen.getByLabelText(/Full Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Organization Role/i)).toBeInTheDocument();
  });

  it('correctly persists and clears refresh tokens in storage helpers', () => {
    setStorageToken('test-access-token');
    setStorageRefreshToken('test-refresh-token');

    expect(getStorageToken()).toBe('test-access-token');
    expect(getStorageRefreshToken()).toBe('test-refresh-token');

    clearStorageAuth();

    expect(getStorageToken()).toBeNull();
    expect(getStorageRefreshToken()).toBeNull();
  });
});


