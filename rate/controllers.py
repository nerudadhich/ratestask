import datetime
import requests

from decouple import config
from .models import Port, Price
from .serializers import PriceSerializer
from rate.raw_sql import ports_query, average_price_query


def get_prices(date_from, date_to, origin, destination, rates_null=False):
    """
    This is to calculate average price of each day `from` to `to` dates
    between origin and destination
    :param date_from: start date for fare calculation
    :param date_to: end date for fare calculation
    :param origin: trip origin port or region slug
    :param destination: trip destination port or region slug
    :param rates_null: if rates_null true return an empty value (JSON null)
                       for days on which there are less than 3 prices in total
    :return: list of average price for each day
            [{
                day: 2020-12-02
                average_price: 129
            }]
    """
    _validate_dates(date_from, date_to)
    origin_ports = get_ports_code(origin)
    destination_ports = get_ports_code(destination)
    query = average_price_query.format(
        rates_null=rates_null,
        origin_ports=str(origin_ports)[1:-1],
        destination_ports=str(destination_ports)[1:-1],
        date_from=date_from,
        date_to=date_to
    )
    prices = Price.objects.raw(query)
    return PriceSerializer(prices, many=True).data


# Note: here we can process this using background task or
# on batch system if data is huge
def create_prices(data, currency):
    """
    Create bulk fare for given port for a given range of date
    :param data:
    :param currency:
    :return: True if success else errors list
    """
    fare_dates = _get_dates_list(
        data.get('date_from'), data.get('date_to'))
    price = _validate_price(data.get('price'))
    if (currency and currency.lower() !=
            config('DEFAULT_CURRENCY', 'USD').lower()):
        currency_rate = _get_currency_rate(currency)
        # Assumption taken that we store integer price,
        # might not be the real case
        price = round(price / currency_rate)
    prices = []
    for date in fare_dates:
        prices.append({
            'day': date,
            'orig_code': data.get('orig_code', None),
            'dest_code': data.get('dest_code', None),
            'price': price,
        })
    price_serializer = PriceSerializer(data=prices, many=True)
    if price_serializer.is_valid():
        price_serializer.save()
        return True, {"success": True}
    return False, price_serializer.errors[0]


def get_ports_code(region_slug):
    """
    This method will return all ports code in a region
    :param region_slug: this can be region slug or a port code
    :return: port codes list
    """
    # todo: can put extra validation if provided codes or slug is correct

    ports = Port.objects.raw(
        ports_query.format(port=region_slug).replace('\n', ''))
    if not ports:
        raise ValueError(
            f'No port or region found with given code `{region_slug}`')
    return [port.code for port in ports]


def _validate_dates(date_from, date_to):
    """
    Validate the date and convert string to date
    :param date_from: fare start date
    :param date_to: fare end date
    :return: exception if not valid date or return date objects
    """
    # todo: date format can be picked from configs
    d_from = datetime.datetime.strptime(date_from, "%Y-%m-%d")
    d_to = datetime.datetime.strptime(date_to, "%Y-%m-%d")
    if d_to < d_from:
        raise ValueError("`date_to` must be greater than equal to `date_from`")
    return d_from, d_to


def _get_dates_list(date_from, date_to):
    """
    Return list of dates `from` to `to` date
    :param date_from: fare start date
    :param date_to: fare end date
    :return: list of dates
    """
    d_from, d_to = _validate_dates(date_from, date_to)
    return [(d_from + datetime.timedelta(days=x)).strftime("%Y-%m-%d")
            for x in range((d_to - d_from).days + 1)]


def _get_currency_rate(currency):
    """
    This function calculate currency conversion rate for USD base price.
    :param currency: currency code
    :return: exception or currency rate
    """
    response = requests.get(f'{config("OPENEXCHANGERATES_URL")}')
    if not response.ok:
        # log
        # can handle exception in better way later
        raise Exception(
            f'currency conversion api not working {response.text}')
    rates = response.json().get('rates')
    currency_rate = rates.get(currency.upper(), None)
    if not currency_rate:
        raise ValueError(f'Given currency conversion rate not found')
    return currency_rate


def _validate_price(price):
    """
    Validate the given price and return
    :param price: fare between ports
    :return: exception if fails or return price in float
    """
    try:
        price = float(price)
    except ValueError:
        raise ValueError('Please provide valid price')
    if price < 1:
        raise ValueError('Price should be positive number')
    return price
