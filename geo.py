
class Geo(object):
    def get_block_id(self, latitude, longitude):
        latitude = float(latitude)
        longitude = float(longitude)
        poly = [
            ('%.2f' % (latitude + 0.08), '%.2f' % (longitude - 0.06)),
            ('%.2f' % (latitude - 0.04), '%.2f' % (longitude - 0.06)),
            ('%.2f' % (latitude - 0.04), '%.2f' % (longitude + 0.06)),
            ('%.2f' % (latitude + 0.08), '%.2f' % (longitude + 0.06)),
            ('%.2f' % (latitude + 0.08), '%.2f' % (longitude - 0.06)),
        ]
        return '|'.join([ ','.join(coords) for coords in poly ])
