/**
 * Redux Customer Management Slice.
 *
 * Manages customer listing, pagination, filtering, single selection, and CRUD operations.
 */

import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Customer, CustomerQueryParams, PaginatedData } from '@/types';
import { customerApi } from '@/services/customerApi';
import { CustomerFormData } from '@/schemas';

interface CustomerState {
  customers: Customer[];
  selectedCustomer: Customer | null;
  total: number;
  totalPages: number;
  page: number;
  pageSize: number;
  filters: CustomerQueryParams;
  isLoading: boolean;
  isMutating: boolean;
  error: string | null;
}

const initialState: CustomerState = {
  customers: [],
  selectedCustomer: null,
  total: 0,
  totalPages: 1,
  page: 1,
  pageSize: 10,
  filters: {},
  isLoading: false,
  isMutating: false,
  error: null,
};

/**
 * Async thunk to retrieve paginated customer accounts with active filters.
 */
export const fetchCustomers = createAsyncThunk(
  'customers/fetchCustomers',
  async (params: CustomerQueryParams | undefined, { rejectWithValue }) => {
    try {
      return await customerApi.getCustomers(params);
    } catch (err: any) {
      return rejectWithValue(err.message || 'Failed to fetch customers');
    }
  }
);

/**
 * Async thunk to fetch single customer details by UUID.
 */
export const fetchCustomerById = createAsyncThunk(
  'customers/fetchCustomerById',
  async (id: string, { rejectWithValue }) => {
    try {
      return await customerApi.getCustomer(id);
    } catch (err: any) {
      return rejectWithValue(err.message || 'Failed to fetch customer');
    }
  }
);

/**
 * Async thunk to create a new customer account.
 */
export const createCustomer = createAsyncThunk(
  'customers/createCustomer',
  async (data: CustomerFormData, { rejectWithValue }) => {
    try {
      return await customerApi.createCustomer(data);
    } catch (err: any) {
      return rejectWithValue(err.message || 'Failed to create customer');
    }
  }
);

/**
 * Async thunk to update an existing customer account.
 */
export const updateCustomer = createAsyncThunk(
  'customers/updateCustomer',
  async ({ id, data }: { id: string; data: Partial<CustomerFormData> }, { rejectWithValue }) => {
    try {
      return await customerApi.updateCustomer(id, data);
    } catch (err: any) {
      return rejectWithValue(err.message || 'Failed to update customer');
    }
  }
);

/**
 * Async thunk to delete a customer account.
 */
export const deleteCustomer = createAsyncThunk(
  'customers/deleteCustomer',
  async (id: string, { rejectWithValue }) => {
    try {
      await customerApi.deleteCustomer(id);
      return id;
    } catch (err: any) {
      return rejectWithValue(err.message || 'Failed to delete customer');
    }
  }
);

export const customerSlice = createSlice({
  name: 'customers',
  initialState,
  reducers: {
    /** Update query and filter parameters, resetting page index to 1 */
    setCustomerFilters: (state, action: PayloadAction<CustomerQueryParams>) => {
      state.filters = action.payload;
      state.page = 1;
    },
    /** Set current pagination page index */
    setCustomerPage: (state, action: PayloadAction<number>) => {
      state.page = action.payload;
    },
    /** Clear active selected customer */
    clearSelectedCustomer: (state) => {
      state.selectedCustomer = null;
    },
    /** Clear customer error message */
    clearCustomerError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch List
      .addCase(fetchCustomers.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchCustomers.fulfilled, (state, action: PayloadAction<PaginatedData<Customer>>) => {
        state.isLoading = false;
        state.customers = action.payload.items;
        state.total = action.payload.total;
        state.totalPages = action.payload.total_pages;
        state.page = action.payload.page;
        state.pageSize = action.payload.page_size;
      })
      .addCase(fetchCustomers.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch Detail
      .addCase(fetchCustomerById.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchCustomerById.fulfilled, (state, action: PayloadAction<Customer>) => {
        state.isLoading = false;
        state.selectedCustomer = action.payload;
      })
      .addCase(fetchCustomerById.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Mutations
      .addCase(createCustomer.pending, (state) => {
        state.isMutating = true;
        state.error = null;
      })
      .addCase(createCustomer.fulfilled, (state, action: PayloadAction<Customer>) => {
        state.isMutating = false;
        state.customers.unshift(action.payload);
      })
      .addCase(createCustomer.rejected, (state, action) => {
        state.isMutating = false;
        state.error = action.payload as string;
      })
      .addCase(updateCustomer.fulfilled, (state, action: PayloadAction<Customer>) => {
        state.isMutating = false;
        state.selectedCustomer = action.payload;
        const index = state.customers.findIndex((c) => c.id === action.payload.id);
        if (index !== -1) {
          state.customers[index] = action.payload;
        }
      })
      .addCase(deleteCustomer.fulfilled, (state, action: PayloadAction<string>) => {
        state.isMutating = false;
        state.customers = state.customers.filter((c) => c.id !== action.payload);
      });
  },
});

export const { setCustomerFilters, setCustomerPage, clearSelectedCustomer, clearCustomerError } =
  customerSlice.actions;
export default customerSlice.reducer;

