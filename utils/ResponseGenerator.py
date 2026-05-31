

from rest_framework.response import Response
from rest_framework import status



class ResponseGenerator():
    @staticmethod
    def response(data, message, status):
        return Response(
                data={"data":data, "message":message,},
                status=status,
            )
        