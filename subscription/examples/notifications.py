from django.contrib.sites.models import Site

class Comment(object):
    queue = "comment"
    def __call__(cls,*args,**kwargs):
        return cls.emit(*args,**kwargs)

    def emit(self, backend, instance, request):
        site = Site.objects.get_current()
        dont_send_to = None
        if request.user.is_authenticated() and instance.user == request.user:
            dont_send_to = [request.user]

        if backend.name == "email":
            email_body = "%s commented on %s\r\n\r\nhttp://%%s/" % \
                (instance.user, instance.content_object, site.domain, \
                instance.content_object.get_absolute_url())

            backend.emit(instance.user,subject="New comment on %s",body=email_body,dont_send_to=dont_send_to,subscribers_of=instance)

        if backend.name == "redis":
            backend().emit("[[%s]] commented on %s" % (instance.user.username,instance.content_object),\
                subscribers_of=instance.content_object,dont_send_to=dont_send_to,queue=self.queue)
