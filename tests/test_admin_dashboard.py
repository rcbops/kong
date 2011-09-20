# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack, LLC
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

""" Walkthrough the OpenStack Dashboard """

import tests
import unittest2

from splinter.browser import Browser
from pprint import pprint

class TestOpenstackDashboard(tests.FunctionalTest):
    def setUp(self):
        self.browser = ""

    def tearDown(self):
        self.browser = ""

    def _logIn(self):
        self.browser.visit("http://%s" % self.dash['host'])
        self.browser.fill('username', self.dash['admin_user'])
        self.browser.fill('password', self.dash['admin_pass'])
        button = self.browser.find_by_id('home_login_btn')
        button.click()

    def _logOut(self):
        drop_button = self.browser.find_by_id("drop_btn")
        drop_button.click()
        logout = self.browser.find_link_by_href("/auth/logout/")
        logout.click()

    def lookForError(self):
        self.assertFalse(self.browser.is_text_present("Error"))

    def validateOverview(self):
        self.assertTrue(self.browser.is_text_present("CPU"), 
            "CPU Status is not showing properly")
        self.assertTrue(self.browser.is_text_present("RAM"), 
            "RAM Status is not showing properly")
        self.assertTrue(self.browser.is_text_present("Disk"), 
            "Disk Status is not showing properly")

    @tests.skip_test("--Skipping--")
    def test_overview_page(self):
        self.browser = Browser()
        self._logIn()
        overview = self.browser.find_link_by_text("Overview")
        overview.click()
        self.lookForError()
        self.validateOverview()
        self._logOut()
        self.browser.quit()

    @tests.skip_test("--Skipping--")
    def test_instances_page(self):
        self.browser = Browser()
        self._logIn()
        instances = self.browser.find_link_by_text("Instances")
        instances.click()
        self.lookForError()
        self._logOut()
        self.browser.quit()

    def test_adding_a_keypair(self):
        self.browser = Browser()
        self._logIn()
        keypair = self.browser.find_link_by_text("Keypairs")
        keypair.click()
        self.lookForError()
        keypair_btn = self.browser.find_by_id("keypairs_create_link") 
        keypair_btn.click()
        self.browser.fill('name', "test_keypair_test")
        button = self.browser.find_by_value('Create Keypair')
        button.click()
        return_link = self.browser.find_link_by_partial_text("Return to keypairs")
        return_link.click()
        self.assertTrue(self.browser.is_text_present("test_keypair_test"),
            "Created keypair not found")
        delete_link = self.browser.find_by_id("delete_test_keypair_test")
        delete_link.click()
        # accept the js alert
        alert = self.browser.get_alert()
        alert.accept()
        # verify delete message
        self.assertTrue(self.browser.is_text_present(
            "Successfully deleted keypair: test_keypair_test"),
            "Keypair not successfully deleted")
        self._logOut()
        self.browser.quit()
