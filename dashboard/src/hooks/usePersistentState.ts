import { useState, useEffect } from 'react';

export function usePersistentState<T>(key: string, initialValue: T): [T, (value: T | ((prev: T) => T)) => void] {
  const [state, setState] = useState<T>(() => {
    try {
      const stored = localStorage.getItem(`nsoc_${key}`);
      return stored ? JSON.parse(stored) : initialValue;
    } catch {
      return initialValue;
    }
  });
  useEffect(() => {
    try { localStorage.setItem(`nsoc_${key}`, JSON.stringify(state)); } catch {}
  }, [key, state]);
  return [state, setState];
}
