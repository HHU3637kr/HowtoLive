/**
 * 会话列表侧边栏组件
 */

import React, { useEffect, useState } from 'react';
import { useSessionStore } from '../../store/sessionStore';
import { useChatStore } from '../../store/chatStore';
import { useAuthStore } from '../../store/authStore';
import { getSessions, createSession, deleteSession, getSessionDetail } from '../../services/sessions';
import { SessionItem } from './SessionItem';

export const SessionList: React.FC = () => {
  const { sessions, currentSessionId, setSessions, setCurrentSession, addSession, removeSession } = useSessionStore();
  const { setMessages, clearMessages } = useChatStore();
  const { logout } = useAuthStore();
  const [loading, setLoading] = useState(false);

  // 加载会话列表
  useEffect(() => {
    loadSessions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadSessions = async () => {
    try {
      const data = await getSessions();
      setSessions(data);
      
      // 如果有会话且当前没有选中会话，自动选中第一个
      if (data.length > 0 && !currentSessionId) {
        await loadSessionMessages(data[0].session_id);
      }
    } catch (error) {
      console.error('加载会话列表失败:', error);
    }
  };

  // 创建新会话
  const handleCreateSession = async () => {
    if (loading) return;
    setLoading(true);
    
    try {
      const newSession = await createSession();
      addSession(newSession);
      setCurrentSession(newSession.session_id);
      clearMessages();
    } catch (error) {
      console.error('创建会话失败:', error);
      alert('创建会话失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 加载会话消息
  const loadSessionMessages = async (sessionId: string) => {
    try {
      const detail = await getSessionDetail(sessionId);
      setCurrentSession(sessionId);
      setMessages(detail.messages);
    } catch (error) {
      console.error('加载会话消息失败:', error);
      alert('加载会话消息失败');
    }
  };

  // 删除会话
  const handleDeleteSession = async (sessionId: string) => {
    if (!window.confirm('确定要删除这个会话吗？')) {
      return;
    }

    try {
      await deleteSession(sessionId);
      removeSession(sessionId);
      
      // 如果删除的是当前会话，清空消息
      if (sessionId === currentSessionId) {
        clearMessages();
        
        // 如果还有其他会话，自动选中第一个
        const remainingSessions = sessions.filter(s => s.session_id !== sessionId);
        if (remainingSessions.length > 0) {
          await loadSessionMessages(remainingSessions[0].session_id);
        }
      }
    } catch (error) {
      console.error('删除会话失败:', error);
      alert('删除会话失败');
    }
  };

  return (
    <div className="w-64 bg-gray-50 border-r border-gray-200 flex flex-col h-screen">
      {/* 头部 */}
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={handleCreateSession}
          disabled={loading}
          className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          新建对话
        </button>
      </div>

      {/* 会话列表 */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {sessions.length === 0 ? (
          <div className="text-center text-gray-500 text-sm py-8">
            暂无会话<br />点击上方按钮创建新对话
          </div>
        ) : (
          sessions.map((session) => (
            <SessionItem
              key={session.session_id}
              session={session}
              isActive={session.session_id === currentSessionId}
              onClick={() => loadSessionMessages(session.session_id)}
              onDelete={() => handleDeleteSession(session.session_id)}
            />
          ))
        )}
      </div>

      {/* 底部用户信息 */}
      <div className="p-4 border-t border-gray-200">
        <button
          onClick={logout}
          className="w-full flex items-center justify-center px-4 py-2 text-gray-700 hover:bg-gray-200 rounded-lg transition-colors"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          退出登录
        </button>
      </div>
    </div>
  );
};

