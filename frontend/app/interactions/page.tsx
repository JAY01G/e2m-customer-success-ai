'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  fetchInteractions,
  setInteractionFilters,
  setInteractionPage,
} from '@/store/slices/interactionSlice';
import { interactionApi } from '@/services/interactionApi';
import { useToast } from '@/components/providers/ToastProvider';
import { InteractionQueryParams } from '@/types';
import { AppLayout } from '@/components/layout/AppLayout';
import { InteractionTable } from '@/components/interactions/InteractionTable';
import { InteractionFilters } from '@/components/interactions/InteractionFilters';
import { Pagination } from '@/components/ui/Pagination';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Spinner } from '@/components/ui/Spinner';
import { Plus } from 'lucide-react';

export default function InteractionsPage() {
  const dispatch = useAppDispatch();
  const { toast } = useToast();
  const { interactions, total, totalPages, page, pageSize, filters, isLoading } =
    useAppSelector((state) => state.interactions);
  const { user } = useAppSelector((state) => state.auth);

  const [deleteModalState, setDeleteModalState] = useState<{
    isOpen: boolean;
    id: string;
    title: string;
  }>({ isOpen: false, id: '', title: '' });
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    dispatch(fetchInteractions({ ...filters, page, page_size: pageSize }));
  }, [dispatch, page, pageSize, filters]);

  const handleFilterChange = (newFilters: InteractionQueryParams) => {
    dispatch(setInteractionFilters(newFilters));
  };

  const handlePageChange = (newPage: number) => {
    dispatch(setInteractionPage(newPage));
  };

  const handleDeletePrompt = (id: string, title: string) => {
    setDeleteModalState({ isOpen: true, id, title });
  };

  const handleConfirmDelete = async () => {
    if (!deleteModalState.id) return;
    setIsDeleting(true);
    const targetTitle = deleteModalState.title;
    try {
      await interactionApi.deleteInteraction(deleteModalState.id);
      toast.success('Interaction Deleted', `Meeting "${targetTitle}" was removed successfully.`);
      setDeleteModalState({ isOpen: false, id: '', title: '' });
      dispatch(fetchInteractions({ ...filters, page, page_size: pageSize }));
    } catch (err: any) {
      const msg = err.message || 'Failed to delete interaction';
      toast.error('Deletion Failed', msg);
    } finally {
      setIsDeleting(false);
    }
  };

  const isCsmOrAdmin =
    user?.role === 'ADMIN' || user?.role === 'CUSTOMER_SUCCESS_MANAGER';

  return (
    <AppLayout>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div className="space-y-1">
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
            Customer Interactions
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground">
            Review meeting logs, call notes, and automated AI insight extractions
          </p>
        </div>

        {isCsmOrAdmin && (
          <Link href="/interactions/new">
            <Button variant="primary" size="md" leftIcon={<Plus className="h-4 w-4" />}>
              Log Meeting Notes
            </Button>
          </Link>
        )}
      </div>

      <InteractionFilters
        onFilterChange={handleFilterChange}
        initialFilters={filters}
      />

      {isLoading ? (
        <div className="py-16">
          <Spinner size={36} label="Loading interactions..." />
        </div>
      ) : (
        <div className="space-y-4">
          <InteractionTable
            interactions={interactions}
            onDelete={handleDeletePrompt}
            isLoading={isLoading}
          />

          <Pagination
            currentPage={page}
            totalPages={totalPages}
            onPageChange={handlePageChange}
            totalItems={total}
            pageSize={pageSize}
          />
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteModalState.isOpen}
        onClose={() => setDeleteModalState({ isOpen: false, id: '', title: '' })}
        title="Confirm Interaction Deletion"
      >
        <p className="text-sm text-muted-foreground leading-relaxed">
          Are you sure you want to permanently delete meeting log{' '}
          <strong className="text-foreground">&quot;{deleteModalState.title}&quot;</strong>?
          The associated AI insights will also be removed.
        </p>

        <div className="flex items-center justify-end gap-3 mt-6 pt-4 border-t border-border">
          <Button
            variant="secondary"
            onClick={() =>
              setDeleteModalState({ isOpen: false, id: '', title: '' })
            }
            disabled={isDeleting}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleConfirmDelete}
            isLoading={isDeleting}
          >
            Delete Interaction
          </Button>
        </div>
      </Modal>
    </AppLayout>
  );
}
