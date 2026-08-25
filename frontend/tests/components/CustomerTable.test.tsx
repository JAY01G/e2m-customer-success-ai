import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import authReducer from '@/store/slices/authSlice';
import { CustomerTable } from '@/components/customers/CustomerTable';
import { Customer, UserRole } from '@/types';

const mockCustomers: Customer[] = [
  {
    id: 'cust-1',
    name: 'Sarah Connor',
    company_name: 'Cyberdyne Systems',
    email: 'sarah@cyberdyne.io',
    phone: '+1 555 123 4567',
    industry: 'Robotics',
    status: 'ACTIVE',
    health_score: 95,
    owner_id: 'user-1',
    owner: { id: 'user-1', name: 'John Admin', email: 'admin@test.com', role: 'ADMIN' as UserRole, is_active: true },
    notes: 'Key client',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'cust-2',
    name: 'Miles Dyson',
    company_name: 'Dyson Research',
    email: 'miles@dyson.com',
    status: 'AT_RISK',
    health_score: 42,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

const createMockStore = () =>
  configureStore({
    reducer: {
      auth: authReducer,
    },
    preloadedState: {
      auth: {
        user: { id: 'user-1', name: 'John Admin', email: 'admin@test.com', role: 'ADMIN' as UserRole, is_active: true },
        token: 'fake-token',
        isAuthenticated: true,
        isLoading: false,
        error: null,
      },
    },
  });

describe('CustomerTable Component', () => {
  it('renders table headers and customer list data properly', () => {
    const store = createMockStore();
    render(
      <Provider store={store}>
        <CustomerTable customers={mockCustomers} />
      </Provider>
    );

    expect(screen.getByText('Cyberdyne Systems')).toBeInTheDocument();
    expect(screen.getByText('Dyson Research')).toBeInTheDocument();
    expect(screen.getByText(/ACTIVE/i)).toBeInTheDocument();
    expect(screen.getByText(/AT RISK/i)).toBeInTheDocument();
    expect(screen.getByText('95')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  it('renders empty state message when no customers are provided', () => {
    const store = createMockStore();
    render(
      <Provider store={store}>
        <CustomerTable customers={[]} />
      </Provider>
    );

    expect(
      screen.getByText(/No customer accounts found matching your criteria/i)
    ).toBeInTheDocument();
  });
});
