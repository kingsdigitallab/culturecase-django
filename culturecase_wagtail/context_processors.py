
def settings(request):
    from django.conf import settings as djsettings

    var_names = ['DEBUG', 'GA_ID']

    ret = {
        k: getattr(djsettings, k, None) for k in var_names
    }

    return ret
