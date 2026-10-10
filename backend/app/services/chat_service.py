"""
Orchestrates the chat pipeline: analyzer -> hybrid search -> RAG engine ->
answer_builder, then persists the conversation/message/citations.
"""
import logging
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.system import AnswerCitation
from app.models.users import Conversation, Message
from app.rag import answer_builder
from app.rag.analyzer import analyze_question
from app.rag.engine import GeminiUnavailableError, generate_answer
from app.repositories.user_repository import ConversationRepository
from app.schemas.legal import SearchResultItem
from app.search.hybrid import hybrid_search

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.conversations = ConversationRepository(db)

    def _get_or_create_conversation(self, user_id: str, conversation_id: Optional[str], first_message: str) -> Conversation:
        if conversation_id:
            conv = self.conversations.get(conversation_id)
            if conv and conv.user_id == user_id:
                return conv
        title = (first_message[:80] + "...") if len(first_message) > 80 else first_message
        return self.conversations.create(user_id=user_id, title=title)

    def ask(self, user_id: str, message: str, conversation_id: Optional[str] = None) -> Tuple[Conversation, Message, List[SearchResultItem]]:
        conversation = self._get_or_create_conversation(user_id, conversation_id, message)
        self.conversations.add_message(conversation.id, role="user", content=message)

        # 1. Analyzer: understand the question.
        analysis = analyze_question(message)

        # 2. Search: hybrid retrieval over the legal corpus.
        search_results = hybrid_search(self.db, message, limit=8)

        # 3. RAG engine: call Gemini with grounded context, or fall back.
        try:
            raw = generate_answer(message, search_results, analysis)
            answer_text = answer_builder.parse_gemini_answer(raw)
        except GeminiUnavailableError as exc:
            logger.warning("Chat: Gemini unavailable, using fallback answer: %s", exc)
            answer_text = answer_builder.build_fallback_answer(
                question=message,
                analysis=analysis,
                context_results=search_results,
                note="خدمة الذكاء الاصطناعي (Gemini) غير مُهيأة حالياً على هذا الخادم.",
            )

        assistant_message = self.conversations.add_message(conversation.id, role="assistant", content=answer_text)

        # 4. Persist citations for traceability (answer_citations table).
        for result in search_results[:5]:
            citation = AnswerCitation(
                message_id=assistant_message.id,
                source_type=result.result_type,
                article_id=result.id if result.result_type == "article" else None,
                judgment_id=result.id if result.result_type == "judgment" else None,
                citation_text=result.title,
                relevance_score=result.score,
            )
            self.db.add(citation)
        self.db.commit()

        return conversation, assistant_message, search_results
