/**
 * Redux Executive Dashboard Slice.
 *
 * Manages fetching, caching, and state storage of aggregated executive metrics and sentiment breakdowns.
 */

import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { DashboardSummary } from '@/types';
import { dashboardApi } from '@/services/dashboardApi';

interface DashboardState {
  summary: DashboardSummary | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: DashboardState = {
  summary: null,
  isLoading: false,
  error: null,
};

/**
 * Async thunk to fetch aggregated executive dashboard summary metrics.
 */
export const fetchDashboardSummary = createAsyncThunk(
  'dashboard/fetchSummary',
  async (_, { rejectWithValue }) => {
    try {
      return await dashboardApi.getDashboardSummary();
    } catch (err: any) {
      return rejectWithValue(err.message || 'Failed to fetch dashboard summary');
    }
  }
);

export const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    /** Clear active dashboard error message */
    clearDashboardError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchDashboardSummary.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(
        fetchDashboardSummary.fulfilled,
        (state, action: PayloadAction<DashboardSummary>) => {
          state.isLoading = false;
          state.summary = action.payload;
        }
      )
      .addCase(fetchDashboardSummary.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearDashboardError } = dashboardSlice.actions;
export default dashboardSlice.reducer;

