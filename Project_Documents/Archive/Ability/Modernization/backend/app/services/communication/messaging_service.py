from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
from fastapi import HTTPException, WebSocket
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.core.logging import logger
from app.models.communication import (
    Message,
    MessageThread,
    MessageParticipant,
    MessageAttachment
)

class MessagingService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.db = db
        self.active_connections: Dict[str, WebSocket] = {}

    async def create_thread(
        self,
        participants: List[Dict],
        thread_type: str = "direct"
    ) -> MessageThread:
        """Create new message thread"""
        try:
            # Create thread
            thread = await MessageThread.create(
                type=thread_type,
                created_at=datetime.now()
            )
            
            # Add participants
            for participant in participants:
                await MessageParticipant.create(
                    thread_id=thread.id,
                    user_id=participant["user_id"],
                    role=participant.get("role", "member"),
                    created_at=datetime.now()
                )
            
            return thread
        except Exception as e:
            logger.error(f"Failed to create thread: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def send_message(
        self,
        thread_id: str,
        sender_id: str,
        content: Dict,
        attachments: Optional[List[Dict]] = None
    ) -> Message:
        """Send message in thread"""
        try:
            # Validate thread participation
            await self._validate_participant(thread_id, sender_id)
            
            # Process attachments
            processed_attachments = await self._process_attachments(
                attachments
            ) if attachments else []
            
            # Create message
            message = await Message.create(
                thread_id=thread_id,
                sender_id=sender_id,
                content=content["text"],
                content_type=content.get("type", "text"),
                metadata=content.get("metadata", {}),
                created_at=datetime.now()
            )
            
            # Link attachments
            for attachment in processed_attachments:
                attachment.message_id = message.id
                await attachment.save()
            
            # Notify participants
            await self._notify_participants(
                thread_id,
                message,
                sender_id
            )
            
            return message
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_thread_messages(
        self,
        thread_id: str,
        user_id: str,
        limit: int = 50,
        before_id: Optional[str] = None
    ) -> List[Message]:
        """Get messages from thread"""
        try:
            # Validate thread participation
            await self._validate_participant(thread_id, user_id)
            
            # Get messages
            query = Message.filter(thread_id=thread_id)
            if before_id:
                query = query.filter(id__lt=before_id)
            messages = await query.order_by("-created_at").limit(limit).all()
            
            # Mark messages as read
            await self._mark_messages_read(messages, user_id)
            
            return messages
        except Exception as e:
            logger.error(f"Failed to get messages: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def connect_websocket(
        self,
        websocket: WebSocket,
        user_id: str
    ) -> None:
        """Connect user to WebSocket"""
        try:
            await websocket.accept()
            self.active_connections[user_id] = websocket
        except Exception as e:
            logger.error(f"WebSocket connection failed: {str(e)}")
            raise

    async def disconnect_websocket(
        self,
        user_id: str
    ) -> None:
        """Disconnect user from WebSocket"""
        try:
            if user_id in self.active_connections:
                await self.active_connections[user_id].close()
                del self.active_connections[user_id]
        except Exception as e:
            logger.error(f"WebSocket disconnection failed: {str(e)}")
            raise

    async def _validate_participant(
        self,
        thread_id: str,
        user_id: str
    ) -> None:
        """Validate user participation in thread"""
        participant = await MessageParticipant.get(
            thread_id=thread_id,
            user_id=user_id
        )
        if not participant:
            raise ValueError("User is not a thread participant")

    async def _process_attachments(
        self,
        attachments: List[Dict]
    ) -> List[MessageAttachment]:
        """Process message attachments"""
        processed = []
        for attachment in attachments:
            processed_attachment = await MessageAttachment.create(
                filename=attachment["filename"],
                content_type=attachment["content_type"],
                url=attachment["url"],
                size=attachment["size"],
                metadata=attachment.get("metadata", {}),
                created_at=datetime.now()
            )
            processed.append(processed_attachment)
        return processed

    async def _notify_participants(
        self,
        thread_id: str,
        message: Message,
        sender_id: str
    ) -> None:
        """Notify thread participants of new message"""
        participants = await MessageParticipant.filter(
            thread_id=thread_id
        ).all()
        
        notification = {
            "type": "new_message",
            "thread_id": thread_id,
            "message": {
                "id": message.id,
                "content": message.content,
                "sender_id": sender_id,
                "created_at": message.created_at.isoformat()
            }
        }
        
        for participant in participants:
            if (
                participant.user_id != sender_id and
                participant.user_id in self.active_connections
            ):
                try:
                    await self.active_connections[
                        participant.user_id
                    ].send_json(notification)
                except Exception as e:
                    logger.error(
                        f"Failed to notify participant {participant.user_id}: {str(e)}"
                    )

    async def _mark_messages_read(
        self,
        messages: List[Message],
        user_id: str
    ) -> None:
        """Mark messages as read by user"""
        for message in messages:
            if message.sender_id != user_id:
                message.read_by = message.read_by or []
                if user_id not in message.read_by:
                    message.read_by.append(user_id)
                    await message.save()
