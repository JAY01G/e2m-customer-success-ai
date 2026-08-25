/**
 * Redux Customer Interaction Slice.
 *
 * Manages customer touchpoint logs, pagination, detail views, creation mutations, and AI insight generation.
 */

import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Interaction, InteractionQueryParams, AIInsight, PaginatedData } from '@/types';
import { interactionApi } from '@/services/interactionApi';
import { insightApi } from '@/services/insightApi';
import { InteractionFormData } from '@/schemas';

interface InteractionState {
  interactions: Interaction[];
  selectedInteraction: Interaction | null;
  total: number;
  totalPages: number;
  page: number;
  pageSize: number;
  filters: InteractionQueryParams;
  isLoading: boolean;
  isMutating: boolean;
  isGeneratingInsight: boolean;
  error: string | null;
}

const initialState: InteractionState = {
  interactions: [],
  selectedInteraction: null,
  total: 0,
  totalPages: 1,
  page: 1,
  pageSize: 10,
  filters: {},
  isLoading: false,
  isMutating: false,
  isGeneratingInsight: false,
  error: null,
};

/**
 * Async thunk to retrieve paginated interaction meeting logs with active filters.
 */
export const fetchInteractions = createAsyncThunk(
  'interactions/fetchInteractions',
  async (params: InteractionQueryParams | undefined, { rejectWithValue }) => {
    try {
      return await interactionApi.getInteractions(params);
    } catch (err: any) {
      return rejectWithValue(err.message || 'Failed to fetch interactions');
    }
  }
);

/**
 * Async thunk to retrieve a single interaction with AI insights by UUID.
 */
export const fetchInteractionById = createAsyncThunk(
  'interactions/fetchInteractionById',
  async (id: string, { rejectWithValue }) => {
    try {
      return await interactionApi.getInteraction(id);
    } catch (err: any) {
      return rejectWithValue(err.message || 'Failed to fetch interaction');
    }
  }
);

/**
 * Async thunk to record a new touchpoint interaction.
 */
export const createInteraction = createAsyncThunk(
  'interactions/createInteraction',
  async (data: InteractionFormData, { rejectWithValue }) => {
    try {
      return await interactionApi.createInteraction(data);
    } catch (err: any) {
      return rejectWithValue(err.message || 'Failed to record interaction');
    }
  }
);

/**
 * Async thunk to generate or re-generate AI intelligence insights for an interaction.
 */
export const generateInteractionInsight = createAsyncThunk(
  'interactions/generateInsight',
  async (
    { interactionId, regenerate }: { interactionId: string; regenerate?: boolean },
    { rejectWithValue }
  ) => {
    try {
      return await insightApi.generateInsight(interactionId, regenerate);
    } catch (err: any) {
      return rejectWithValue(err.message || 'Failed to generate AI insight');
    }
  }
);

export const interactionSlice = createSlice({
  name: 'interactions',
  initialState,
  reducers: {
    /** Update query filters and reset page to 1 */
    setInteractionFilters: (state, action: PayloadAction<InteractionQueryParams>) => {
      state.filters = action.payload;
      state.page = 1;
    },
    /** Set current pagination page index */
    setInteractionPage: (state, action: PayloadAction<number>) => {
      state.page = action.payload;
    },
    /** Clear active selected interaction */
    clearSelectedInteraction: (state) => {
      state.selectedInteraction = null;
    },
    /** Clear interaction error state */
    clearInteractionError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch List
      .addCase(fetchInteractions.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(
        fetchInteractions.fulfilled,
        (state, action: PayloadAction<PaginatedData<Interaction>>) => {
          state.isLoading = false;
          state.interactions = action.payload.items;
          state.total = action.payload.total;
          state.totalPages = action.payload.total_pages;
          state.page = action.payload.page;
          state.pageSize = action.payload.page_size;
        }
      )
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch Detail
      .addCase(fetchInteractionById.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(
        fetchInteractionById.fulfilled,
        (state, action: PayloadAction<Interaction>) => {
          state.isLoading = false;
          state.selectedInteraction = action.payload;
        }
      )
      .addCase(fetchInteractionById.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Create
      .addCase(createInteraction.pending, (state) => {
        state.isMutating = true;
        state.error = null;
      })
      .addCase(
        createInteraction.fulfilled,
        (state, action: PayloadAction<Interaction>) => {
          state.isMutating = false;
          state.interactions.unshift(action.payload);
        }
      )
      .addCase(createInteraction.rejected, (state, action) => {
        state.isMutating = false;
        state.error = action.payload as string;
      })
      // AI Insight Generation
      .addCase(generateInteractionInsight.pending, (state) => {
        state.isGeneratingInsight = true;
      })
      .addCase(
        generateInteractionInsight.fulfilled,
        (state, action: PayloadAction<AIInsight>) => {
          state.isGeneratingInsight = false;
          if (state.selectedInteraction) {
            state.selectedInteraction.ai_insight = action.payload;
          }
          const index = state.interactions.findIndex(
            (i) => i.id === action.payload.interaction_id
          );
          if (index !== -1) {
            state.interactions[index].ai_insight = action.payload;
          }
        }
      )
      .addCase(generateInteractionInsight.rejected, (state, action) => {
        state.isGeneratingInsight = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  setInteractionFilters,
  setInteractionPage,
  clearSelectedInteraction,
  clearInteractionError,
} = interactionSlice.actions;
export default interactionSlice.reducer;

