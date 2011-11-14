import datetime

from django.db import models
from django.conf import settings

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

import subscription

class SubscriptionManager(models.Manager):
    def subscribe(self,user,obj):
        ct = ContentType.objects.get_for_model(obj)
        Subscription.objects.get_or_create(content_type=ct,object_id=obj.pk,user=user)

class NotificationManager(models.Manager):
    def emit(self,*args,**kwargs):
        backend = kwargs.pop('backend',None) or None
        notification_cls = kwargs.pop('notification_cls',None) or None

        backends = subscription.get_backends().values()
        if backend:
            backend_module = subscription.get_backends()[backend]()
            backends = [backend_module]

        for backend in backends:
            if notification_cls:
                notification_cls()(backend,*args,**kwargs)
                continue

            backend.emit(*args,**kwargs)

    def emit_notification(self,notification,*args,**kwargs):
        kwargs.update({'notification_cls': subscription.load_notification(notification)})

        self.emit(*args,**kwargs)

class Subscription(models.Model):
    user = models.ForeignKey('auth.User')
    content_type = models.ForeignKey('contenttypes.ContentType')
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    timestamp = models.DateTimeField(editable=False,default=datetime.datetime.now)
    objects = SubscriptionManager()
    notifications = NotificationManager()
    class Meta:
        db_table ="subscription"
        unique_together = ('user','content_type','object_id')

"""
Seems sensible to auto-subscribe people to objects they comment on.

Just send this with the comment_was_posted signal

def auto_subscribe(**kwargs):
    comment = kwargs.pop('comment')
    auto_subscribe_field = getattr(settings,'SUBSCRIPTION_AUTOSUBSCRIBE_PROFILE_FIELD','auto_subscribe')
    if getattr(comment.user.get_profile(),auto_subscribe_field,True):
        Subscription.objects.subscribe(user,comment.content_object)

comment_was_posted.connect(auto_subscribe, sender=CommentModel)
"""

"""
Make abstract, turn into emit backend
#comment_was_posted.connect(email_comment, sender=CommentModel)

def email_comment(**kwargs):
    comment = kwargs.pop('comment')
    request = kwargs.pop('request')

    site = Site.objects.get(id=settings.SITE_ID)

    supress_email_field = getattr(settings,'SUBSCRIPTION_EMAIL_SUPRESS_PROFILE_FIELD','no_email')
    t = loader.get_template('comments/email_comment_template.html')

    subscriptions = Subscription.objects.filter(content_type=comment.content_type,\
            object_id=comment.object_pk).exclude(user=comment.user)

    for i in subscriptions:
        if getattr(i.user.get_profile(),supress_email_field,False):
            continue

        c = {
            'domain': site.domain,
            'site_name': site.name,
            'c': comment,
            'delete': i.user.has_perm('comments.delete_comment'),
            'subscription': i,
        }
        if not i.user.email:
            continue

        send_mail(("%s - Comment on %s") % (site.name,comment.content_object), \
               t.render(RequestContext(request,c)), None, [i.user.email])
"""
