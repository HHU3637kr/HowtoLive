/**
 * 聊天消息状态管理
 */

import { create } from 'zustand';
import { Message } from '../types';

interface ChatState {
  messages: Message[];
  isStreaming: boolean;
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  appendToLastMessage: (content: string) => void;
  setStreaming: (isStreaming: boolean) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isStreaming: false,
  setMessages: (messages) => set({ messages }),
  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, message] 
  })),
  appendToLastMessage: (content) => set((state) => {
    const messages = [...state.messages];
    if (messages.length > 0) {
      const lastMessage = { ...messages[messages.length - 1] };
      lastMessage.content += content;
      messages[messages.length - 1] = lastMessage;
    }
    return { messages };
  }),
  setStreaming: (isStreaming) => set({ isStreaming }),
  clearMessages: () => set({ messages: [] }),
}));

