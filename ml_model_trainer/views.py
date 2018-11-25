import os
import ast
from subprocess import Popen, PIPE, STDOUT
from django.core.files.base import ContentFile

from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView

from .models import Experiment
from .serializers import ExperimentSerializer, ImageSerializer, \
    MLModelSerializer


class MLModelView(CreateAPIView):
    """View creates Machine learning model"""

    serializer_class = MLModelSerializer


class ExperimentView(CreateAPIView):
    """View runs experiment and save data into model"""

    serializer_class = ExperimentSerializer

    def post(self, request, *args, **kwargs):
        """Handle POST request

        Notes
        -----
        1. Adds model_id to request body and save request body data to DB
        """
        request.data.update(kwargs)
        return super(ExperimentView, self).post(request, *args, **kwargs)


class UploadImageView(CreateAPIView):
    """View upload images and save into db"""

    serializer_class = ImageSerializer

    def post(self, request, *args, **kwargs):
        """Handle POST request

        Notes
        -----
        1. Adds model_id to request body and save request body data to DB
        """
        request.data.update(kwargs)
        return super(UploadImageView, self).post(request, *args, **kwargs)


class TestView(APIView):
    """View to test optimum experiment params"""

    def post(self, request, *args, **kwargs):
        """Execute test script to test best accuracy experiment params"""
        request_data = request.data.dict()
        image_file = request_data['image']
        full_filename = os.path.join('media', 'test_images', image_file.name)
        fout = open(full_filename, 'wb+')
        file_content = ContentFile(image_file.read())
        for chunk in file_content.chunks():
            fout.write(chunk)
        fout.close()

        best_experiment = Experiment.objects.order_by('-accuracy').first()
        learning_rate = str(best_experiment.learning_rate)
        layers_count = str(best_experiment.layers_count)
        steps_count = str(best_experiment.steps_count)

        script_path = settings.BASE_DIR + '/ml_model_trainer/test.py'
        test = Popen(
            ["python", script_path,
             "--i", learning_rate, "--j", layers_count, "--k", steps_count,
             "--image", full_filename],
            stdout=PIPE, stderr=STDOUT)
        exp_result = test.stdout.read()
        test_dict = ast.literal_eval(exp_result.decode('utf-8'))

        result_dict = {
            'learning_rate': test_dict['i'],
            'layers_count': test_dict['j'],
            'steps_count': test_dict['k'],
            'accuracy': test_dict['accuracy'],
            'image': test_dict['image']
        }
        return Response(result_dict, status=status.HTTP_201_CREATED)
