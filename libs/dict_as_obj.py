class DictAsObj(dict):
    """
    Example:
    new_dict_as_obj = DictAsObj({'a': 1}, b=2, c=[3, 4])
    """

    def __init__(self, *args, **kwargs):
        super(DictAsObj, self).__init__(*args, **kwargs)

        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(DictAsObj, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(DictAsObj, self).__delitem__(key)
        del self.__dict__[key]
