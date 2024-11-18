from django.db import models
from django.core.validators import FileExtensionValidator

class Dataset(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(
        upload_to='datasets/',
        validators=[FileExtensionValidator(allowed_extensions=['csv'])]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Player(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    team = models.CharField(max_length=100)
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    tackles = models.IntegerField(default=0)
    interceptions = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.team})"