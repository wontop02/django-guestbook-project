from django.db import models

class Guestbook(models.Model):

    id = models.AutoField(primary_key=True)
    writer = models.CharField(max_length=10)
    title = models.CharField(max_length=30)
    content = models.TextField()
    password = models.CharField(max_length=4)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self): 
        return f"{self.title} - {self.writer}"
