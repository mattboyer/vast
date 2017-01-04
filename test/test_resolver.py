from unittest import TestCase, skip

class test_RIPE_request(TestCase):

    @skip
    def test_url(self):
        r = RIPE_request('foo')
        self.assertEquals('https://stat.ripe.net/data/foo', r.url)

    @skip
    def test_get(self):
        r = RIPE_requests.announced_prefixes
        print(dir(RIPE_requests))
        #r.get({'resource': 'AS3333'})
