from django.db import models

# Create your models here.

class GoogleResult(models.Model):
    r_name = models.CharField(max_length=25)
    r_address = models.CharField(max_length=100)
    r_lat = models.FloatField()
    r_lon = models.FloatField()

    def __str__(self):
       return self.r_name + ' ' + self.r_address + ' ' + str(self.r_lat) + ','+ str(self.r_lon)

class GoogleResult_cost(models.Model):
    result_text = models.CharField(max_length=100)
    def __str__(self):
        return self.result_text

class GoogleResult_time(models.Model):
    
    r_startlat = models.FloatField()
    r_startlon = models.FloatField()
    r_destlat = models.FloatField()
    r_destlon = models.FloatField()
    r_time = models.CharField(max_length=20)
    origin = models.CharField(max_length=100)
    destination2 = models.CharField(max_length=100)
    
    def __str__(self):
        return str(self.r_startlat) + ' ' + str(self.r_startlon) + ' ' + str(self.r_destlat) + ' ' + str(self.r_destlon) + ' ' + self.r_time + ' ' + self.origin + ' ' + self.destination2

class GoogleResult_steps(models.Model):
    
    step = models.CharField(max_length=200)
    time = models.CharField(max_length=20)
    
    def __str__(self):
        return self.step + ' ' + self.time