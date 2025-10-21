/**
 * 主应用组件
 */

import React, { useEffect, useState } from 'react';
import { LoginForm } from './components/Auth/LoginForm';
import { RegisterForm } from './components/Auth/RegisterForm';
import { SessionList } from './components/Sidebar/SessionList';
import { ChatWindow } from './components/Chat/ChatWindow';
import { useAuthStore } from './store/authStore';
import { getMe } from './services/auth';

function App() {
  const { token, setAuth, user } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [showRegister, setShowRegister] = useState(false);

  // 初始化：如果有 token，尝试获取用户信息
  useEffect(() => {
    const initAuth = async () => {
      if (token && !user) {
        try {
          const userData = await getMe();
          setAuth(token, userData);
        } catch (error) {
          console.error('获取用户信息失败:', error);
          // Token 无效，清除
          localStorage.removeItem('token');
        }
      }
      setLoading(false);
    };

    initAuth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 加载中
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  // 未登录：显示登录或注册表单
  if (!token || !user) {
    if (showRegister) {
      return (
        <RegisterForm 
          onSuccess={() => window.location.reload()} 
          onSwitchToLogin={() => setShowRegister(false)}
        />
      );
    } else {
      return (
        <LoginForm 
          onSuccess={() => window.location.reload()} 
          onSwitchToRegister={() => setShowRegister(true)}
        />
      );
    }
  }

  // 已登录：显示主应用
  return (
    <div className="flex h-screen overflow-hidden">
      <SessionList />
      <ChatWindow />
    </div>
  );
}

export default App;
