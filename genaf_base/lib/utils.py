
_QUERY_CLASS_ = None

def get_query_class():
    global _QUERY_CLASS_
    assert _QUERY_CLASS_
    return _QUERY_CLASS_

def set_query_class(cls):
    global _QUERY_CLASS_
    _QUERY_CLASS_ = cls


def detect_buffer( buf ):
    """ this function returns the modified buffer and the delimiter of 
        CSV/tab-delimited file
        
        return (buf, delimiter)
    """

    # find our new line character, this is for Mac Excel blunder

    n_count = buf.count('\n')
    r_count = buf.count('\r')

    if n_count == 0 and r_count > 0:
        # Mac Excel
        buf = buf.replace('\r', '\n')
        n_count = r_count
    elif r_count > n_count:
        raise RuntimeError('Invalid text content')

    # we detect delimiter by the higher number of occurence
    tab_count = buf.count('\t')
    comma_count = buf.count(',')

    if comma_count > tab_count and comma_count > n_count:
        return (buf, ',')
    return (buf, '\t')


