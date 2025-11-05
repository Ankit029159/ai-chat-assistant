import { useCallback, useState, useEffect } from 'react';
import { CellMeasurer, CellMeasurerCache } from 'react-virtualized';

// Hook wrapping react-virtualized List for dynamic row heights
export default function useVirtualizedMessages(messages) {
  const cache = new CellMeasurerCache({
    fixedWidth: true,
    minHeight: 60,
  });

  const rowRenderer = useCallback(
    ({ index, key, parent, style }) => {
      const message = messages[index];
      return (
        <CellMeasurer cache={cache} columnIndex={0} key={key} parent={parent} rowIndex={index}>
          {({ measure }) => (
            <div style={style} onLoad={measure}>
              {/* MessageBubble component must be imported and used here */}
            </div>
          )}
        </CellMeasurer>
      );
    },
    [messages, cache]
  );

  return { rowRenderer, cache };
}
