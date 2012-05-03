from resttest.jsontools import nested_search
from utils import SERVICES, r
import tests

nova = SERVICES['nova']
glance = SERVICES['glance']



class TestNovaAPI2(tests.FunctionalTest):
    tags = ['nova', 'nova-api', 'keystone']

    def test_nova_list_flavors(self):
        r, d = nova.GET("/flavors", code=200)
        if len(d['flavors']) == 0:
            raise AssertionError("No flavors configured in openstack")

    @tests.skip_test("Needs create server first")
    def test_nova_list_servers(self):
        r, d = nova.GET("/servers", code=200)
        if len(d['servers']) == 0:
            raise AssertionError("No servers found at all")
        elif len(nested_search("/servers/*/name=testserver", d)) < 1:
            raise AssertionError("Could not find your test server")

    def test_verify_extensions(self):
        request, content = nova.GET("/extensions", code=200)
        required_extensions = {'os-simple-tenant-usage': 1,
                               'os-hosts': 1,
                               'os-quota-sets': 1,
                               'os-flavor-extra-specs': 1,
                               'os-create-server-ext': 1,
                               'os-keypairs': 1,
                               'os-floating-ips': 1}
        aliases = [ e['alias'] for e in content['extensions']]
        for i in required_extensions:
            if not i in aliases:
                raise AssertionError("Required extension %s not provided" % i)

    @tests.skip_test("currently not working")
    def test_upload_kernel_to_glance(self):
        kernel = self.config['environment']['kernel']
        headers = {'x-image-meta-is-public': 'true',
                   'x-image-meta-name': 'test-kernel',
                   'x-image-meta-disk-format': 'aki',
                   'x-image-meta-container-format': 'aki',
                   'Content-Length': '%d' % os.path.getsize(kernel),
                   'Content-Type': 'application/octet-stream'}

        image_file = open(kernel, "rb")
        response, content = r.POST("%s/images" %
                                        glance.endpoint, headers=headers,
                                        body=image_file, code=201)
    test_upload_kernel_to_glance.tags = ['glance', 'nova']
