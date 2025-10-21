
/**
 * 聊天 API - SSE 流式接口
 */

import { API_BASE_URL } from '../config';
import { StreamChunk } from '../types';

/**
 * 流式聊天
 * 使用 Server-Sent Events (SSE) 接收实时响应
 */
export const streamChat = async (
  sessionId: string,
  message: string,
  onChunk: (chunk: StreamChunk) => void,
  onError: (error: string) => void,
  onComplete: () => void
): Promise<void> => {
  const token = localStorage.getItem('token');
  if (!token) {
    onError('未登录');
    return;
  }

  const url = `${API_BASE_URL}/api/chat/stream`;
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ 
        session_id: sessionId, 
        message 
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      onError(`HTTP ${response.status}: ${errorText}`);
      return;
    }

    const reader = response.body?.getReader();
    if (!reader) {
      onError('无法读取响应流');
      return;
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        break;
      }

      // 解码并追加到缓冲区
      buffer += decoder.decode(value, { stream: true });
      
      // 按行处理
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // 保留最后不完整的行

      for (const line of lines) {
        // 跳过空行
        if (!line.trim()) {
          continue;
        }
        
        if (line.startsWith('data: ')) {
          const data = line.slice(6).trim();
          
          // SSE 结束标记
          if (data === '[DONE]') {
            onComplete();
            return;
          }

          try {
            const chunk: StreamChunk = JSON.parse(data);
            onChunk(chunk);
            
            // 处理错误类型
            if (chunk.type === 'error') {
              onError(chunk.error || '未知错误');
              return;
            }
            
            // 处理完成类型
            if (chunk.type === 'done') {
              onComplete();
              return;
            }
          } catch (e) {
            console.error('解析 SSE 数据失败:', e);
            console.error('原始行:', JSON.stringify(line));
            console.error('提取的数据:', JSON.stringify(data));
          }
        }
      }
    }

    onComplete();
  } catch (error: any) {
    onError(error.message || '网络错误');
  }
};

