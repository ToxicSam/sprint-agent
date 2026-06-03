import { useState, useRef, useEffect, useCallback } from 'react';
import { useStore } from '@/store';
import { cn } from '@/lib/utils';
import { Send, X, Bot, User, Sparkles, Wand2, FileText, BarChart3, Trash2 } from 'lucide-react';
import { sendMessage, getMessageHistory, clearHistory } from '@/api/agent';
import type { AgentMessage } from '@/types';

export default function AgentPanel() {
  const agentPanelOpen = useStore(s => s.agentPanelOpen);
  const toggleAgentPanel = useStore(s => s.toggleAgentPanel);
  const agentMessages = useStore(s => s.agentMessages);
  const agentTyping = useStore(s => s.agentTyping);
  const addAgentMessage = useStore(s => s.addAgentMessage);
  const setAgentMessages = useStore(s => s.setAgentMessages);
  const clearAgentMessages = useStore(s => s.clearAgentMessages);
  const setAgentTyping = useStore(s => s.setAgentTyping);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Load message history on mount
  useEffect(() => {
    let cancelled = false;
    getMessageHistory()
      .then(msgs => {
        if (!cancelled && msgs.length > 0) {
          setAgentMessages(msgs);
        }
      })
      .catch(err => {
        console.error('Failed to load message history:', err);
      });
    return () => { cancelled = true; };
  }, [setAgentMessages]);

  // Auto-scroll on new messages or typing indicator
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [agentMessages, agentTyping]);

  const handleSend = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    // Optimistically add user message
    const userMsg: AgentMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: trimmed,
      created_at: new Date().toISOString(),
    };
    addAgentMessage(userMsg);
    setInput('');
    setIsLoading(true);
    setAgentTyping(true);

    try {
      const agentMsg = await sendMessage(trimmed);
      addAgentMessage(agentMsg);
    } catch (err) {
      console.error('Failed to send message:', err);
      addAgentMessage({
        id: `msg-error-${Date.now()}`,
        role: 'system',
        content: 'Sorry, something went wrong. Please try again.',
        created_at: new Date().toISOString(),
      });
    } finally {
      setIsLoading(false);
      setAgentTyping(false);
    }
  }, [input, isLoading, addAgentMessage, setAgentTyping]);

  const handleClear = useCallback(async () => {
    try {
      await clearHistory();
      clearAgentMessages();
    } catch (err) {
      console.error('Failed to clear history:', err);
    }
  }, [clearAgentMessages]);

  return (
    <>
      {/* Collapsed state: icon button */}
      {!agentPanelOpen && (
        <button
          onClick={toggleAgentPanel}
          className="fixed right-0 top-12 bottom-8 z-[30] w-12 flex items-center justify-center bg-[hsl(var(--card))] border-l border-[hsl(var(--border))] hover:bg-[hsl(var(--accent))] transition-colors"
          title="Open Agent Panel"
        >
          <div className="relative">
            <Bot className="w-5 h-5 text-violet-500" />
            <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          </div>
        </button>
      )}

      {/* Expanded panel */}
      {agentPanelOpen && (
        <aside className="fixed right-0 top-12 bottom-8 z-[50] w-[320px] flex flex-col bg-[hsl(var(--card))] border-l border-[hsl(var(--border))]">
          {/* Header */}
          <div className="flex items-center justify-between px-4 h-12 border-b border-[hsl(var(--border))] shrink-0">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center">
                <Sparkles className="w-3.5 h-3.5 text-white" />
              </div>
              <span className="font-semibold text-sm">Sprint Agent</span>
              <span className="w-2 h-2 bg-green-500 rounded-full" />
            </div>
            <div className="flex items-center gap-1">
              {agentMessages.length > 0 && (
                <button
                  onClick={handleClear}
                  className="p-1.5 rounded-md hover:bg-[hsl(var(--accent))] transition-colors"
                  title="Clear chat"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              )}
              <button
                onClick={toggleAgentPanel}
                className="p-1.5 rounded-md hover:bg-[hsl(var(--accent))] transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Quick actions */}
          <div className="flex gap-2 px-3 py-2 border-b border-[hsl(var(--border))] shrink-0">
            {[
              { icon: Wand2, label: 'Quick fix' },
              { icon: FileText, label: 'Summarize' },
              { icon: BarChart3, label: 'Analyze' },
            ].map(action => (
              <button
                key={action.label}
                onClick={() => {
                  setInput(`Help me ${action.label.toLowerCase()}`);
                }}
                disabled={isLoading}
                className="flex items-center gap-1 px-2 py-1 rounded-md text-xs bg-[hsl(var(--accent))] hover:bg-violet-500/10 hover:text-violet-600 transition-colors disabled:opacity-40"
              >
                <action.icon className="w-3 h-3" />
                {action.label}
              </button>
            ))}
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-3 min-h-0">
            {agentMessages.length === 0 && (
              <div className="text-center py-8">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center mx-auto mb-3">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <p className="text-sm font-medium">Sprint Agent</p>
                <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">Ask me anything about your sprint</p>
              </div>
            )}
            {agentMessages.map(msg => (
              <div
                key={msg.id}
                className={cn(
                  'flex gap-2',
                  msg.role === 'user' ? 'flex-row-reverse' : ''
                )}
              >
                <div className={cn(
                  'w-6 h-6 rounded-full flex items-center justify-center shrink-0',
                  msg.role === 'user'
                    ? 'bg-[hsl(var(--accent))]'
                    : msg.role === 'system'
                    ? 'bg-red-500/20'
                    : 'bg-gradient-to-br from-violet-500 to-pink-500'
                )}>
                  {msg.role === 'user'
                    ? <User className="w-3 h-3" />
                    : msg.role === 'system'
                    ? <X className="w-3 h-3 text-red-500" />
                    : <Bot className="w-3 h-3 text-white" />
                  }
                </div>
                <div className={cn(
                  'rounded-lg px-3 py-2 text-sm max-w-[85%]',
                  msg.role === 'user'
                    ? 'bg-violet-500 text-white'
                    : msg.role === 'system'
                    ? 'bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20'
                    : 'bg-[hsl(var(--accent))] text-[hsl(var(--foreground))]'
                )}>
                  {msg.content}
                </div>
              </div>
            ))}
            {agentTyping && (
              <div className="flex gap-2">
                <div className="w-6 h-6 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center shrink-0">
                  <Bot className="w-3 h-3 text-white" />
                </div>
                <div className="bg-[hsl(var(--accent))] rounded-lg px-3 py-2 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-[hsl(var(--muted-foreground))] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-1.5 h-1.5 bg-[hsl(var(--muted-foreground))] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-1.5 h-1.5 bg-[hsl(var(--muted-foreground))] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-3 border-t border-[hsl(var(--border))] shrink-0">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter') handleSend();
                }}
                placeholder={isLoading ? 'Waiting for response...' : 'Ask the agent...'}
                disabled={isLoading}
                className="flex-1 h-9 px-3 rounded-md border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/30 disabled:opacity-50"
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className="h-9 w-9 flex items-center justify-center rounded-md bg-violet-500 text-white hover:bg-violet-600 disabled:opacity-40 disabled:hover:bg-violet-500 transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </aside>
      )}
    </>
  );
}
