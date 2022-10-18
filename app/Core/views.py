"""
Vista Core para app
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def health_check(request):
    """Regresa una respuesta correctamente"""
    return Response({'healthy': True})
