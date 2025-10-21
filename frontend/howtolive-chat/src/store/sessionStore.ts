/**
 * 会话状态管理
 */

import { create } from 'zustand';
import { SessionInfo } from '../types';

interface SessionState {
  sessions: SessionInfo[];
  currentSessionId: string | null;
  setSessions: (sessions: SessionInfo[]) => void;
  setCurrentSession: (sessionId: string) => void;
  addSession: (session: SessionInfo) => void;
  removeSession: (sessionId: string) => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  sessions: [],
  currentSessionId: null,
  setSessions: (sessions) => set({ sessions }),
  setCurrentSession: (sessionId) => set({ currentSessionId: sessionId }),
  addSession: (session) => set((state) => ({ 
    sessions: [session, ...state.sessions] 
  })),
  removeSession: (sessionId) => set((state) => ({
    sessions: state.sessions.filter(s => s.session_id !== sessionId),
    currentSessionId: state.currentSessionId === sessionId ? null : state.currentSessionId,
  })),
}));

