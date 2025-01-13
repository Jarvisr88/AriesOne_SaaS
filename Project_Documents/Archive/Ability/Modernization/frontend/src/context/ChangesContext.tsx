import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useToast } from '@chakra-ui/react';

// Types
export interface Change {
  id: string;
  type: 'create' | 'update' | 'delete';
  entity: string;
  entityId: string;
  field?: string;
  oldValue?: any;
  newValue?: any;
  timestamp: string;
  userId: string;
  metadata?: Record<string, any>;
}

interface ChangesState {
  changes: Change[];
  pendingChanges: Change[];
  isLoading: boolean;
  error: Error | null;
  lastSyncTimestamp: string | null;
}

type ChangesAction =
  | { type: 'ADD_CHANGE'; payload: Change }
  | { type: 'ADD_PENDING_CHANGE'; payload: Change }
  | { type: 'REMOVE_PENDING_CHANGE'; payload: string }
  | { type: 'SET_CHANGES'; payload: Change[] }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: Error | null }
  | { type: 'SET_LAST_SYNC'; payload: string }
  | { type: 'CLEAR_CHANGES' };

interface ChangesContextType extends ChangesState {
  trackChange: (change: Omit<Change, 'id' | 'timestamp'>) => Promise<void>;
  syncChanges: () => Promise<void>;
  clearChanges: () => void;
  retryFailedChanges: () => Promise<void>;
}

// Context
const ChangesContext = createContext<ChangesContextType | undefined>(undefined);

// Reducer
const changesReducer = (state: ChangesState, action: ChangesAction): ChangesState => {
  switch (action.type) {
    case 'ADD_CHANGE':
      return {
        ...state,
        changes: [action.payload, ...state.changes].sort(
          (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        ),
      };
    case 'ADD_PENDING_CHANGE':
      return {
        ...state,
        pendingChanges: [...state.pendingChanges, action.payload],
      };
    case 'REMOVE_PENDING_CHANGE':
      return {
        ...state,
        pendingChanges: state.pendingChanges.filter(
          (change) => change.id !== action.payload
        ),
      };
    case 'SET_CHANGES':
      return {
        ...state,
        changes: action.payload.sort(
          (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        ),
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
      };
    case 'SET_LAST_SYNC':
      return {
        ...state,
        lastSyncTimestamp: action.payload,
      };
    case 'CLEAR_CHANGES':
      return {
        ...state,
        changes: [],
        pendingChanges: [],
        lastSyncTimestamp: null,
      };
    default:
      return state;
  }
};

// Provider
interface ChangesProviderProps {
  children: React.ReactNode;
  websocketUrl: string;
}

export const ChangesProvider: React.FC<ChangesProviderProps> = ({
  children,
  websocketUrl,
}) => {
  const toast = useToast();
  const [state, dispatch] = useReducer(changesReducer, {
    changes: [],
    pendingChanges: [],
    isLoading: false,
    error: null,
    lastSyncTimestamp: null,
  });

  // WebSocket connection
  const { sendMessage, lastMessage, connectionStatus } = useWebSocket(websocketUrl);

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (lastMessage?.type === 'change') {
      const change = lastMessage.data as Change;
      dispatch({ type: 'ADD_CHANGE', payload: change });
      
      toast({
        title: 'Change Detected',
        description: `${change.type} operation on ${change.entity}`,
        status: 'info',
        duration: 3000,
        isClosable: true,
      });
    }
  }, [lastMessage, toast]);

  // Handle WebSocket connection status
  useEffect(() => {
    if (connectionStatus === 'disconnected') {
      toast({
        title: 'Connection Lost',
        description: 'Trying to reconnect...',
        status: 'warning',
        duration: null,
      });
    } else if (connectionStatus === 'connected') {
      toast.closeAll();
      toast({
        title: 'Connected',
        description: 'Real-time updates active',
        status: 'success',
        duration: 3000,
      });
    }
  }, [connectionStatus, toast]);

  const trackChange = async (
    changeData: Omit<Change, 'id' | 'timestamp'>
  ): Promise<void> => {
    try {
      const change: Change = {
        ...changeData,
        id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
      };

      dispatch({ type: 'ADD_PENDING_CHANGE', payload: change });

      // Send change to server
      await sendMessage({
        type: 'track_change',
        data: change,
      });

      dispatch({ type: 'REMOVE_PENDING_CHANGE', payload: change.id });
      dispatch({ type: 'ADD_CHANGE', payload: change });

    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error as Error });
      toast({
        title: 'Error Tracking Change',
        description: (error as Error).message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const syncChanges = async (): Promise<void> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });

      const response = await fetch('/api/changes/sync', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          lastSyncTimestamp: state.lastSyncTimestamp,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to sync changes');
      }

      const { changes, timestamp } = await response.json();
      dispatch({ type: 'SET_CHANGES', payload: changes });
      dispatch({ type: 'SET_LAST_SYNC', payload: timestamp });

    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error as Error });
      toast({
        title: 'Sync Failed',
        description: (error as Error).message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const retryFailedChanges = async (): Promise<void> => {
    const failedChanges = [...state.pendingChanges];
    dispatch({ type: 'CLEAR_CHANGES' });

    for (const change of failedChanges) {
      await trackChange(change);
    }
  };

  const clearChanges = () => {
    dispatch({ type: 'CLEAR_CHANGES' });
  };

  return (
    <ChangesContext.Provider
      value={{
        ...state,
        trackChange,
        syncChanges,
        clearChanges,
        retryFailedChanges,
      }}
    >
      {children}
    </ChangesContext.Provider>
  );
};

// Hook
export const useChanges = () => {
  const context = useContext(ChangesContext);
  if (context === undefined) {
    throw new Error('useChanges must be used within a ChangesProvider');
  }
  return context;
};
