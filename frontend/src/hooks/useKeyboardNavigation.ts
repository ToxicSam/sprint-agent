import { useCallback, useRef } from 'react';

interface KeyboardNavOptions {
  onSubmit?: () => void;
  onFillFromYesterday?: () => void;
}

/**
 * Excel-like keyboard navigation for a table of inputs.
 * - Tab: next cell (right)
 * - Shift+Tab: previous cell (left)
 * - Enter: next row, same column
 * - Shift+Enter: previous row, same column
 * - Ctrl+Enter: submit all
 */
export function useKeyboardNavigation(options: KeyboardNavOptions = {}) {
  const cellRefs = useRef<Map<string, HTMLInputElement>>(new Map());

  const registerCell = useCallback(
    (rowId: string, colId: string, el: HTMLInputElement | null) => {
      const key = `${rowId}-${colId}`;
      if (el) {
        cellRefs.current.set(key, el);
      } else {
        cellRefs.current.delete(key);
      }
    },
    []
  );

  const focusCell = useCallback((rowId: string, colId: string) => {
    const key = `${rowId}-${colId}`;
    const el = cellRefs.current.get(key);
    if (el) {
      el.focus();
      el.select();
      return true;
    }
    return false;
  }, []);

  const handleKeyDown = useCallback(
    (
      e: React.KeyboardEvent<HTMLInputElement>,
      rowIds: string[],
      colIds: string[],
      currentRowId: string,
      currentColId: string
    ) => {
      const rowIdx = rowIds.indexOf(currentRowId);
      const colIdx = colIds.indexOf(currentColId);
      if (rowIdx === -1 || colIdx === -1) return;

      // Ctrl+Enter: submit
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        options.onSubmit?.();
        return;
      }

      // Enter: next row, same column
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        const nextRowIdx = rowIdx + 1;
        if (nextRowIdx < rowIds.length) {
          focusCell(rowIds[nextRowIdx], currentColId);
        }
        return;
      }

      // Shift+Enter: previous row, same column
      if (e.key === 'Enter' && e.shiftKey) {
        e.preventDefault();
        const prevRowIdx = rowIdx - 1;
        if (prevRowIdx >= 0) {
          focusCell(rowIds[prevRowIdx], currentColId);
        }
        return;
      }

      // Tab: next cell (right, wrap to next row)
      if (e.key === 'Tab' && !e.shiftKey) {
        // Let default tab happen if there's a next cell in the same row
        const nextColIdx = colIdx + 1;
        if (nextColIdx < colIds.length) {
          e.preventDefault();
          focusCell(currentRowId, colIds[nextColIdx]);
        } else {
          // Wrap to next row's first editable cell
          const nextRowIdx = rowIdx + 1;
          if (nextRowIdx < rowIds.length) {
            e.preventDefault();
            focusCell(rowIds[nextRowIdx], colIds[0]);
          }
        }
        return;
      }

      // Shift+Tab: previous cell (left, wrap to previous row)
      if (e.key === 'Tab' && e.shiftKey) {
        const prevColIdx = colIdx - 1;
        if (prevColIdx >= 0) {
          e.preventDefault();
          focusCell(currentRowId, colIds[prevColIdx]);
        } else {
          const prevRowIdx = rowIdx - 1;
          if (prevRowIdx >= 0) {
            e.preventDefault();
            focusCell(rowIds[prevRowIdx], colIds[colIds.length - 1]);
          }
        }
        return;
      }

      // Y key: Fill from yesterday (when not in input)
      if (e.key === 'y' || e.key === 'Y') {
        if (!e.ctrlKey && !e.metaKey && !e.altKey) {
          options.onFillFromYesterday?.();
        }
      }
    },
    [focusCell, options]
  );

  return {
    registerCell,
    focusCell,
    handleKeyDown,
  };
}
