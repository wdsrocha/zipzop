def rsa_to_str(x):
    return str(x).replace('{', 'foo').replace('}', 'bar')


def str_to_rsa(x):
    return eval(x.replace('foo', '{').replace('bar', '}'))
