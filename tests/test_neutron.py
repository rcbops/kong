from utils import SERVICES
import tests
from resttest.jsontools import nested_search
import time

neutron = SERVICES['network']
k = SERVICES['keystone']
admin = SERVICES['keystone-admin']
user = k.get_config()[1]
project = k.get_config()[3]
api_ver = 'v2.0'


class TestNeutronAPI(tests.FunctionalTest):
    tags = ['neutron']

    def test_001_list_agents(self):
        agent_id = neutron.GET('/%s/agents' % api_ver, code=200)

    def test_002_agent_show(self):
        agent_id = nested_search('agents/*/id', neutron.GET('/%s/agents' % api_ver, code=200)[1])[0]
        neutron.GET('/%s/agents/%s' % (api_ver, agent_id), code=200)

    def test_003_ext_list(self):
        neutron.GET('/%s/extensions.json' % api_ver, code=200)

    def test_004_ext_show(self):
        neutron.GET('/%s/extensions/agent.json' % api_ver, code=200)

    def test_005_net_list(self):
        neutron.GET('/%s/networks.json' % api_ver, code=200)

    def test_006_net_list_on_dhcp_agent(self):
        dhcp_agent_id = nested_search('agents/*/agent_type=DHCP agent/id', neutron.GET('/%s/agents' % api_ver, code=200)[1])
        if dhcp_agent_id:
            neutron.GET('/%s/subnets.json?id=%s' % (api_ver, dhcp_agent_id), code=200)
        else:
            pass

    def test_007_net_create(self):
        resp, body = neutron.POST(
            '/%s/networks.json' % api_ver,
            body={'network':
            {'name': 'test-network', 'admin_state_up': 'True'}},
            code=201)

        network_id = body['network']['id']

        resp, body = neutron.GET_with_keys_eq(
            '/%s/networks/%s' % (api_ver, network_id),
            {'/network/status': 'ACTIVE'},
            code=200, timeout=20, delay=2)

    def test_008_net_show(self):
        network_id = nested_search('networks/*/name=test-network/id', neutron.GET('/%s/networks' % api_ver, code=200)[1])[0]

        neutron.GET('/%s/networks/%s' % (api_ver, network_id), code=200)

    def test_009_net_update(self):
        network_id = nested_search('networks/*/name=test-network/id', neutron.GET('/%s/networks' % api_ver, code=200)[1])[0]

        resp, body = neutron.PUT(
            '/%s/networks/%s.json' % (api_ver, network_id),
            body={'network':
            {'name': 'a-new-test-network'}},
            code=200)

        resp, body = neutron.GET_with_keys_eq(
            '/%s/networks/%s' % (api_ver, network_id),
            {'/network/name': 'a-new-test-network'},
            code=200)

        neutron.PUT('/%s/networks/%s.json' % (api_ver, network_id),
                body={'network': {'name': 'test-network'}}, code=200)

    def test_010_dhcp_agent_network_add(self):
        dhcp_agent_id = nested_search('agents/*/agent_type=DHCP agent/id', neutron.GET('/%s/agents' % api_ver, code=200)[1])[0]
        network_id = nested_search('networks/*/name=test-network/id', neutron.GET('/%s/networks' % api_ver, code=200)[1])[0]

        resp, body = neutron.POST('/%s/agents/%s/dhcp-networks.json'
            % (api_ver, dhcp_agent_id),
            body={'network_id': '%s' % network_id},
            code=201)

#        # check network is on the dhcp agent (net-list-on-dhcp-agent)
#        resp, body = neutron.GET('/%s/agents/%s/dhcp-networks.json?id=%s'
#            % (api_ver, dhcp_agent_id, network_id))
#
#        # check dhcp agent is on the network detail (dhcp-agent-list-hosting-net)
#        resp, body = neutron.GET('/%s/networks/%s/dhcp-agents.json?id=%s'
#            % (api_ver, network_id, dhcp_agent_id))
#


    def test_011_port_create(self):
        network_id = nested_search('networks/*/name=test-network/id', neutron.GET('/%s/networks' % api_ver, code=200)[1])[0]

        resp, body = neutron.POST(
            '/%s/ports.json' % api_ver,
            body={'port':
            {'network_id': '%s' % network_id,
            'admin_state_up': True,
            'name': 'test-port'}},
            code=201)

        port_id = body['port']['id']

        resp, body = neutron.GET_with_keys_eq(
            '/%s/ports/%s' % (api_ver, port_id),
            {'/port/admin_state_up': True},
            code=200, timeout=10, delay=2)

#    def test_xxxx_port_list(self):
#    def test_xxxx_port_show(self):
#    def test_xxxx_port_update(self):
#    def test_xxxx_quota_list(self):
#    def test_xxxx_quota_show(self):
#    def test_xxxx_quota_update(self):
#    def test_xxxx_security_group_create(self):
#    def test_xxxx_security_group_list(self):
#    def test_xxxx_security_group_rule_create(self):
#    def test_xxxx_security_group_rule_list(self):
#    def test_xxxx_security_group_rule_show(self):
#    def test_xxxx_security_group_show(self):
#    def test_xxxx_subnet_create(self):
#    def test_xxxx_subnet_list(self):
#    def test_xxxx_subnet_show(self):
#    def test_xxxx_subnet_update(self):


#    def test_xxxx_security_group_rule_delete(self):
#    def test_xxxx_security_group_delete(self):
#    def test_xxxx_quota_delete(self):
    def test_068_port_delete(self):
        resp, body = neutron.GET('/%s/ports.json?fields=id&name=test-port' % api_ver, code=200)
        port_ids = [p['id'] for p in body['ports']]

        for port in port_ids:
            neutron.DELETE('/%s/ports/%s.json' % (api_ver, port), code=204)

#    def test_xxxx_subnet_delete(self):
    def test_069_dhcp_agent_network_remove(self):
        resp, body = neutron.GET('/%s/networks.json?fields=id&name=test-network' % api_ver, code=200)
        network_ids = [p['id'] for p in body['networks']]
        dhcp_agent_id = nested_search('agents/*/agent_type=DHCP agent/id', neutron.GET('/%s/agents' % api_ver, code=200)[1])[0]

        for net in network_ids:
            resp, body = neutron.DELETE('/%s/agents/%s/dhcp-networks/%s' % (api_ver, dhcp_agent_id, net), code=204)

    def test_070_net_delete(self):
        resp, body = neutron.GET('/%s/networks.json?fields=id&name=test-network' % api_ver, code=200)
        network_ids = [p['id'] for p in body['networks']]

        for net in network_ids:
            neutron.DELETE('/%s/networks/%s.json' % (api_ver, net), code=204)

#
#    def test_002_list_resources(self):
#        neutron.GET('/%s/resources' % api_ver, code=200)
#
#    def test_003_list_users(self):
#        neutron.GET('/%s/users' % api_ver, code=200)
#
#    def test_004_list_projects(self):
#        neutron.GET('/%s/projects' % api_ver, code=200)
#
#    def test_005_list_meters_for_user(self):
#        response, data = admin.GET("/users")
#        userid = nested_search("/users/*/name=%s/id" % user, data)[0]
#        neutron.GET('/%s/users/%s/meters'
#                       % (api_ver, userid), code=200)
#
#    def test_006_list_meters_for_project(self):
#        response, data = admin.GET("/tenants")
#        projectid = nested_search("/tenants/*/name=%s/id" % project, data)[0]
#        neutron.GET('/%s/projects/%s/meters'
#                       % (api_ver, projectid), code=200)
#
#    def test_007_list_resources_for_user(self):
#        response, data = admin.GET("/users")
#        userid = nested_search("/users/*/name=%s/id" % user, data)[0]
#        neutron.GET('/%s/users/%s/resources'
#                       % (api_ver, userid), code=200)
#
#    def test_008_list_resources_for_project(self):
#        response, data = admin.GET("/tenants")
#        projectid = nested_search("/tenants/*/name=%s/id" % project, data)[0]
#        neutron.GET('/%s/projects/%s/resources'
#                       % (api_ver, projectid), code=200)
