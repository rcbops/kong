from resttest.jsontools import nested_search
from resttest.resttest import Retryable
from time import sleep
from utils import SERVICES
import tests
import os

nova = SERVICES['nova']
glance = SERVICES['glance']
neutron = SERVICES['neutron']
neutron_api_ver = 'v2.0'


def md5sum_file(path):
    from hashlib import md5
    md5sum = md5()
    with open(path, 'rb') as file:
        for chunk in iter(lambda: file.read(8192), ''):
            md5sum.update(chunk)
    return md5sum.hexdigest()


def glance_headers(name, file, format, kernel=None, ramdisk=None):
    h = {'x-image-meta-is-public': 'true',
            'x-image-meta-name': name,
            'x-image-meta-disk-format': format,
            'x-image-meta-container-format': format,
            'Content-Length': '%s' % os.path.getsize(file),
            'Content-Type': 'application/octet-stream'}
    if kernel:
        h['x-image-meta-property-Kernel_id'] = str(kernel)
    if ramdisk:
        h['x-image-meta-property-Ramdisk_id'] = str(ramdisk)
    return h


class TestNovaAPI(tests.FunctionalTest):

    tags = ['nova', 'nova-api', 'nova-neutron']

    @Retryable
    def ping_host(self, address, netns=None):
        """
        Ping a host ever <interval> seconds, up to a maximum of <max_wait>
        seconds for until the address is succesfully pingable, or the
        maximum wait interval has expired
        """
        import subprocess
        ping_command='ping -c1 -q %s > /dev/null 2>&1' % (address)
        if netns:
            ping_command='ip netns exec %s ping -c1 -q %s > /dev/null 2>&1' % (netns, address)
        try:
            retcode = subprocess.call(ping_command, shell=True)
            if retcode == 0:
                return True
        except OSError, e:
            print "Error running external ping command: ", e
            print retcode
            return False
        raise AssertionError("Could not ping host %s" % address)

    def test_nova_list_flavors(self):
        r, d = nova.GET("/flavors", code=200)
        if len(d['flavors']) == 0:
            raise AssertionError("No flavors configured in openstack")
        if len(nested_search("/flavors/*/name=m1.tiny",
                             nova.GET("/flavors")[1])) == 0:
            raise AssertionError("No flavor m1.tiny found.")

    def test_verify_extensions(self):
        request, content = nova.GET("/extensions", code=200)
        required_extensions = set(['os-simple-tenant-usage',
                                   'os-hosts',
                                   'os-quota-sets',
                                   'os-flavor-extra-specs',
                                   'os-create-server-ext',
                                   'os-keypairs',
                                   'os-floating-ips'])
        aliases = [e['alias'] for e in content['extensions']]
        for i in required_extensions:
            if not i in aliases:
                raise AssertionError("Required extension %s not provided" % i)

    def test_001_upload_kernel_to_glance(self):
        kernel = self.config['environment']['kernel']
        headers = glance_headers("test-kernel", kernel, "aki")
        md5 = md5sum_file(kernel)
        with open(kernel, "rb") as image_file:
            r, d = glance.POST_raw_with_keys_eq(
                "/images",
                 {"/image/name": "test-kernel",
                  "/image/checksum": md5},
                  headers=headers,
                  body=image_file, code=201)
    test_001_upload_kernel_to_glance.tags = ['glance', 'nova', 'nova-neutron']

    def test_002_upload_initrd_to_glance(self):
        initrd = self.config['environment']['initrd']
        headers = glance_headers("test-ramdisk", initrd, "ari")
        md5 = md5sum_file(initrd)
        with open(initrd, "rb") as image_file:
            r, data = glance.POST_raw_with_keys_eq(
                "/images",
                {"/image/name": "test-ramdisk",
                 "/image/checksum": md5},
                headers=headers,
                body=image_file,
                code=201)
    test_002_upload_initrd_to_glance.tags = ['glance', 'nova', 'nova-neutron']

    def test_003_upload_image_to_glance(self):
        kernel = glance.GET("/images?name=test-kernel")[1]['images'][0]['id']
        initrd = glance.GET("/images?name=test-ramdisk")[1]['images'][0]['id']
        image = self.config['environment']['image']
        headers = glance_headers("test-image", image, "ami", kernel, initrd)
        md5 = md5sum_file(image)
        with open(image, "rb") as image_file:
            r, d = glance.POST_raw_with_keys_eq(
                "/images",
                {"/image/name": "test-image",
                 "/image/checksum": str(md5)},
                 headers=headers,
                 body=image_file,
                 code=201)
    test_003_upload_image_to_glance.tags = ['glance', 'nova', 'nova-neutron']

    def test_004_verify_active_images(self):
        for name in ["test-kernel", "test-ramdisk", "test-image"]:
            i = glance.GET("/images?name=%s" % name)[1]['images'][0]['id']
            nova.GET_with_keys_eq("/images/%s" % i,
                                  {"/image/status": "ACTIVE"},
                                  code=200)

    def test_005_upload_glance_image_sync(self):
        initrd = self.config['environment']['initrd']
        headers = glance_headers("test-ramdisk-glance-image-sync",
                                  initrd,
                                  "ari")
        md5 = md5sum_file(initrd)
        with open(initrd, "rb") as image_file:
            r, data = glance.POST_raw_with_keys_eq(
                "/images",
                {"/image/name": "test-ramdisk-glance-image-sync",
                 "/image/checksum": md5},
                headers=headers,
                body=image_file,
                code=201)
    test_005_upload_glance_image_sync.tags = ['glance-image-sync']

    def test_006_verify_glance_image_sync(self):
        api_nodes = self.config['glance-image-sync']['api_nodes']
        r, d = glance.GET("/images?name=test-ramdisk-glance-image-sync")
        i = d['images'][0]['id']
        # give some time to allow the sync to happen
        sleep(10)
        for api in api_nodes.split(','):
            glance.GET("/images/%s" % i, code=200)
    test_006_verify_glance_image_sync.tags = ['glance-image-sync']

    def test_007_delete_glance_image_sync(self):
        api_nodes = self.config['glance-image-sync']['api_nodes']
        r, d = glance.GET("/images?name=test-ramdisk-glance-image-sync")
        i = d['images'][0]['id']
        glance.DELETE("/images/%s" % i, code=200)
        # give some time to allow the sync to happen
        sleep(10)
        for api in api_nodes.split(','):
            glance.GET("/images/%s" % i, code=404)
    test_007_delete_glance_image_sync.tags = ['glance-image-sync']

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

    test_150_create_security_group.tags = ['nova']

    def test_151_create_security_group_rule(self):
        gid = nested_search("/security_groups/*/name=kongsec/id",
                            nova.GET("/os-security-groups")[1])[0]
        nova.POST("/os-security-group-rules",
                  body={"security_group_rule":
                        {"from_port": "-1", "to_port": "-1",
                         "parent_group_id": "%s" % gid,
                         "cidr": "0.0.0.0/0", "ip_protocol": "icmp"}},
                         code=200)

    test_151_create_security_group_rule.tags = ['nova']

    def test_160_security_group_create(self):
        resp, body = neutron.POST(
            '/%s/security-groups.json' % neutron_api_ver,
            body={'security_group': {
                  'name': 'test-sec-group'}},
            code=201)

        secgroup_id = body['security_group']['id']

        resp, body = neutron.GET_with_keys_eq(
            '/%s/security-groups/%s.json' % (neutron_api_ver, secgroup_id),
            {'/security_group/name': 'test-sec-group'},
            code=200)

    test_160_security_group_create.tags = ['nova-neutron']


    def test_161_security_group_rule_create(self):
        secgroup_id = nested_search(
            'security_groups/*/name=test-sec-group/id',
            neutron.GET('/%s/security-groups' % neutron_api_ver, code=200)[1])[0]

        resp, body = neutron.POST(
            '/%s/security-group-rules.json' % neutron_api_ver,
            body={'security_group_rule': {
                  'ethertype': 'IPv4',
                  'direction': 'ingress',
                  'protocol': 'ICMP',
                  'security_group_id': '%s' % secgroup_id}})

        secgroup_rule_id = body['security_group_rule']['id']

        resp, body = neutron.GET_with_keys_eq(
            '/%s/security-group-rules/%s.json' % (neutron_api_ver, secgroup_rule_id),
            {'/security_group_rule/protocol': 'icmp'},
            code=200)

    test_161_security_group_rule_create.tags = ['nova-neutron']

    def test_165_net_create(self):
        resp, body = neutron.POST(
            '/%s/networks.json' % neutron_api_ver,
            body={'network': {
                  'name': self.config['nova']['network_label'],
                  'admin_state_up': 'True'}},
            code=201)

        network_id = body['network']['id']

        resp, body = neutron.GET_with_keys_eq(
            '/%s/networks/%s' % (neutron_api_ver, network_id),
            {'/network/status': 'ACTIVE'},
            code=200, timeout=20, delay=2)

    test_165_net_create.tags = ['nova-neutron']

    def test_170_subnet_create(self):
        network_id = nested_search(
            'networks/*/name=%s/id' % self.config['nova']['network_label'],
            neutron.GET('/%s/networks' % neutron_api_ver, code=200)[1])[0]

        resp, body = neutron.POST(
            '/%s/subnets.json' % neutron_api_ver,
            body={'subnet': {
                  'network_id': '%s' % network_id,
                  'ip_version': 4,
                  'cidr': '192.168.78.0/29',
                  'name': 'test-subnet'}},
            code=201)

    test_170_subnet_create.tags = ['nova-neutron']

    def test_190_create_server_neutron(self):
        network_id = nested_search(
            'networks/*/name=%s/id' % self.config['nova']['network_label'],
            neutron.GET('/%s/networks' % neutron_api_ver, code=200)[1])[0]
        image = nova.GET("/images?name=test-image")[1]['images'][0]['id']
        flavor = nested_search("/flavors/*/name=m1.tiny/id",
                               nova.GET("/flavors")[1])[0]


        r, d = nova.POST("/servers",
                        body={"server": 
                                 {"name": "testing server creation", 
                                 "imageRef": image, "flavorRef": flavor, 
                                 "max_count": 1, "min_count": 1, 
                                 "networks": [{"uuid": network_id}]
                                 }
                             },
                        code=202) 
        server_id = d['server']['id']
        r, d = nova.GET_with_keys_eq("/servers/%s" % server_id,
                                     {"/server/status": "ACTIVE"},
                                     code=200, timeout=60, delay=5)
        ip = d['server']['addresses'][self.config['nova']['network_label']][0]['addr']

        netns="qdhcp-%s" % network_id
        if not self.ping_host(ip, netns=netns, delay=5, timeout=200):
            raise AssertionError("Server is active but does not ping")

    test_190_create_server_neutron.tags = ['nova-neutron']


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
            if self.ping_host(i['addr'], delay=5, timeout=200):
                good = True
        if not good:
            raise AssertionError("Server is active but does not ping")

    test_200_create_server.tags = ['nova']

    def test_201_list_servers(self):
        r, d = nova.GET("/servers/detail", code=200)
        servers = nested_search("/servers/*/name=testing server creation", d)
        if len(servers) == 0:
            raise AssertionError("No server found with name testing server " +
                                 "creation")

#    test_201_list_servers.tags = ['nova']

    def test_202_get_server_details(self):
        r, d = nova.GET("/servers/detail")
        sid = nested_search("/servers/*/name=testing server creation/id", d)[0]
        r, d = nova.GET("/servers/%s" % sid, code=200)

#    test_202_get_server_details.tags = ['nova']

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

#    test_203_update_server.tags = [ 'nova']

    def test_210_list_addresses(self):
        label = self.config['nova']['network_label']
        r, d = nova.GET("/servers")
        sid = nested_search("/servers/*/name=testing server creation/id", d)[0]
        addrs = nova.GET('/servers/%s/ips' % (sid),
                         code=200)[1]
        if not len(nested_search('/addresses/%s' % (label), addrs)[0]) > 0:
            raise AssertionError("No addresses found for network %s" % (label))

#    test_210_list_addresses.tags = ['nova']

    def test_300_delete_server(self):
        r, d = nova.GET("/servers/detail")
        sid = nested_search("/servers/*/name=testing server creation/id", d)[0]
        nova.DELETE("/servers/%s" % sid, code=204)
        r, d = nova.GET("/servers/%s" % sid,
            code=404, timeout=60, delay=5)

#    test_300_delete_server.tags = ['nova']

    def test_305_delete_test_images_from_glance(self):
        for name in ["test-kernel", "test-ramdisk", "test-image"]:
            i = glance.GET("/images?name=%s" % name)[1]['images'][0]['id']
            glance.DELETE("/images/%s" % i, code=200)
            r, d = nova.GET_with_keys_eq(
                "/images/%s" % i,
                {"/image/status": "DELETED"},
                code=200, timeout=60, delay=5)
    test_305_delete_test_images_from_glance.tags = ['glance', 'nova', 'nova-neutron']

    def test_901_delete_security_group_rule(self):
        data = nova.GET("/os-security-groups")[1]
        gid = nested_search("/security_groups/*/name=kongsec/id",
                            data)[0]
        rids = nested_search("/security_groups/*/rules/*/parent_group_id=" +\
                            str(gid) + "/id", data)
        for rid in rids:
            nova.DELETE("/os-security-group-rules/%s" % rid, code=202)

    test_901_delete_security_group_rule.tags = ['nova']


    def test_902_delete_security_group(self):
        gid = nested_search("/security_groups/*/name=kongsec/id",
                            nova.GET("/os-security-groups")[1])[0]
        nova.DELETE("/os-security-groups/%s" % gid, timeout=60,
                    delay=5, code=202)

    test_902_delete_security_group.tags = ['nova']

    def test_920_security_group_rule_delete(self):
        secgroup_id = nested_search(
            'security_groups/*/name=test-sec-group/id',
            neutron.GET('/%s/security-groups' % neutron_api_ver, code=200)[1])[0]
        resp, body = neutron.GET(
            '/%s/security-groups/%s' % (neutron_api_ver, secgroup_id))

        try:
            secgroup_rule_id = nested_search(
                'security_group/security_group_rules/*/protocol=icmp/id',
                body)[0]
            neutron.DELETE(
                '/%s/security-group-rules/%s.json'
                % (neutron_api_ver, secgroup_rule_id), code=204)
        except IndexError:
            pass

    test_920_security_group_rule_delete.tags = ['nova-neutron']

    def test_925_security_group_delete(self):
        resp, body = neutron.GET(
            '/%s/security-groups.json?fields=id&name=test-sec-group'
            % neutron_api_ver, code=200)

        security_group_ids = [p['id'] for p in body['security_groups']]

        for net in security_group_ids:
            neutron.DELETE(
                '/%s/security-groups/%s.json'
                % (neutron_api_ver, net), code=204)

    test_925_security_group_delete.tags = ['nova-neutron']

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

    def test_960_net_delete(self):
        resp, body = neutron.GET(
            '/%s/networks.json?fields=id&name=%s' 
                % (neutron_api_ver, self.config['nova']['network_label']), code=200)
        network_ids = [p['id'] for p in body['networks']]

        for net in network_ids:
            neutron.DELETE('/%s/networks/%s.json' % (neutron_api_ver, net), code=204)

    test_960_net_delete.tags = ['nova-neutron']
