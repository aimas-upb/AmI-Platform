from bottle import abort, request

def query_param(name, transform, **kwargs):
    """
    Wrapps a handle function with definition of query parameters.
    You can use it like this:
    
        >>> @route('/session_list', method='GET')
        >>> @query_param('start', int, default = 0)
        >>> @query_param('end', int, default = None)
        >>> def get_session_list(start, end):
        >>>     return (start, end)            
        >>> 
    """
    def decorator(func):    
        def wrapper(*wrapper_wargs, **wrapper_kwargs):            
            if name not in request.query:
                if 'default' not in kwargs:
                    abort(403, 'Missing parameter: %s' % name)
                else:
                    wrapper_kwargs[name] = kwargs['default']
            else:
                try:
                    wrapper_kwargs[name] = transform(request.query[name])
                except ValueError:
                    abort(403, 'Wrong parameter format for: %s' % name)

            return func(*wrapper_wargs, **wrapper_kwargs)
        return wrapper
    return decorator