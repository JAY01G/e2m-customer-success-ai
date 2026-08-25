'use client';

/**
 * Redux Store Context Provider.
 *
 * Wraps client component subtrees with the initialized Redux store context.
 */

import React from 'react';
import { Provider } from 'react-redux';
import { store } from '@/store';

/**
 * Client component provider wrapping application tree in the global Redux store.
 */
export const ReduxProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <Provider store={store}>{children}</Provider>;
};

