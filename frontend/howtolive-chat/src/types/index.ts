/**
 * TypeScript 类型定义
 * 基于后端 API 模型（backend/api/models.py）
 */

// ============ 用户认证相关 ============

export interface User {
  id: number;
  username: string;
  email?: string;
  created_at: string;
  last_login?: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface UserRegister {
  username: string;
  password: string;
  email?: string;
}

export interface UserLogin {
  username: string;
  password: string;
}

// ============ 会话相关 ============

export interface SessionInfo {
  session_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface SessionDetail {
  session_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

export interface SessionCreate {
  title?: string;
}

// ============ 聊天相关 ============

export interface Message {
  role: string;  // "user" 或 agent 名称
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  session_id: string;
  message: string;
}

// ============ SSE 流式响应 ============

export interface StreamChunk {
  type: 'start' | 'token' | 'done' | 'error';
  content?: string;
  session_id?: string;
  message_id?: string;
  error?: string;
}

