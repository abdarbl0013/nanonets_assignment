from django.db import models


class MLModel(models.Model):
    """Machine Learning Model"""
    name = models.CharField(max_length=50)


class Experiment(models.Model):
    """Model to store experiment parameters and results"""

    model = models.ForeignKey(MLModel, related_name='experiments',
                              on_delete=models.CASCADE)
    learning_rate = models.FloatField()
    layers_count = models.IntegerField()
    steps_count = models.IntegerField()
    accuracy = models.FloatField()


class Image(models.Model):
    """Model to store uploaded image file"""

    model = models.ForeignKey(MLModel, related_name='images',
                              on_delete=models.CASCADE)
    image = models.ImageField(upload_to='exp_images/')
