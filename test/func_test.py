# coding=utf-8
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class TestBookmarks(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.get('http://localhost:5000')

    def tearDown(self):
        self.driver.close()

    def test_name_in_h1(self):
        USER_NAME = 'q'
        elem_login = self.driver.find_element_by_name('login')
        elem_login.send_keys(USER_NAME)
        elem_pwd = self.driver.find_element_by_name('pwd')
        elem_pwd.send_keys('1')
        elem_pwd.send_keys(Keys.RETURN)
        elem_h1 = self.driver.find_element_by_tag_name('h1')
        self.assertTrue(USER_NAME in elem_h1.text)
