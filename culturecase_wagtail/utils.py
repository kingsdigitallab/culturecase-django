
def signup_to_newsletter(merge_vars):
    '''
    Subscribe a user to a Mailchimp newsletter

    merge_vars = {
        'EMAIL': '',
        'FNAME': '',
        'LNAME': '',
        'ORG': '',
    }

    Newsletter id and mailchimp account id should be set up in settings.py
    '''
    ret = True

    import mailchimp
    from django.conf import settings

    try:
        api = mailchimp.Mailchimp(settings.MAILCHIMP_API_KEY)
        res = api.lists.subscribe(
            settings.MAILCHIMP_LIST_ID,
            {'email': merge_vars['EMAIL']},
            merge_vars
        )
        print(res)
    except Exception:
        raise

    # res = api.lists.activity(settings.MAILCHIMP_LIST_ID)

    return ret
