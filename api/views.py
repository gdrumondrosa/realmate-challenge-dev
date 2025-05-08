from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer

class WebhookView(APIView):
    def post(self, request):
        payload = request.data

        try:
            event_type = payload['type']
            timestamp = payload['timestamp']
            data = payload['data']
        except (KeyError, TypeError):
            return Response({'detail': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)

        if event_type == 'NEW_CONVERSATION':
            conv_id = data.get('id')

            # Se não existie id no payload, erro
            if not conv_id:
                return Response({'detail': 'Missing conversation id'}, status=status.HTTP_400_BAD_REQUEST)

            # Se já existir conversa com o id, erro
            if Conversation.objects.filter(id=conv_id).exists():
                return Response({'detail': 'Conversation already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            # Liberado para criar a conversa
            Conversation.objects.create(id=conv_id, state=Conversation.OPEN)
            return Response({'detail': 'Conversation opened.'}, status=status.HTTP_201_CREATED)

        elif event_type == 'NEW_MESSAGE':
            msg_id  = data.get('id')
            conv_id = data.get('conversation_id')
            direction = data.get('direction')
            content   = data.get('content')

            # Se não existie alguma informação no payload, erro
            if None in (msg_id, conv_id, direction, content):
                return Response({'detail': 'Missing message fields'}, status=status.HTTP_400_BAD_REQUEST)

            conv = Conversation.objects.filter(id=conv_id).first()

            # Se não existir conversa com o id, erro
            if not conv:
                return Response({'detail': 'Conversation not found'}, status=status.HTTP_400_BAD_REQUEST)

            # Se a conversa estiver fechada, erro
            if conv.state == Conversation.CLOSED:
                return Response({'detail': 'Conversation closed'}, status=status.HTTP_400_BAD_REQUEST)

            # Se já existir a mensagem com o id, erro
            if Message.objects.filter(id=msg_id).exists():
                return Response({'detail': 'Message already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            # Liberado para criar a mensagem
            Message.objects.create(
                id=msg_id,
                conversation=conv,
                direction=direction,
                content=content,
                timestamp=timestamp
            )
            return Response({'detail': 'Message saved.'}, status=status.HTTP_201_CREATED)

        elif event_type == 'CLOSE_CONVERSATION':
            conv_id = data.get('id')
            conv = Conversation.objects.filter(id=conv_id).first()

            # Se não existir conversa com o id, erro
            if not conv:
                return Response({'detail': 'Conversation not found'}, status=status.HTTP_400_BAD_REQUEST)

            # Se a conversa já estiver fechada, erro
            if conv.state == Conversation.CLOSED:
                return Response({'detail': 'Conversation already closed.'}, status=status.HTTP_400_BAD_REQUEST)

            # Liberado para fechar a conversa
            conv.state = Conversation.CLOSED
            conv.save()
            return Response({'detail': 'Conversation closed.'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Unsupported event type'}, status=status.HTTP_400_BAD_REQUEST)

class ConversationDetailView(APIView):
    def get(self, request, id):
        conv = get_object_or_404(Conversation, id=id)
        serializer = ConversationSerializer(conv)
        return Response(serializer.data)
    
class ConversationListView(APIView):
    def get(self, request):
        convs = Conversation.objects.all()
        serializer = ConversationSerializer(convs, many=True)
        return Response(serializer.data)