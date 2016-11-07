import uuid


def random_file_name(extension, prefix=None):
    """ Generate a random file name given an extension and
        an optional prefix. """

    if prefix is None:
        return "/tmp/%s.%s" % (uuid.uuid4(), extension)
    else:
        return "/tmp/%s_%s.%s" % (prefix, uuid.uuid4(), extension)
