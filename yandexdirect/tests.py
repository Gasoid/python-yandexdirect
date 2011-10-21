# encoding=utf-8

import os
import sys
import unittest

import yandexdirect

SETTINGS_FILENAME = ".yandex_direct.conf"


class YandexTests(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(SETTINGS_FILENAME):
            raise Exception("Please create %s with application_id, login and auth_token, one per line" % SETTINGS_FILENAME)
        application_id, login, token = file(SETTINGS_FILENAME, "rb").read().strip().split("\n")
        self.client = yandexdirect.Client(application_id, login, token)

    def test_auth_url(self):
        self.client.application_id = "appid"
        self.assertEquals("https://oauth.yandex.ru/authorize?response_type=code&client_id=appid&state=state", self.client.get_auth_url("state"))

    def test_ping(self):
        self.assertEquals(1, self.client.Ping())

    def test_bad_ping(self):
        self.assertRaises(yandexdirect.AuthError, self.client.Ping, ["wrong client", "wrong token"])

    def test_version(self):
        self.assertEquals(4, self.client.GetVersion())


def run_tests():
    loader = unittest.defaultTestLoader

    print "Logging to tests.log"
    sys.stderr = sys.stdout = open("tests.log", "wb")

    suite = loader.loadTestsFromTestCase(YandexTests)
    unittest.TextTestRunner().run(suite)


if __name__ == "__main__":
    run_tests()
