from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured

def load_module(path):
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    mod = import_module(module)
    return getattr(mod, attr)

def load_backend(path): # full 'some.path.to.Path'
    try:
        return load_module(path)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing subscription backend %s: "%s"' % (path, e))
    except ValueError, e:
        raise ImproperlyConfigured('Error importing subscription backends. Is SUBSCRIPTION_BACKENDS a correctly defined dictionary?')
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" subscription backend' % (module, attr))

def load_notification(path):
    try:
        return load_module(path)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing notification %s: "%s"' % (path, e))
    except ValueError, e:
        raise ImproperlyConfigured('Error importing notification class')
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" notification backend' % (app, path[1]))

def get_backends():
    from django.conf import settings
    backend_objs = {}
    for backend_name, backend_path in settings.SUBSCRIPTION_BACKENDS.items():
        backend_objs[backend_name] = load_backend(backend_path)
        backend_objs[backend_name].name = backend_name

    if not backend_objs:
        raise ImproperlyConfigured('No subscription backends have been defined. Does SUBSCRIPTION_BACKENDS contain anything?')

    return backend_objs
