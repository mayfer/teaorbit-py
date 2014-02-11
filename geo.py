


class Geo(object):
    @staticmethod
    def _truncate(f, n):
        '''Truncates/pads a float f to n decimal places without rounding'''
        return float(('%.*f' % (n + 1, f))[:-1])

    @staticmethod
    def get_room_id(latitude, longitude):
        latitude = float(latitude)
        longitude = float(longitude)

        flat_lat = self._truncate(latitude, 2)
        flat_long = self._truncate(longitude, 2)

        poly = [
            ('%.2f' % (flat_lat + 0.00), '%.2f' % (flat_long - 0.00)),
            ('%.2f' % (flat_lat + 0.01), '%.2f' % (flat_long - 0.00)),
            ('%.2f' % (flat_lat + 0.01), '%.2f' % (flat_long - 0.01)),
            ('%.2f' % (flat_lat + 0.00), '%.2f' % (flat_long - 0.01)),
            ('%.2f' % (flat_lat + 0.00), '%.2f' % (flat_long - 0.00)),
        ]
        return '|'.join([ ','.join(coords) for coords in poly ])
