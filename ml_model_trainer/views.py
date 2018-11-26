import os
import ast
from subprocess import Popen, PIPE, STDOUT
from django.core.files.base import ContentFile

from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, \
    RetrieveDestroyAPIView, DestroyAPIView

from .models import Experiment, MLModel, Image
from .serializers import ExperimentSerializer, ImageSerializer, \
    MLModelSerializer


class MLModelView(RetrieveUpdateAPIView, CreateAPIView):
    """View creates Machine learning model"""

    serializer_class = MLModelSerializer
    queryset = MLModel.objects.all()


class ExperimentView(RetrieveDestroyAPIView, CreateAPIView):
    """View runs experiment and save data into model"""

    serializer_class = ExperimentSerializer
    queryset = Experiment.objects.all()

    def get_queryset(self):
        """Get list of items for Experiment View"""
        return self.queryset.filter(model_id=self.kwargs['model_id'])

    def post(self, request, *args, **kwargs):
        """Handle POST request

        Notes
        -----
        1. Adds model_id to request body and save request body data to DB
        """
        request.data.update(kwargs)
        return super(ExperimentView, self).post(request, *args, **kwargs)


class UploadImageView(DestroyAPIView, CreateAPIView):
    """View upload images and save into db"""

    serializer_class = ImageSerializer
    queryset = Image.objects.all()

    def get_queryset(self):
        """Get list of items for Experiment View"""
        return self.queryset.filter(model_id=self.kwargs['model_id'])

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
        """Handles POST request

        Notes
        -----
        1. Saves uploaded test file to directory and name it
        2. Fetch parameters of most accurate experiment
        3. Run test script with test image name and parameters from last step
        4. Map test experiment result to keys and return response
        """
        request_data = request.data.dict()
        image_file = request_data['test_image']
        test_images_dir = settings.TEST_IMAGES_DIR_PATH
        if not os.path.exists(test_images_dir):
            os.makedirs(test_images_dir)
        test_filename = os.path.join(test_images_dir, image_file.name)

        with open(test_filename, 'wb+') as file_obj:
            file_content = ContentFile(image_file.read())
            for chunk in file_content.chunks():
                file_obj.write(chunk)

        # Fetch parameters of most accurate experiment
        best_experiment = Experiment.objects.order_by('-accuracy').first()
        if not best_experiment:
            raise Exception('No experiment has been performed yet')

        learning_rate = str(best_experiment.learning_rate)
        layers_count = str(best_experiment.layers_count)
        steps_count = str(best_experiment.steps_count)

        # Execute test script
        script_path = os.path.abspath('model_scripts/test.py')
        test = Popen(
            ["python", script_path,
             "--i", learning_rate, "--j", layers_count, "--k", steps_count,
             "--image", test_filename],
            stdout=PIPE, stderr=STDOUT)
        exp_result = test.stdout.read()
        test_dict = ast.literal_eval(exp_result.decode('utf-8'))

        result_dict = {
            'learning_rate': test_dict['i'],
            'layers_count': test_dict['j'],
            'steps_count': test_dict['k'],
            'accuracy': test_dict['accuracy']
        }
        return Response(result_dict, status=status.HTTP_201_CREATED)
