from resttest.jsontools import nested_search
from utils import SERVICES
import tests

nova = SERVICES['nova']


class TestNovaAPI2(tests.FunctionalTest):
    tags = ['nova', 'nova-api']

    def test_nova_list_flavors(self):
        r, d = nova.GET("/flavors", code=200)
        if len(d['flavors']) == 0:
            raise AssertionError("No flavors configured in openstack")
