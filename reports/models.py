from django.db import models
from users.models import User
# Create your models here.
class ReportCSV(models.Model):

    user = models.ForeignKey(User)
    csv_data = models.TextField() 

    class Meta:
        verbose_name = "ReportCSV"
        verbose_name_plural = "ReportCSVs"

    def __str__(self):
        pass
    

class ReportXLS(models.Model):

    user = models.ForeignKey(User)
    xls_data = models.FileField(upload_to = 'files/') 

    class Meta:
        verbose_name = "ReportCSV"
        verbose_name_plural = "ReportCSVs"

    def __str__(self):
        pass
    