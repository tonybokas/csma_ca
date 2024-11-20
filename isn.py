#!/usr/bin/env python


def isn(hours: int):
    if not isinstance(hours, int):
        raise Exception(f'expecting hours {type(1)}, but got {type(hours)}')

    # ((Hours x 60 mins x 60 seconds x 10^6 microseconds) / 4 increments))
    # modulo 2^32
    return f'{round(((hours * 60 * 60 * 10**6)/4) % 2**32):,d}'


isn('h')
