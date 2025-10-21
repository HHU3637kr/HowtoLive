/**
 * 会话列表项组件
 */

import React from 'react';
import { SessionInfo } from '../../types';

interface SessionItemProps {
  session: SessionInfo;
  isActive: boolean;
  onClick: () => void;
  onDelete: () => void;
}

export const SessionItem: React.FC<SessionItemProps> = ({ 
  session, 
  isActive, 
  onClick, 
  onDelete 
}) => {
  return (
    <div
      className={`
        group flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer
        ${isActive 
          ? 'bg-gray-200 text-gray-900' 
          : 'text-gray-700 hover:bg-gray-100'
        }
      `}
      onClick={onClick}
    >
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium truncate">
          {session.title}
        </div>
        <div className="text-xs text-gray-500">
          {session.message_count} 条消息
        </div>
      </div>
      <button
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
        className="ml-2 p-1 opacity-0 group-hover:opacity-100 hover:bg-gray-300 rounded transition-opacity"
        title="删除会话"
      >
        <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      </button>
    </div>
  );
};

