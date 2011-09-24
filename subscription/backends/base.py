from string import Formatter

from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User
from subscription.models import Subscription

__all__ = ['BaseBackend','SimpleEmailBackend']

class BaseBackend(object):
    def __call__(obj,*args,**kwargs):
        return obj.emit(*args,**kwargs)

    def get_recipients(self):
        if not self.subscribers_of:
            for recipient in self.send_only_to:
                return [recipient]

        self.content_type = ContentType.objects.get_for_model(self.subscribers_of)
        subscription_kwargs = {'content_type': self.content_type, 'object_id': self.subscribers_of.pk}
        if self.send_only_to:
            subscription_kwargs.update({'user__in': send_only_to})

        subscriptions = Subscription.objects.filter(**subscription_kwargs)

        if self.send_only_to:
            return User.objects.filter(pk__in=subscriptions.filter(user__in=self.send_only_to).values_list('user'))

        if self.dont_send_to:
            return User.objects.filter(pk__in=subscriptions.exclude(user__in=self.dont_send_to).values_list('user'))

        return User.objects.filter(pk__in=subscriptions.values_list('user'))

    def process_text(self):
        #explicit_format_options = [i[1] for i in Formatter().parse(self.text)]
        return self.text.format(self.format_kwargs)
        return text

    def emit(self,text,subscribers_of=None,dont_send_to=None,send_only_to=None,format_kwargs=None,queue=None,**kwargs):
        # subscribers_of - Thing people are subscribed to
        # dont_send_to / send_only_to - useful maybe?
        # text - string you want to emit.
        # format_kwargs - Will be applied to text a la: text.format(**format_kwargs)
        # **kwargs - Maybe you wrote a backend that wants more stuff than the above!!
        # CAREFUL: If you send a typo-kwarg it will just be sent to emit(), so no error will raise at this point.
        self.text = text
        self.subscribers_of = subscribers_of
        self.dont_send_to = dont_send_to
        self.send_only_to = send_only_to
        self.format_kwargs = format_kwargs
        self.queue = queue or 'default'
        self.kwargs = kwargs

        text = self.process_text()

        self.deliver(**kwargs)

    def deliver(self,**kwargs):
        for user in self.get_recipients():
            self.user_emit(user,self.process_text(),**kwargs)

    def user_emit(self,user,text,**kwargs):
        raise NotImplementedError("Override this!")

class SimpleEmailBackend(BaseBackend):
    def user_emit(self,user,subject,text,**kwargs):
        if not user.email:
            return

        send_mail(self.get_subject(),text,None,[user.email])

    def get_subject(self):
        return "Here's a subject!"
