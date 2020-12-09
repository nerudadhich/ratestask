import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rate.controllers import get_prices, create_prices

LOGGER = logging.getLogger(__name__)


@api_view(['GET'])
def get_prices_list(request):
    """
    Fare list for given dates between origin and destination
    """
    try:
        _validate_params(request.GET)
        prices = get_prices(
            date_from=request.GET.get('date_from'),
            date_to=request.GET.get('date_to'),
            origin=request.GET.get('origin'),
            destination=request.GET.get('destination')
        )
    except (ValueError, TypeError) as e:
        return Response(str(e), status.HTTP_400_BAD_REQUEST)
    return Response(prices, status.HTTP_200_OK)


@api_view(['GET'])
def get_prices_list_with_null(request):
    """
    Fare list for given dates between origin and destination
    """
    try:
        _validate_params(request.GET)
        prices = get_prices(
            date_from=request.GET.get('date_from'),
            date_to=request.GET.get('date_to'),
            origin=request.GET.get('origin'),
            destination=request.GET.get('destination'),
            rates_null=True
        )
    except (ValueError, TypeError) as e:
        return Response({'error': str(e)}, status.HTTP_400_BAD_REQUEST)
    return Response(prices, status.HTTP_200_OK)


@api_view(['POST'])
def create_prices_view(request):
    """
    Fare list for given dates between origin and destination
    """
    # todo: this block can be moved into custom exception handler middleware
    # https://www.django-rest-framework.org/api-guide/exceptions/
    try:
        is_created, message = create_prices(
            request.data, request.GET.get('currency', 'USD'))
    except (ValueError, TypeError) as e:
        return Response({'error': str(e)}, status.HTTP_400_BAD_REQUEST)
    if is_created:
        return Response(message, status.HTTP_201_CREATED)
    return Response(message, status.HTTP_400_BAD_REQUEST)


def _validate_params(params):
    """
    Validate required query params
    :param params:
    :return: raise ValueError if validation fails
    """
    if all([params.get('date_from'), params.get('date_to'), params.get('origin'), params.get('destination')]):
        return
    raise ValueError("`date_from`, `date_to`, `origin` and `destination`" 
                     "are required params")
