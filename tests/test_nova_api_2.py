from resttest.jsontools import nested_search
from utils import SERVICES
import tests

nova = SERVICES['nova']


# def test_020_list_flavors_v1_1(self):
#     path = self.nova['path'] + '/flavors'
#     http = httplib2.Http()
#     headers = {'X-Auth-User': '%s' % (self.keystone['user']),
#                'X-Auth-Token': '%s' % (self.nova['X-Auth-Token'])}
#     response, content = http.request(path, 'GET', headers=headers)
#     data = json.loads(content)
#     for i in data['flavors']:
#         if i['name'] == "m1.tiny":
#             self.flavor['id'] = i['id']
#             self.assertEqual(response.status, 200)
#     self.assertNotEqual(content, '{"flavors": []}')
# test_020_list_flavors_v1_1.tags = ['nova', 'nova-api']

class TestNovaAPI2(tests.FunctionalTest):
    tags = ['nova', 'nova-api']
    
    def test_nova_list_flavors(self):
        r, d = nova.GET("/flavors",code=200)
        if len(d['flavors']) == 0:
            raise AssertionError("No flavors configured in openstack")

    
