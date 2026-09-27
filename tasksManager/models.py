from django.conf import settings
from django.db import models

statuses = {
    "complete" : 1,
    "created" : 2,
    "active" : 3,
    "inactive" : 4,
}


# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(choices=statuses.items(), max_length=10)
    workers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="tasks")

    def __str__(self):
        return self.title

