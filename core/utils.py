import json

JSON_DUMPS_STRING_LIMIT = 50

def json_dumps(dictionary):
    """ Custom version of json.dumps which truncates long string fields. """
    return json.dumps(_truncate_strs(dictionary))

def _truncate_strs(dictionary):
    """ Given a dictionary, explore it using depth first search (DFS)
    and truncate the values of keys which are "too long".

    """
    # Edge case - dictionary is in fact not a dictionary, but a string
    if type(dictionary) != dict:
        result = str(dictionary)
        if len(result) > JSON_DUMPS_STRING_LIMIT:
            result = result[0:JSON_DUMPS_STRING_LIMIT] + '... (truncated)'
        return result

    result = {}
    for k, v in dictionary.iteritems():
        # If value is a dictionary, recursively truncate big strings
        if type(v) == dict:
            result[k] = _truncate_strs(v)
        # If it's a large string, truncate it
        elif (type(v) == str or type(v) == unicode) and len(v) > JSON_DUMPS_STRING_LIMIT:
            result[k] = v[0:JSON_DUMPS_STRING_LIMIT] + '... (truncated)'
        # Otherwise, copy any type of thing
        else:
            result[k] = v
    return result
