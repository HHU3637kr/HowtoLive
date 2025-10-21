/**
 * 会话管理 API
 */

import api from './api';
import { SessionInfo, SessionDetail, SessionCreate } from '../types';

/**
 * 创建新会话
 */
export const createSession = async (data?: SessionCreate): Promise<SessionInfo> => {
  const response = await api.post<SessionInfo>('/api/sessions', data || {});
  return response.data;
};

/**
 * 获取会话列表
 */
export const getSessions = async (): Promise<SessionInfo[]> => {
  const response = await api.get<SessionInfo[]>('/api/sessions');
  return response.data;
};

/**
 * 获取会话详情（包含历史消息）
 */
export const getSessionDetail = async (sessionId: string): Promise<SessionDetail> => {
  const response = await api.get<SessionDetail>(`/api/sessions/${sessionId}`);
  return response.data;
};

/**
 * 删除会话
 */
export const deleteSession = async (sessionId: string): Promise<void> => {
  await api.delete(`/api/sessions/${sessionId}`);
};

