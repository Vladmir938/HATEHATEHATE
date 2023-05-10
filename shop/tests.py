from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from shop.models import Product


class ProductApiViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('shop:product_list')
        self.product_data = {
            'name': 'Test Product',
            'description': 'This is SPARTA',
            'price': 300.0,
            'category': None
        }
        self.product = Product.objects.create(**self.product_data)

    def test_get_product_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.product.name)

    def test_create_product(self):
        response = self.client.post(self.url, self.product_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(Product.objects.last().name, self.product_data['name'])

    def test_get_product_detail(self):
        detail_url = reverse('product-detail', args=[self.product.pk])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], self.product.name)

    def test_update_product(self):
        detail_url = reverse('product-detail', args=[self.product.pk])
        updated_data = self.product_data.copy()
        updated_data['name'] = 'Updated Test Product'
        response = self.client.put(detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Product.objects.get(pk=self.product.pk).name, updated_data['name'])

    def test_delete_product(self):
        detail_url = reverse('product-detail', args=[self.product.pk])
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Product.objects.count(), 0)