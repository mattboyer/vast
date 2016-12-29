'''Autonomous Systems

   If you are currently engineering an AS, careful thought should be
   taken to register appropriately sized CIDR blocks with your
   registration authority in order to minimize the number of advertised
   prefixes from your AS.  In the perfect world that number can, and
   should, be as low as one.
'''


class AS(object):
    '''Models a single Autonomous System'''
    def __init__(self):
        self.asn = int()
        self.prefixes = set()
