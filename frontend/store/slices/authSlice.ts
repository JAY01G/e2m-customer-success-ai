/**
 * Redux Authentication Slice.
 *
 * Manages user login/register async thunks, token persistence, and session state.
 */

import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { AuthState, User, AuthResponseData } from '@/types';
import { authApi } from '@/services/authApi';
import { LoginFormData, RegisterFormData } from '@/schemas';
import {
  getStorageToken,
  setStorageToken,
  removeStorageToken,
  setStorageRefreshToken,
  removeStorageRefreshToken,
  getStorageUser,
  setStorageUser,
  removeStorageUser,
  clearStorageAuth,
} from '@/lib/helpers';

const initialState: AuthState = {
  user: getStorageUser(),
  token: getStorageToken(),
  isAuthenticated: !!getStorageToken(),
  isLoading: false,
  error: null,
};

/**
 * Async thunk to authenticate credentials, persist tokens to localStorage, and populate Auth state.
 */
export const loginUser = createAsyncThunk(
  'auth/login',
  async (data: LoginFormData, { rejectWithValue }) => {
    try {
      const response = await authApi.login(data);
      setStorageToken(response.access_token);
      if (response.refresh_token) {
        setStorageRefreshToken(response.refresh_token);
      }
      setStorageUser(response.user);
      return response;
    } catch (err: any) {
      return rejectWithValue(err.message || 'Login failed');
    }
  }
);

/**
 * Async thunk to register a new user and set active session.
 */
export const registerUser = createAsyncThunk(
  'auth/register',
  async (data: RegisterFormData, { rejectWithValue }) => {
    try {
      const response = await authApi.register(data);
      setStorageToken(response.access_token);
      if (response.refresh_token) {
        setStorageRefreshToken(response.refresh_token);
      }
      setStorageUser(response.user);
      return response;
    } catch (err: any) {
      return rejectWithValue(err.message || 'Registration failed');
    }
  }
);

/**
 * Async thunk to fetch the currently authenticated user profile and refresh cache.
 */
export const fetchCurrentUser = createAsyncThunk(
  'auth/fetchCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const user = await authApi.getMe();
      setStorageUser(user);
      return user;
    } catch (err: any) {
      return rejectWithValue(err.message || 'Failed to fetch user profile');
    }
  }
);

export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    /**
     * Clear session tokens, user cache, and reset authentication state.
     */
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      state.error = null;
      clearStorageAuth();
    },
    /**
     * Reset any pending auth error messages.
     */
    clearAuthError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action: PayloadAction<AuthResponseData>) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.token = action.payload.access_token;
        state.user = action.payload.user;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Register
      .addCase(registerUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state, action: PayloadAction<AuthResponseData>) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.token = action.payload.access_token;
        state.user = action.payload.user;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Current User
      .addCase(fetchCurrentUser.fulfilled, (state, action: PayloadAction<User>) => {
        state.user = action.payload;
        state.isAuthenticated = true;
      });
  },
});

export const { logout, clearAuthError } = authSlice.actions;
export default authSlice.reducer;

