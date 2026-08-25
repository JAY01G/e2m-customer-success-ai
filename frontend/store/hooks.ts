/**
 * Typed Redux Hooks.
 *
 * Provides pre-typed `useAppDispatch` and `useAppSelector` hooks for Redux store state access.
 */

import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import type { AppDispatch, RootState } from './index';

/**
 * Pre-typed hook for dispatching Redux actions and thunks.
 */
export const useAppDispatch = () => useDispatch<AppDispatch>();

/**
 * Pre-typed hook for selecting state from the Redux RootState.
 */
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

