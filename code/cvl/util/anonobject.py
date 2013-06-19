__author__ = 'kostas'


class Object(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return ", ".join(["%s=%s" % (key,value) for key,value in self.__dict__.items()])