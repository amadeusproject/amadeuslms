def always_as_child(fn):
    """ 
        Tries to run child model method if relevant
        should be applied on KnowsChild child class
    """
    def f(self, *args, **kwargs):
        child_self = self.as_child()
        f_parent = getattr(self.__class__, fn.__name__)
        f_child = getattr(child_self.__class__, fn.__name__)

        if f_parent != f_child:
            return f_child(child_self, *args, **kwargs)
        else:
            return fn(self, *args, **kwargs)
    
    return f