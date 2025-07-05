from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ConversationMessage:
    user_id: int
    content: str
    is_bot_message: bool
    timestamp: datetime

class ConversationCache:
    def __init__(self, max_age_minutes: int = 60):
        self._conversations: Dict[int, List[ConversationMessage]] = {}
        self._max_age = timedelta(minutes=max_age_minutes)
    
    def add_message(self, user_id: int, content: str, is_bot_message: bool = False):
        if user_id not in self._conversations:
            self._conversations[user_id] = []
        
        message = ConversationMessage(
            user_id=user_id,
            content=content,
            is_bot_message=is_bot_message,
            timestamp=datetime.now()
        )
        
        self._conversations[user_id].append(message)
        
        self._cleanup_old_messages(user_id)
    
    def get_conversation(self, user_id: int) -> List[ConversationMessage]:
        if user_id not in self._conversations:
            return []
        
        self._cleanup_old_messages(user_id)
        return self._conversations[user_id]
    
    def get_recent_context(self, user_id: int, max_messages: int = 10) -> str:
        messages = self.get_conversation(user_id)
        
        if not messages:
            return ""
        
        recent_messages = messages[-max_messages:]
        
        context_lines = []
        for msg in recent_messages:
            role = "Bot" if msg.is_bot_message else "User"
            context_lines.append(f"{role}: {msg.content}")
        
        return "\n".join(context_lines)
    
    def clear_user_conversation(self, user_id: int):
        if user_id in self._conversations:
            del self._conversations[user_id]
    
    def clear_all_conversations(self):
        self._conversations.clear()
    
    def _cleanup_old_messages(self, user_id: int):
        if user_id not in self._conversations:
            return
        
        cutoff_time = datetime.now() - self._max_age
        self._conversations[user_id] = [
            msg for msg in self._conversations[user_id]
            if msg.timestamp > cutoff_time
        ]

        if not self._conversations[user_id]:
            del self._conversations[user_id]
    
    def get_conversation_count(self, user_id: int) -> int:
        return len(self.get_conversation(user_id))

conversation_cache = ConversationCache(max_age_minutes=60)
