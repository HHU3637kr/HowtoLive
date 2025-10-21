/**
 * 输入区域组件
 */

import React, { useState } from 'react';
import { useChatStore } from '../../store/chatStore';
import { useSessionStore } from '../../store/sessionStore';
import { streamChat } from '../../services/chat';
import { Message } from '../../types';

export const InputArea: React.FC = () => {
  const [input, setInput] = useState('');
  const { addMessage, appendToLastMessage, setStreaming, isStreaming } = useChatStore();
  const { currentSessionId } = useSessionStore();

  const handleSend = async () => {
    if (!input.trim() || !currentSessionId || isStreaming) {
      return;
    }

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };

    // 添加用户消息
    addMessage(userMessage);
    setInput('');
    setStreaming(true);

    // 添加 AI 消息占位符
    const aiMessage: Message = {
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
    };
    addMessage(aiMessage);

    // 开始流式接收
    await streamChat(
      currentSessionId,
      userMessage.content,
      (chunk) => {
        if (chunk.type === 'token' && chunk.content) {
          appendToLastMessage(chunk.content);
        }
      },
      (error) => {
        console.error('聊天错误:', error);
        appendToLastMessage(`\n[错误: ${error}]`);
        setStreaming(false);
      },
      () => {
        setStreaming(false);
      }
    );
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-end space-x-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={currentSessionId ? "输入消息...（Enter 发送，Shift+Enter 换行）" : "请先创建或选择一个会话"}
            disabled={!currentSessionId || isStreaming}
            className="flex-1 resize-none border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            rows={3}
            maxLength={2000}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || !currentSessionId || isStreaming}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isStreaming ? (
              <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>
        <div className="text-xs text-gray-400 mt-2 text-center">
          {input.length}/2000
        </div>
      </div>
    </div>
  );
};

