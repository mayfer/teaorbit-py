
class Geo(object):
    def get_block_id(self, latitude, longitude):
        latitude = float(latitude)
        longitude = float(longitude)
        poly = [
            ('%.2f' % latitude, '%.2f' % longitude),
            ('%.2f' % (latitude - 0.01), '%.2f' % longitude),
            ('%.2f' % (latitude - 0.01), '%.2f' % (longitude + 0.01)),
            ('%.2f' % latitude, '%.2f' % (longitude + 0.01)),
            ('%.2f' % latitude, '%.2f' % longitude),
        ]
        return '|'.join([ ','.join(coords) for coords in poly ])
