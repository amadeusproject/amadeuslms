""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

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
    