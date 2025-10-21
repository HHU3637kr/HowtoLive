/**
 * 聊天窗口主组件
 */

import React from 'react';
import { MessageList } from './MessageList';
import { InputArea } from './InputArea';
import { useSessionStore } from '../../store/sessionStore';

export const ChatWindow: React.FC = () => {
  const { currentSessionId, sessions } = useSessionStore();
  const currentSession = sessions.find(s => s.session_id === currentSessionId);

  return (
    <div className="flex-1 flex flex-col h-screen bg-white">
      {/* 头部 */}
      <div className="border-b border-gray-200 px-6 py-4 bg-white">
        <h1 className="text-lg font-semibold text-gray-900">
          {currentSession?.title || 'HowToLive 聊天助手'}
        </h1>
        {currentSession && (
          <p className="text-sm text-gray-500 mt-1">
            会话 ID: {currentSession.session_id}
          </p>
        )}
      </div>

      {/* 消息列表 */}
      <MessageList />

      {/* 输入区域 */}
      <InputArea />
    </div>
  );
};

