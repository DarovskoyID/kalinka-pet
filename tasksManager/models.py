from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

statuses = {
    "complete" : 1,
    "created" : 2,
    "active" : 3,
    "inactive" : 4,
}

priorities = {
    "low" : 1,
    "medium" : 2,
    "high" : 3,
}


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=512)
    color_Red = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(255)])
    color_Green = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(255)])
    color_Blue = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(255)])

    def __str__(self):
        return self.title

# Create your models here.
class Task(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    completed = models.DateField(null=True, blank=True)
    status = models.CharField(choices=statuses.items(), max_length=20, default="created")
    priority = models.CharField(choices=priorities.items(), max_length=20, default="low")
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    workers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="tasks")

    def __str__(self):
        return self.title

