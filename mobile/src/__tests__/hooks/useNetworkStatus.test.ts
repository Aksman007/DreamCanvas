/**
 * useNetworkStatus Hook Tests
 */

import { renderHook, act } from '@testing-library/react-native';
import NetInfo from '@react-native-community/netinfo';
import { useNetworkStatus } from '../../hooks/useNetworkStatus';

describe('useNetworkStatus', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should return initial connected state', () => {
    const { result } = renderHook(() => useNetworkStatus());
    
    expect(result.current.isConnected).toBe(true);
    expect(result.current.isOffline).toBe(false);
  });

  it('should subscribe to network changes on mount', () => {
    renderHook(() => useNetworkStatus());
    
    expect(NetInfo.addEventListener).toHaveBeenCalled();
  });

  it('should unsubscribe on unmount', () => {
    const unsubscribe = jest.fn();
    (NetInfo.addEventListener as jest.Mock).mockReturnValue(unsubscribe);
    
    const { unmount } = renderHook(() => useNetworkStatus());
    unmount();
    
    expect(unsubscribe).toHaveBeenCalled();
  });
});