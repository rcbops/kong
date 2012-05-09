from resttest.jsontools import nested_search
from utils import SERVICES
import tests
import os

nova = SERVICES['nova']
glance = SERVICES['glance']


def glance_headers(name, file, format, kernel=None, ramdisk=None):
    h = {'x-image-meta-is-public': 'true',
            'x-image-meta-name': name,
            'x-image-meta-disk-format': format,
            'x-image-meta-container-format': format,
            'Content-Length': '%d' % os.path.getsize(file),
            'Content-Type': 'application/octet-stream'}
    if kernel:
        h['x-image-meta-property-Kernel_id'] = kernel
    if ramdisk:
        h['x-image-meta-property-Ramdisk_id'] = ramdisk
    return h


class TestNovaAPI(tests.FunctionalTest):

    tags = ['nova', 'nova-api']

    def ping_host(self, address, interval, max_wait):
        """
        Ping a host ever <interval> seconds, up to a maximum of <max_wait>
        seconds for until the address is succesfully pingable, or the
        maximum wait interval has expired
        """
        import time
        import subprocess
        start = time.time()
        while(time.time() - start < max_wait):
            try:
                retcode = subprocess.call(
                    'ping -c1 -q %s > /dev/null 2>&1' % (address),
                    shell=True)
                if retcode == 0:
                    return True
            except OSError, e:
                print "Error running external ping command: ", e
                print retcode
                return False
            time.sleep(2)
        return False

    def test_nova_list_flavors(self):
        r, d = nova.GET("/flavors", code=200)
        if len(d['flavors']) == 0:
            raise AssertionError("No flavors configured in openstack")
        if len(nested_search("/flavors/*/name=m1.tiny",
                             nova.GET("/flavors")[1])) == 0:
            raise AssertionError("No flavor m1.tiny found.")

    def test_verify_extensions(self):
        request, content = nova.GET("/extensions", code=200)
        required_extensions = {'os-simple-tenant-usage',
                               'os-hosts',
                               'os-quota-sets',
                               'os-flavor-extra-specs',
                               'os-create-server-ext',
                               'os-keypairs',
                               'os-floating-ips'}
        aliases = [e['alias'] for e in content['extensions']]
        for i in required_extensions:
            if not i in aliases:
                raise AssertionError("Required extension %s not provided" % i)

    def test_001_upload_kernel_to_glance(self):
        kernel = self.config['environment']['kernel']
        headers = glance_headers("test-kernel", kernel, "aki")
        md5 = self._md5sum_file(kernel)
        with open(kernel, "rb") as image_file:
            r, d = glance.POST_raw_with_keys_eq(
                "/images",
                 {"/image/name": "test-kernel",
                  "/image/checksum": md5},
                  headers=headers,
                  body=image_file, code=201)
    test_001_upload_kernel_to_glance.tags = ['glance', 'nova']

    def test_002_upload_initrd_to_glance(self):
        initrd = self.config['environment']['initrd']
        headers = glance_headers("test-ramdisk", initrd, "ari")
        md5 = self._md5sum_file(initrd)
        with open(initrd, "rb") as image_file:
            r, data = glance.POST_raw_with_keys_eq(
                "/images",
                {"/image/name": "test-ramdisk",
                 "/image/checksum": md5},
                headers=headers,
                body=image_file,
                code=201)
    test_002_upload_initrd_to_glance.tags = ['glance', 'nova']

    def test_003_upload_image_to_glance(self):
        kernel = glance.GET("/images?name=test-kernel")[1]['images'][0]['id']
        initrd = glance.GET("/images?name=test-ramdisk")[1]['images'][0]['id']
        image = self.config['environment']['image']
        headers = glance_headers("test-image", image, "ami", kernel, initrd)
        md5 = self._md5sum_file(image)
        with open(image, "rb") as image_file:
            r, d = glance.POST_raw_with_keys_eq(
                "/images",
                {"/image/name": "test-image",
                 "/image/checksum": md5},
                 headers=headers,
                 body=image_file,
                 code=201)
    test_003_upload_image_to_glance.tags = ['glance', 'nova']

    def test_004_verify_active_images(self):
        for name in ["test-kernel", "test-ramdisk", "test-image"]:
            i = glance.GET("/images?name=%s" % name)[1]['images'][0]['id']
            nova.GET_with_keys_eq("/images/%s" % i,
                                  {"/image/status": "ACTIVE"},
                                  code=200)

    def test_verify_not_blank_limits(self):
        r, d = nova.GET_with_keys_ne("/limits",
                                     {"/limits": {}},
                                     code=200)

    def test_150_create_security_group(self):
        nova.POST("/os-security-groups",
                  body={"security_group":
                        {"name": "kongsec",
                         "description": "for testing only"}},
                         code=200)

    def test_151_create_security_group_rule(self):
        gid = nested_search("/security_groups/*/name=kongsec/id",
                            nova.GET("/os-security-groups")[1])[0]
        nova.POST("/os-security-group-rules",
                  body={"security_group_rule":
                        {"from_port": "-1", "to_port": "-1",
                         "parent_group_id": "%s" % gid,
                         "cidr": "0.0.0.0/0", "ip_protocol": "icmp"}},
                         code=200)

    def test_200_create_server(self):
        image = nova.GET("/images?name=test-image")[1]['images'][0]['id']
        flavor = nested_search("/flavors/*/name=m1.tiny/id",
                               nova.GET("/flavors")[1])[0]
        r, d = nova.POST("/servers",
                         body={"server": {"name": "testing server creation",
                            "flavorRef": flavor, "imageRef": image,
                            "security_groups": [{"name": "kongsec"}]}},
                         code=202)
        server_id = d['server']['id']
        r, d = nova.GET_with_keys_eq("/servers/%s" % server_id,
                                     {"/server/status": "ACTIVE"},
                                     code=200, timeout=60, delay=5)
        net = d['server']['addresses'][self.config['nova']['network_label']]
        good = False
        for i in net:
            if self.ping_host(i['addr'], 5, 60):
                good = True
        if not good:
            raise AssertionError("Server is active but does not ping")

    def test_201_list_servers(self):
        r, d = nova.GET("/servers/detail", code=200)
        servers = nested_search("/servers/*/name=testing server creation", d)
        if len(servers) == 0:
            raise AssertionError("No server found with name testing server " +
                                 "creation")

    def test_202_get_server_details(self):
        r, d = nova.GET("/servers/detail")
        sid = nested_search("/servers/*/name=testing server creation/id", d)[0]
        r, sssssssssssd = nova.GET("/servers/%s" % sid, code=200)

    def test_203_update_server(self):
        r, d = nova.GET("/servers/detail")
        sid = nested_search("/servers/*/name=testing server creation/id", d)[0]
        name = "updated"
        nova.PUT_with_keys_eq(
            "/servers/%s" % sid,
            {"/server/name": name},
            body={"server": {"name": name}},
            code=200)
        nova.PUT("/servers/%s" % sid,
                 body={"server":
                       {"name": "testing server creation"}})

    def test_210_list_addresses(self):
        label = self.config['nova']['network_label']
        r,d = nova.GET("/servers")
        sid = nested_search("/servers/*/name=testing server creation/id", d)[0]
        addrs = nova.GET('/servers/%s/ips' % (sid),
                         code=200)[1]
        if not len(nested_search('/addresses/%s' % (label), addrs)[0]) > 0:
            raise AssertionError("No addresses found for network %s" % (label))

    def test_900_delete_server(self):
        r, d = nova.GET("/servers/detail")
        sid = nested_search("/servers/*/name=testing server creation/id", d)[0]
        nova.DELETE("/servers/%s" % sid, code=204)

    def test_997_delete_test_images_from_glance(self):
        for name in ["test-kernel", "test-ramdisk", "test-image"]:
            i = glance.GET("/images?name=%s" % name)[1]['images'][0]['id']
            glance.DELETE("/images/%s" % i, code=200)
    test_997_delete_test_images_from_glance.tags = ['glance', 'nova']

    def test_901_delete_security_group_rule(self):
        data = nova.GET("/os-security-groups")[1]
        gid = nested_search("/security_groups/*/name=kongsec/id",
                            data)[0]
        rids = nested_search("/security_groups/*/rules/*/parent_group_id=" +\
                            str(gid) + "/id", data)
        for rid in rids:
            nova.DELETE("/os-security-group-rules/%s" % rid, code=202)

    def test_902_delete_security_group(self):
        gid = nested_search("/security_groups/*/name=kongsec/id",
                            nova.GET("/os-security-groups")[1])[0]
        nova.DELETE("/os-security-groups/%s" % gid, timeout=60,
                    delay=5, code=202)

    def test_901_delete_security_group_rule_diablo_final(self):
        data = nova.GET("/os-security-groups")[1]
        gid = nested_search("/security_groups/*/name=kongsec/id",
                            data)[0]
        rids = nested_search("/security_groups/*/rules/*/parent_group_id=" +\
                            str(gid) + "/id", data)
        try:
            for rid in rids:
                nova.DELETE("/os-security-group-rules/%s" % rid, code=202)
        except ValueError:
            pass

    def test_902_delete_security_group_diablo_final(self):
        gid = nested_search("/security_groups/*/name=kongsec/id",
                            nova.GET("/os-security-groups")[1])[0]
        nova.DELETE("/os-security-groups/%s" % gid, timeout=60,
                    delay=5, code=404)
