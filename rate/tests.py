from django.test import TestCase
from unittest import mock
from rate.controllers import create_prices
from rate.models import Region, Port, Price


# Create your tests here.
class CreatePriceControllerTest(TestCase):

    def setUp(self):
        self.r1 = Region(slug='test1')
        self.r1.save()
        self.r2 = Region(slug='test2')
        self.r2.save()
        self.p1 = Port(parent_slug=self.r1, code='abc')
        self.p1.save()
        self.p2 = Port(parent_slug=self.r2, code='xyz')
        self.p2.save()
        self.price_data = {
            'date_from': '2020-11-20',
            'date_to': '2020-11-24',
            'origin_code': self.p1.code,
            'destination_code': self.p2.code,
            'price': 123
        }

    def test_create_price(self):
        is_created, message = create_prices(self.price_data, 'USD')
        self.assertTrue(is_created)
        self.assertEqual(message, {'success': True})
        self.assertEqual(5, Price.objects.count())

    def test_create_price_when_to_date_less_than_from_date(self):
        self.price_data['date_to'] = '2020-11-19'
        with self.assertRaisesMessage(
            ValueError,
            "`date_to` must be greater than equal to `date_from`"
        ):
            create_prices(self.price_data, 'USD')

    def test_create_price_when_date_has_wrong_format(self):
        self.price_data['date_from'] = '19-11-2020'
        with self.assertRaisesMessage(
            ValueError,
            "time data '19-11-2020' does not match format '%Y-%m-%d'"
        ):
            create_prices(self.price_data, 'USD')

    def test_create_price_when_invalid_price(self):
        self.price_data['price'] = -1
        with self.assertRaisesMessage(
            ValueError,
            "Price should be positive number"
        ):
            create_prices(self.price_data, 'USD')

        self.price_data['price'] = 'abc'
        with self.assertRaisesMessage(
            ValueError,
            "Please provide valid price"
        ):
            create_prices(self.price_data, 'USD')

    @mock.patch('requests.get')
    def test_create_price_when_inr_currency(self, req_mock):
        res = mock.MagicMock()
        res.ok.return_value = True
        res.json.return_value = {
            'rates': {
                'INR': 74
            }
        }
        req_mock.return_value = res
        self.price_data['date_to'] = '2020-11-20'
        is_created, message = create_prices(self.price_data, 'INR')
        self.assertTrue(is_created)
        self.assertEqual(message, {'success': True})
        self.assertEqual(1, Price.objects.count())
        self.assertEqual(Price.objects.first().price, 2)
