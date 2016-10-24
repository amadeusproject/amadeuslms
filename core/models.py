from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.models import User
from autoslug.fields import AutoSlugField
# Create your models here.

class MimeType(models.Model):
    typ = models.CharField(_('Type'), max_length=100, unique=True)
    icon = models.CharField(_('Icon'), max_length=50, unique=True)

    class Meta:
        verbose_name= _('Amadeus Mime Type')
        verbose_name_plural = _('Amadeus Mime Types')

    def get_icon(self, type):
        pass

    def __str__(self):
        return self.typ

class Action(models.Model):
    """
	It represents an Action on the program by a User such as "create post",
	"visualize post", etc. It is supposed to be created everytime we want an aciton
    """

    name = models.CharField(_('Name'), max_length = 100)
    slug = AutoSlugField(_("Slug"), populate_from=('name'), unique=True)
    created_date = models.DateField(_('Created Date'), auto_now_add=True)

    class Meta:
        verbose_name = "Action"
        verbose_name_plural = "Actions"

    def __str__(self):
        return self.name


class Resource(models.Model):
    """
		It represents the resource where the action was applied on.
		Example: Pool was answered (Resource: Pool), PDF was visualized(Resource: PDF).

        Attributes:
            @name: name of the resource affected, it will be unique because a resource can be affecte
            by a huge amount of actions
            @created_date: The date the resource was created
            @link: Which URL made that resource able to find
    """

    name = models.CharField(_('Name'), max_length =100)
    slug = AutoSlugField(_("Slug"), populate_from='name', unique=True)
    created_date = models.DateField(_('Created Date'), auto_now_add=True)
    url = models.CharField(_('URL'), max_length =100, default="")


    class Meta:
        verbose_name = "Resource"
        verbose_name_plural = "Resources"

    def __str__(self):
        return self.name


class Action_Resource(models.Model):

    action = models.ForeignKey(Action , verbose_name= _('Action_Applied'))
    resource = models.ForeignKey(Resource, verbose_name = _('Resource'))

    class Meta:
        verbose_name = "Action_Resource"
        verbose_name_plural = "Action_Resources"

    def __str__(self):
        return ''.join([self.action.name, " / ", self.resource.name])


class Notification(models.Model):
    """
    Attributes:
        @message: The message that will be shown on the notification prompt
        @user: The User that the notification will be sent to.
        @read: Whether or not the user has read the notification.
        @datetime: The time the notification was created
        @action_resource: The Object that holds the information about which action was perfomed on the Resource
        @actor: The user who applied the action
    """
    
    message = models.TextField(_('Message'))
    user = models.ForeignKey(User, related_name = _('%(class)s_Actor'), verbose_name= _('User'))
    read = models.BooleanField(_('Read'), default = False)
    datetime = models.DateTimeField(_("Date and Time of action"), auto_now_add = True)
    action_resource = models.ForeignKey(Action_Resource, verbose_name = _('Action_Resource'))
    actor = models.ForeignKey(User, related_name = _('%(class)s_Performer'), verbose_name= _('Perfomer'), null = True)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    def __str__(self):
        return self.message

class Log(models.Model):
    datetime = models.DateTimeField(_("Date and Time of action"), auto_now_add = True)
    user = models.ForeignKey(User, verbose_name = _('Actor'))
    action_resource = models.ForeignKey(Action_Resource, verbose_name = _('Action_Resource'))

    class Meta:
        verbose_name = _('Log')
        verbose_name_plural = _('Logs')
