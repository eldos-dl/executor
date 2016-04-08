from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET', 'POST'])
def get_stats(request):
    from .serializers import StatsSerializer
    from .types import StatsType
    response_serializer = StatsSerializer(StatsType())
    return Response(response_serializer.data, status=status.HTTP_200_OK)

