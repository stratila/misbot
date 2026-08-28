import itertools


def chunked(iterable, size):
    it = iter(iterable)
    while chunk := list(itertools.islice(it, size)):
        yield chunk
