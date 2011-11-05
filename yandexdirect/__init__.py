# encoding=utf-8

"""Yandex.Direct bindings for Python.

Implements API v4.

http://api.yandex.ru/direct/doc/concepts/About.xml
"""

import logging
import simplejson
import urllib

try:
    from google.appengine.api import urlfetch
    HAVE_URLFETCH = True
except ImportError:
    import urllib2
    HAVE_URLFETCH = False


__author__ = "Justin Forest <hex@umonkey.net>, Gasoid <rinat@sgreen.ru>"
__license__ = "GNU LGPL"


class AuthError(Exception):
    pass


class Client(object):
    """Contains functions to access the Yandex API."""
    def __init__(self, application_id, login, auth_token):
        self.application_id = application_id
        self.login = login
        self.auth_token = auth_token

    def call_method(self, method, param=None):
        """Calls an API method."""
        payload = {"method": method, "application_id": self.application_id,
            "login": self.login, "token": self.auth_token}
        if param is not None:
            payload["param"] = param

        data = simplejson.loads(self._fetch(self._get_api_root(method), simplejson.dumps(payload)))
        if type(data) != dict:
            logging.error("Got %s instead of a dict: %s" % (type(data), data))
            enigma.error(500, "Could not interpret a Yandex.API response.")

        if "error_code" in data:
            if data["error_code"] == 53:
                raise AuthError(data["error_str"])
            message = data["error_detail"]
            if data["error_str"]:
                if message:
                    message += "; "
                message += data["error_str"]
            raise Exception("Error %s calling method %s: %s" % (data["error_code"], method, message))
        if "data" not in data:
            raise Exception("Yandex.API response has no \"data\" block.")
        return data["data"]

    def _get_api_root(self, method):
        """Returns the API URL for the specified method."""
        # GetClientsList is very slow in v4 API for some reason.
        if method == "GetClientsList":
            return "https://soap.direct.yandex.ru/json-api/v3/"
        return "https://soap.direct.yandex.ru/json-api/v4/"

    def _fetch(self, url, args):
        """Performs a POST request, returns the response body.  Uses App Engine's urlfetch where available to disable
        SSL certificate checking (which doesn't work with this API because Yandex has 'Yandex Direct' as the CNAME."""
        if HAVE_URLFETCH:
            res = urlfetch.fetch(url=url, payload=args, method=urlfetch.POST, validate_certificate=False)
            return res.content
        else:
            return urllib2.urlopen(url, args).read()

    def __repr__(self):
        return "<yandexdirect.Client application_id=%s login=%s>" % (self.application_id, self.login)

    def get_auth_url(self, state=None):
        return "https://oauth.yandex.ru/authorize?response_type=code&client_id=%s&state=%s" % (self.application_id, urllib.quote(state or ""))

    def get_token_by_code(self, code):
        """Used during OAuth authentication."""
        payload = "grant_type=authorization_code&code=%s&client_id=%s&client_secret=%s" % (code, self.application_id,self.auth_token)
        response = self._fetch("https://oauth.yandex.ru/token", payload)

        data = simplejson.loads(response)
        if "access_token" not in data:
            logging.debug("OAuth response: %s" % data)
            raise AuthError("OAuth server replied with no access token (see the debug log).")
        return data["access_token"]

    def GetVersion(self):
        """Returns the API version number."""
        return self.call_method("GetVersion")

    def Ping(self, login=None, token=None):
        """Pings the API server, must return 1 on success."""
        old_login = self.login
        old_token = self.auth_token
        try:
            if login is not None:
                self.login = login
            if token is not None:
                self.auth_token = token
            return self.call_method("PingAPI")
        finally:
            self.login = old_login
            self.auth_token = old_token

    def GetBanners(self, campaign_ids, archive=None):
        _filter = {}
        if archive == True:
            _filter["StatusArchive"] = ["Yes"]
        elif archive == False:
            _filter["StatusArchive"] = ["No"]

        return self.call_method("GetBanners", {
            "CampaignIDS": campaign_ids,
            "GetPhrases": "WithPrices",
            "Filter": _filter,
        })

    def GetBannerPhrases(self, banner_ids):
        return self.call_method("GetBannerPhrases", banner_ids)

    def GetClientInfo(self, names):
        return self.call_method("GetClientInfo", names)

    def GetClientsList(self, archive=False):
        StatusArch = "No"
        if archive:
            StatusArch = "Yes"
        return self.call_method("GetClientsList", {
            "Filter": {
                "StatusArch": StatusArch,
            }
        })

    def GetSubClients(self, client, archive=None):
        _filter = {"Login": client}
        if archive == True:
            _filter["Filter"] = {"StatusArch": True}
        elif archive == False:
            _filter["Filter"] = {"StatusArch": False}
        return self.call_method("GetSubClients", _filter)

    def GetCampaignsList(self, clients=None, with_client_info=False):
        """Возвращает описания кампаний указанных клиентов.  Если клиенты не указаны, возвращает описания всех кампаний
        (выполняет более одного запроса)."""

        all_clients = None
        if clients is None:
            all_clients = dict([(client["Login"], client) for client in self.GetClientsList()])
            clients = all_clients.keys()

        if not isinstance(clients, list):
            raise ValueError("clients must be a list")

        campaigns = []
        while clients:
            campaigns.extend(self.call_method("GetCampaignsList", clients[:100]))
            del clients[:100]

        if with_client_info and all_clients is not None:
            for idx, campaign in enumerate(campaigns):
                campaigns[idx]["Login_details"] = all_clients[campaign["Login"]]

        return campaigns

    def UpdatePrices(self, updates, step=100):
        if not isinstance(updates, (list, tuple)):
            raise Exception('update_phrases() expects a list.')
        while updates:
            payload = updates[:step]
            del updates[:step]
            self.call_method("UpdatePrices", payload)

    def SetAutoPrice(self, updates):
        self.call_method("SetAutoPrice", updates)
    def GetBalance(self, campaigns):
        if not isinstance(campaigns, (list, tuple)):
            raise Exception('campaigns must be a list.')
        balances = self.call_method("GetBalance", campaigns)
        return balances
