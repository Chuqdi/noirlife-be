from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import status, parsers

from utils.ResponseGenerator import ResponseGenerator
from .models import ChatSession, Message
from .serializers import ChatSessionSerializer, MessageSerializer
from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class ChatSessionListCreateView(APIView):
    """List all sessions (chat history) or create a new one"""

    def get(self, request):
        sessions = ChatSession.objects.filter(user=request.user)
        serializer = ChatSessionSerializer(sessions, many=True)
        return ResponseGenerator.response(
            data=serializer.data,
            status=status.HTTP_200_OK,
            message="Success"
        )

    def post(self, request):
        session = ChatSession.objects.create(user=request.user)
        serializer = ChatSessionSerializer(session)
        return ResponseGenerator.response(
            data=serializer.data,
            status=status.HTTP_201_CREATED,
            message="Session created"
        )


class ChatSessionDetailView(APIView):
    """Get a single session with all its messages"""

    def get(self, request, session_id):
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return ResponseGenerator.response(
                data=None,
                status=status.HTTP_404_NOT_FOUND,
                message="Session not found"
            )
        serializer = ChatSessionSerializer(session)
        return ResponseGenerator.response(
            data=serializer.data,
            status=status.HTTP_200_OK,
            message="Success"
        )

    def delete(self, request, session_id):
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
            session.delete()
        except ChatSession.DoesNotExist:
            pass
        return ResponseGenerator.response(
            data=None,
            status=status.HTTP_204_NO_CONTENT,
            message="Deleted"
        )


class SendMessageView(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def post(self, request, session_id):
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return ResponseGenerator.response(
                data=None,
                status=status.HTTP_404_NOT_FOUND,
                message="Session not found"
            )

        text = request.data.get("text", "")
        file = request.FILES.get("file", None)
        # ── If False, no AI reply is sent. Admin replies manually ────────────
        use_ai = request.data.get("use_ai", "true").lower() == "true"

        # ── Persist user message ─────────────────────────────────────────────
        user_message = Message.objects.create(
            session=session,
            role=Message.Role.USER,
            text=text,
            file_name=file.name if file else None,
            file_mime_type=file.content_type if file else None,
            is_image=file.content_type.startswith("image/") if file else False,
        )

        # ── Auto-title session from first message ────────────────────────────
        if not session.title and text:
            session.title = text[:60]
            session.save(update_fields=["title"])

        if not use_ai:
            # Return user message only — admin will reply via Django admin
            return ResponseGenerator.response(
                data={
                    "user_message": MessageSerializer(user_message).data,
                    "model_message": None,
                    "awaiting_admin": True,
                },
                status=status.HTTP_200_OK,
                message="Message sent. Awaiting admin reply."
            )

        # ── Build ChatGPT history from previous messages ─────────────────────
        history = []
        past_messages = session.messages.exclude(
            id=user_message.id
        ).order_by("date_created")

        for msg in past_messages:
            history.append({
                "role": "user" if msg.role == Message.Role.USER else "assistant",
                "content": msg.text or "",
            })

        # ── Build current message content ─────────────────────────────────────
        if file and file.content_type.startswith("image/"):
            import base64
            encoded = base64.b64encode(file.read()).decode("utf-8")
            current_content = [
                {"type": "text", "text": text or "What's in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{file.content_type};base64,{encoded}"
                    },
                },
            ]
        else:
            current_content = text

        history.append({"role": "user", "content": current_content})
       

        # ── Call ChatGPT ──────────────────────────────────────────────────────
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are Noir, an AI drink intelligence assistant. "
                            "You help users with drink information, BAC levels, "
                            "hangover recovery tips, and drink safety guidance."
                        ),
                    },
                    *history,
                ],
                max_tokens=1000,
            )
            reply_text = response.choices[0].message.content
        except Exception as e:
            print(e)
            return ResponseGenerator.response(
                data=None,
                status=status.HTTP_502_BAD_GATEWAY,
                message=f"ChatGPT error: {str(e)}"
            )
       
        

        # ── Persist model reply ───────────────────────────────────────────────
        model_message = Message.objects.create(
            session=session,
            role=Message.Role.MODEL,
            text=reply_text,
            reply_to=user_message,
        )

        return ResponseGenerator.response(
            data={
                "user_message": MessageSerializer(user_message).data,
                "model_message": MessageSerializer(model_message).data,
                "awaiting_admin": False,
            },
            status=status.HTTP_200_OK,
            message="Success"
        )


class PollNewMessagesView(APIView):
    """
    Frontend polls this to check if admin has replied since last_message_id.
    GET /chat/sessions/<session_id>/poll/?after=<last_message_id>
    """

    def get(self, request, session_id):
        after_id = request.query_params.get("after", 0)
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return ResponseGenerator.response(
                data=None,
                status=status.HTTP_404_NOT_FOUND,
                message="Session not found"
            )

        new_messages = session.messages.filter(
            id__gt=after_id,
            role=Message.Role.MODEL
        ).order_by("date_created")

        serializer = MessageSerializer(new_messages, many=True)
        return ResponseGenerator.response(
            data=serializer.data,
            status=status.HTTP_200_OK,
            message="Success"
        )