""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

import os
from django.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from topics.models import Resource
from users.models import User

valid_formats = [
    'image/bmp',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/gif',
    'text/html',
    'image/jpeg',
    'image/pjpeg',
    'audio/mpeg',
    'audio/x-mpeg',
    'video/mpeg',
    'video/x-mpeg',
    'video/x-mpeq2a',
    'audio/mpeg3',
    'audio/x-mpeg-3',
    'video/mp4',
    'application/vnd.oasis.opendocument.presentation',
    'application/vnd.oasis.opendocument.spreadsheet',
    'application/vnd.oasis.opendocument.text',
    'application/pdf',
    'image/png',
    'application/mspowerpoint',
    'application/powerpoint',
    'application/x-mspowerpoint',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/excel',
    'application/x-excel',
    'application/x-msexcel',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'audio/x-wav',
    'audio/wav'
]

def validate_file_extension(value):
    if hasattr(value.file, 'content_type'):
        if not value.file.content_type in valid_formats:
            raise ValidationError(_('File not supported, use PDF format instead.'))

class MaterialDelivery(Resource):
    presentation = models.TextField(_('Presentation'), blank = False)
    data_ini = models.DateTimeField(_('Init Date'), auto_now_add = False)
    data_end = models.DateTimeField(_('End Date'), auto_now_add = False)

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materials"

    def __str__(self):
        return self.name

    def access_link(self):
        return reverse_lazy('material_delivery:view', args = (), kwargs = {'slug': self.slug})

    def update_link(self):
        return 'material_delivery:update'

    def delete_link(self):
        return 'material_delivery:delete'

    def delete_message(self):
        return _('Are you sure you want delete the Material Delivery')

    def get_data_ini(self):
        return self.data_ini
    
    def get_data_end(self):
        return self.data_end

def get_upload_support_path(instance, filename):
    return os.path.join("material_delivery", ("deliver_%d" % instance.delivery.id), "support", filename)

class SupportMaterial(models.Model):
    delivery = models.ForeignKey(MaterialDelivery, verbose_name = _('Material Delivery'), related_name = 'support_materials', null = True)
    file = models.FileField(_('File'), upload_to=get_upload_support_path, validators = [validate_file_extension], blank = True)

    class Meta:
        verbose_name = "Support Material"
        verbose_name_plural = "Support Materials"

    @property
    def filename(self):
        return os.path.basename(self.file.name)

class StudentDeliver(models.Model):
    delivery = models.ForeignKey(MaterialDelivery, verbose_name = _('Material Delivery'), related_name = 'student_deliver', null = True)
    student = models.ForeignKey(User, verbose_name = _('User'), related_name = 'studentdeliver_user', null = True)

    class Meta:
        verbose_name = "Student Deliver"
        verbose_name_plural = "Students Deliver"

def get_upload_student_path(instance, filename):
    return os.path.join("material_delivery", "students_materials", ("user_%d" % instance.deliver.student.id), ("deliver_%d" % instance.deliver.id), filename)

class StudentMaterial(models.Model):
    deliver = models.ForeignKey(StudentDeliver, verbose_name = _('Student Deliver'), related_name = 'material_deliver', null = True)
    commentary = models.TextField(_('Commentary'), blank = False)
    file = models.FileField(_('File'), upload_to=get_upload_student_path, validators = [validate_file_extension])
    upload_date = models.DateTimeField(_('Upload Date'), auto_now_add = True)

    class Meta:
        verbose_name = "Student Material"
        verbose_name_plural = "Student Materials"

        ordering = ['upload_date']

    @property
    def filename(self):
        return os.path.basename(self.file.name)

def get_upload_teacher_path(instance, filename):
    return os.path.join("material_delivery", "teacher_evaluations", ("user_%d" % instance.teacher.id), ("deliver_%d" % instance.deliver.id), filename)

class TeacherEvaluation(models.Model):
    deliver = models.ForeignKey(StudentDeliver, verbose_name = _('Student Deliver'), related_name = 'student_deliver', null = True)
    evaluation = models.PositiveSmallIntegerField(_("Grade"), null = True)
    commentary = models.TextField(_('Commentary'), blank = True)
    teacher = models.ForeignKey(User, verbose_name = _('User'), related_name = 'teacherevaluation_user', null = True)
    file = models.FileField(_('File'), upload_to=get_upload_teacher_path, validators = [validate_file_extension])
    is_updated = models.BooleanField(_('Is updated?'), default = False)
    evaluation_date = models.DateTimeField(_('Evaluation Date'), auto_now = True)

    class Meta:
        verbose_name = "Teacher Evaluation"
        verbose_name_plural = "Teacher Evaluations"

    @property
    def filename(self):
        return os.path.basename(self.file.name)

