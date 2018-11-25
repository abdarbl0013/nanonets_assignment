import ast
from subprocess import Popen, PIPE, STDOUT

from django.conf import settings
from rest_framework import serializers

from .models import Experiment, Image, MLModel


class MLModelSerializer(serializers.ModelSerializer):
    """Model Serializer for Machine learning model"""

    class Meta(object):
        """Meta information of MLModelSerializer"""
        model = MLModel
        fields = '__all__'


class ExperimentSerializer(serializers.ModelSerializer):
    """Model Serializer for Experiment model"""
    accuracy = serializers.FloatField(required=False)

    class Meta(object):
        """Meta information of ExperimentSerializer"""
        model = Experiment
        fields = ('learning_rate', 'layers_count', 'steps_count',
                  'accuracy', 'model_id')
        extra_kwargs = {
            'model_id': {'source': 'model'},
            'learning_rate': {'write_only': True},
            'layers_count': {'write_only': True},
            'steps_count': {'write_only': True}
        }

    def create(self, validated_data):
        """Create Experiment instance

        Notes
        -----
        1. Call train script to get experiment results
        2. Save results along with params into DB
        """
        script_path = settings.BASE_DIR + '/ml_model_trainer/train.py'
        images_dir = settings.BASE_DIR + '/media/exp_images/'

        train = Popen(
            ["python", script_path,
             "--i", str(validated_data['learning_rate']),
             "--j", str(validated_data['layers_count']),
             "--k", str(validated_data['steps_count']),
             "--images", images_dir],
            stdout=PIPE, stderr=STDOUT)
        exp_result = train.stdout.read()
        result_dict = ast.literal_eval(exp_result.decode('utf-8'))

        validated_data['accuracy'] = result_dict['accuracy']
        return super(ExperimentSerializer,self).create(validated_data)


class ImageSerializer(serializers.ModelSerializer):
    """Model Serializer for Image model"""

    class Meta(object):
        """Meta information of ImageSerializer"""
        model = Image
        fields = ('model_id', 'image',)
        extra_kwargs = {
            'model_id': {'source': 'model'}
        }
