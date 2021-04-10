""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy

from topics.models import Resource
from users.models import User

class h5p_contents_libraries(models.Model):
    content_id = models.PositiveIntegerField(null=False)
    library_id = models.PositiveIntegerField(null=False)
    dependency_type = models.CharField(
        null=False, default='preloaded', max_length=31)
    drop_css = models.PositiveSmallIntegerField(null=False, default=0)
    weight = models.PositiveIntegerField(null=False, default=999999,)

    class Meta:
        db_table = 'h5p_contents_libraries'
        unique_together = (('content_id', 'library_id', 'dependency_type'))

class h5p_libraries(models.Model):
    library_id = models.AutoField(primary_key=True,
        help_text='Identifier of the library')
    machine_name = models.CharField(null=False, default='', max_length=127,
        help_text='Full name of the library')
    title = models.CharField(null=False, default='', max_length=255,
        help_text='Short name of the library')
    major_version = models.PositiveIntegerField(null=False)
    minor_version = models.PositiveIntegerField(null=False)
    patch_version = models.PositiveIntegerField(null=False)
    runnable = models.PositiveSmallIntegerField(null=False, default=1,
        help_text='If the library can be started alone (not a dependency) ?')
    fullscreen = models.PositiveSmallIntegerField(null=False, default=0,
        help_text='Display fullscreen button')
    embed_types = models.CharField(null=False, blank=True, default='', max_length=255)
    preloaded_js = models.TextField(null=True,
        help_text='List of JavaScript files needed by the library')
    preloaded_css = models.TextField(null=True,
        help_text='List of Stylesheet files needed by the library')
    drop_library_css = models.TextField(null=True, blank=True,
        help_text='List of Libraries that should not have CSS included if this library is used')
    semantics = models.TextField(null=False, blank=True,
        help_text='The semantics definition in JSON format')
    restricted = models.PositiveSmallIntegerField(null=False, default=0,
        help_text='If this library can be used to create new content')
    tutorial_url = models.CharField(null=True, max_length=1000, blank=True,
        help_text='URL to a tutorial for this library')

    class Meta:
        db_table = 'h5p_libraries'
        ordering = ['machine_name', 'major_version', 'minor_version']
        verbose_name = 'Library'
        verbose_name_plural = 'Libraries'

    def __unicode__(self):
        return self.machine_name

    def __str__(self):
        return "%s" % (self.machine_name)

class h5p_libraries_libraries(models.Model):
    library_id = models.PositiveIntegerField(null=False)
    required_library_id = models.PositiveIntegerField(null=False)
    dependency_type = models.CharField(null=False, max_length=31)

    class Meta:
        db_table = 'h5p_libraries_libraries'
        unique_together = (('library_id', 'required_library_id'))

class h5p_libraries_languages(models.Model):
    library_id = models.PositiveIntegerField(null=False)
    language_code = models.CharField(null=False, max_length=31)
    language_json = models.TextField(null=False,
        help_text='The translations defined in json format')

    class Meta:
        db_table = 'h5p_libraries_languages'
        ordering = ['language_code', 'library_id']
        verbose_name = 'Library-language'
        verbose_name_plural = 'Libraries-languages'
        unique_together = (('library_id', 'language_code'))

    def __unicode__(self):
        return self.language_code

    def __str__(self):
        return "%s" % (self.language_code)

class h5p_contents(models.Model):
    content_id = models.AutoField(primary_key=True,
        help_text='Identifier of the content')
    title = models.CharField(null=False, max_length=255)
    json_contents = models.TextField(null=False,
        help_text='The content in JSON format')
    embed_type = models.CharField(null=False, default='', max_length=127)
    disable = models.PositiveIntegerField(null=False, default=0)
    main_library_id = models.PositiveIntegerField(null=False,
        help_text='The library we first instanciate for this content')
    content_type = models.CharField(null=True, max_length=127,
        help_text='Content type as defined in h5p.json')
    author = models.CharField(null=True, max_length=127)
    license = models.CharField(null=True, blank=True, max_length=7)
    meta_keywords = models.TextField(null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    filtered = models.TextField(null=False,
        help_text='Filtered version of json_contents')
    slug = models.CharField(null=False, max_length=127,
        help_text='Human readable content identifier that is unique')

    class Meta:
        db_table = 'h5p_contents'
        ordering = ['title', 'author', 'content_id']
        verbose_name = 'Content'
        verbose_name_plural = 'Contents'

    def __unicode__(self):
        return 'Title:%s - Author:%s - Type:%s' % (self.title, self.author, self.content_type)

    def __str__(self):
        return "%s - %s" % (self.content_id, self.title)

    def get_absolute_url(self):
        return '%s?contentId=%s' % (reverse('h5pcontent'), self.content_id)

class h5p_points(models.Model):
    content_id = models.PositiveIntegerField(null=False,
        help_text='Identifier of the content having a score')
    uid = models.PositiveIntegerField(null=False,
        help_text='Identifier of the user with this score')
    started = models.PositiveIntegerField(null=False,
        help_text='Timestamp. Indicates when the user started watching the video')
    finished = models.PositiveIntegerField(null=False, default=0,
        help_text='Timestamp. Indicates when the user finished watching the video')
    points = models.PositiveIntegerField(null=True, blank=True,
        help_text='Current point of the user')
    max_points = models.PositiveIntegerField(null=True, blank=True,
        help_text='Maximum point that the user can have')

    class Meta:
        db_table = 'h5p_points'
        ordering = ['content_id', 'uid']
        verbose_name = 'Score'
        verbose_name_plural = 'Scores'
        unique_together = (('content_id', 'uid'))

class h5p_content_user_data(models.Model):
    user_id = models.PositiveIntegerField(null=False)
    content_main_id = models.PositiveIntegerField(null=False)
    sub_content_id = models.PositiveIntegerField(null=False)
    data_id = models.CharField(null=False, max_length=127)
    timestamp = models.PositiveIntegerField(null=False)
    data = models.TextField(null=False)
    preloaded = models.PositiveSmallIntegerField(null=True)
    delete_on_content_change = models.PositiveSmallIntegerField(null=True)

    class Meta:
        db_table = 'h5p_content_user_data'
        unique_together = (('user_id', 'content_main_id',
                            'sub_content_id', 'data_id'))

class h5p_events(models.Model):
    user_id = models.PositiveIntegerField(null=False,
        help_text='Identifier of the user who caused this event')
    created_at = models.IntegerField(null=False)
    type = models.CharField(null=False, max_length=63,
        help_text='Type of the event. If it concerns a library, a content or a user')
    sub_type = models.CharField(null=False, max_length=63,
        help_text='Action of the event. Example : Create, Delete, Edit...')
    content_id = models.PositiveIntegerField(null=False,
        help_text='If not 0, identifier of the content affected by this event')
    content_title = models.CharField(null=False, max_length=255,
        help_text='If not blank, title of the content affected by this event')
    library_name = models.CharField(null=False, max_length=127,
        help_text='If not blank, name of the library affected by this event')
    library_version = models.CharField(null=False, max_length=31,
        help_text='If not blank, version of the library affected by this event')

    class Meta:
        db_table = 'h5p_events'
        ordering = ['created_at', 'type', 'sub_type']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

class h5p_counters(models.Model):
    type = models.CharField(null=False, max_length=63)
    library_name = models.CharField(null=False, max_length=127)
    library_version = models.CharField(null=False, max_length=31)
    num = models.PositiveIntegerField(null=False)

    class Meta:
        db_table = 'h5p_counters'
        unique_together = (('type', 'library_name', 'library_version'))

class H5P(Resource):
    data_ini = models.DateTimeField(_('Init Date'), auto_now_add = False)
    data_end = models.DateTimeField(_('End Date'), auto_now_add = False)
    h5p_resource = models.ForeignKey(h5p_contents, verbose_name = _("H5P content"), related_name = "h5p_actual_content", null = True)

    class Meta:
        verbose_name = _("H5P")
        verbose_name_plural = _("H5Ps")

    def __str__(self):
        return self.name

    def access_link(self):
        if self.show_window:
            return reverse_lazy(
                "h5p:window_view", args=(), kwargs={"slug": self.slug}
            )

        return reverse_lazy("h5p:view", args=(), kwargs={"slug": self.slug})

    def update_link(self):
        return "h5p:update"

    def delete_link(self):
        return "h5p:delete"

    def delete_message(self):
        return _("Are you sure you want delete this H5P component")

    def get_data_ini(self):
        return self.data_ini
    
    def get_data_end(self):
        return self.data_end

class UserScores(models.Model):
    h5p_component = models.ForeignKey(H5P, verbose_name = _("H5P component"), related_name = 'user_score', null = True)
    student = models.ForeignKey(User, verbose_name = _('User'), related_name = 'h5p_student', null = True)
    max_score = models.DecimalField(max_digits = 5, decimal_places = 2, verbose_name = _('Max Score'))
    score = models.DecimalField(max_digits = 5, decimal_places = 2, verbose_name = _('Student Score'))
    interaction_date = models.DateTimeField(_('Interaction Date'), auto_now_add = True)