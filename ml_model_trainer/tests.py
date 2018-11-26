import json
from PIL import Image
from io import BytesIO

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import MLModel, Experiment


def create_image(size=(100, 100), image_mode='RGB', image_format='PNG'):
    """
    Generate a test image, BytesIO containing the image data."""

    data = BytesIO()
    Image.new(image_mode, size).save(data, image_format)
    data.seek(0)
    return data


class MLModelTestCase(TestCase):
    """Test cases for Model trainer app"""

    def setUp(self):
        """Sets up sample placeholder values / environment for test cases"""
        self.client = APIClient()
        self.content_type = 'application/json'

        self.model = MLModel.objects.create(name='Placeholder ML Model')
        self.experiment = Experiment.objects.create(
            learning_rate=0.01,
            layers_count=2,
            steps_count=3000,
            model=self.model,
            accuracy=0.67
        )

    def test_ml_model(self):
        """Test create operation on MLModel"""
        create_data = {
            'name': 'Sample ML Model'
        }

        url = '/model_trainer/'
        response = self.client.post(url, json.dumps(create_data),
                                    content_type=self.content_type)
        self.assertTrue(status.is_success(response.status_code))
        response_data = response.data
        self.assertEqual(response_data['name'], create_data['name'])

    def test_experiment_create(self):
        """Test create operation on Experiment"""
        create_data = {
            'learning_rate': 0.01,
            'layers_count': 2,
            'steps_count': 4000
        }

        url = '/model_trainer/{0}/experiment/'.format(self.model.id)
        response = self.client.post(url, json.dumps(create_data),
                                    content_type=self.content_type)
        self.assertTrue(status.is_success(response.status_code))
        response_data = response.data
        self.assertEqual(response_data['model_id'], self.model.id)

    def test_upload_image(self):
        """Test upload image"""

        url = '/model_trainer/{0}/image/'.format(self.model.id)

        temp_image = create_image()
        image_file = SimpleUploadedFile('data_image.png',
                                        temp_image.getvalue())

        response = self.client.post(url, {'image': image_file})
        self.assertTrue(status.is_success(response.status_code))
        response_data = response.data
        self.assertEqual(response_data['model_id'], self.model.id)

    def test_model_test(self):
        """Test MLModel test API"""

        temp_image = create_image()
        image_file = SimpleUploadedFile('test_image.png',
                                        temp_image.getvalue())

        url = '/model_trainer/{0}/test/'.format(self.model.id)
        response = self.client.post(url, {'test_image': image_file})
        self.assertTrue(status.is_success(response.status_code))
