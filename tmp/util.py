
def dec_to_bin(value, numdigits=0):
    """ Returns binary representation with specified number of digits.
    >>> print dec_to_bin(10)
    >>> [1, 0, 1, 0]
    >>> print dec_to_bin(234, 10)
    >>> [0, 0, 1, 1, 1, 0, 1, 0, 1, 0]
    >>> print ''.join(str(d) for d in dec_to_bin(234, 10))
    >>> 0011101010
    """
    digits = []
    while value > 0:
        if (value & 1) == 1: digits.insert(0, 1)
        else: digits.insert(0, 0)
        value >>= 1
    # Add lead zeros if required
    if numdigits and len(digits) < numdigits:
        digits[:0] = [0]*(numdigits - len(digits))
    return digits
# dec_to_bin()

def bin_to_dec(row):
    """ Returns decimal representation.
    >>> print bin_to_dec([1, 0, 1, 0]
    >>> 10
    """
    return int(''.join([str(item) for item in row]), 2)
# bin_to_dec
