/**
 * 用户认证 API
 */

import api from './api';
import { User, Token, UserRegister, UserLogin } from '../types';

/**
 * 用户注册
 */
export const register = async (data: UserRegister): Promise<Token> => {
  const response = await api.post<Token>('/api/auth/register', data);
  return response.data;
};

/**
 * 用户登录
 */
export const login = async (data: UserLogin): Promise<Token> => {
  const response = await api.post<Token>('/api/auth/login', data);
  return response.data;
};

/**
 * 获取当前用户信息
 */
export const getMe = async (): Promise<User> => {
  const response = await api.get<User>('/api/auth/me');
  return response.data;
};

