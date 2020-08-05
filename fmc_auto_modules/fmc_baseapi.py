import json
import sys
import requests
from copy import deepcopy
import logging as LOG
requests.packages.urllib3.disable_warnings()

headers = {'Content-Type': 'application/json'}

# Only allow the following objects
OBJECTS_TYPE_ALLOWED = [
    'fqdns',
    'hosts',
    'networks',
    'ranges',
]

HOSTS_OBJECTS_MAPPING = {}
NETWORKS_OBJECTS_MAPPING = {}
INTERFACES_OBJECTS_MAPPING = {}


def ConsoleEcho(msg):
    print(msg)


def _LOG(msg, log_level="info", logfile="/var/log/fmc_automation.log"):
    """
    Logging
    """
    # Print it on Console
    ConsoleEcho(msg)
    # Logging config
    LOG.basicConfig(
        filename=logfile,
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=LOG.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # Logging
    if log_level.lower() == "debug":
        LOG.debug(msg)
    elif log_level.lower() == "warning":
        LOG.warning(msg)
    else:
        LOG.info(msg)


class FmcApiHandler(object):
    """
    FMC's API handler
    """
    def __init__(self, fmcserver, username, password, domain='Global', sslverify=False):
        self.fmcserver = fmcserver
        self.username = username
        self.password = password
        self.sslverify = sslverify
        self.domain = domain
        self.baseuri = 'https://{}'.format(fmcserver)
        token_domain = self.get_token()
        self.token = token_domain['token']
        self.domain_uuid = token_domain['domain_uuid']
        headers['X-auth-access-token'] = self.token

    def _close_connection(self, resp):
        """
        Close connection
        """
        resp.connection.close()

    def get_token(self):
        """
        Get token
        """
        url = '{}/api/fmc_platform/v1/auth/generatetoken'.format(self.baseuri)
        try:
            resp = requests.post(
                url,
                headers=headers,
                auth=requests.auth.HTTPBasicAuth(self.username,self.password),
                verify=False
            )
            token = resp.headers.get('X-auth-access-token', default=None)
            domains = json.loads(resp.headers.get('DOMAINS'))
            if len(domains) == 1:
                domain_uuid = domains[0]["uuid"]
            elif len(domains) > 1:
                for key, value in enumerate(domains):
                    if value['name'] == self.domain:
                        domain_uuid = domains[key]['uuid']
            if token == None:
                _LOG("Token not found. Aborting.")
                self._close_connection(resp)
                sys.exit(1)
        except Exception as exp:
            _LOG(exp)
            self._close_connection(resp)
            sys.exit(1)
        return {'token': token, 'domain_uuid': domain_uuid}

    def get_version(self):
     """
     Get FMC server version
     """
     url = "{}/api/fmc_platform/v1/info/serverversion".format(self.baseuri)
     try:
         resp = requests.get(url, headers=headers, verify=self.sslverify)
     except requests.exceptions.HTTPError as exp:
         _LOG(exp)
     self._close_connection(resp)
     return resp.json()['items'][0]['serverVersion']

    def get_ftdnatpolicies(self, expanded=False):
        """
        GET FTD NAT policies.
        """
        if expanded:
            uri = ("/api/fmc_config/v1/domain/{}/policy/"
                   "ftdnatpolicies?expanded=true".format(self.domain_uuid)
                  )
        else:
            uri = ("/api/fmc_config/v1/domain/{}/policy/"
                   "ftdnatpolicies".format(self.domain_uuid)
                  )
        url = "{baseuri}{uri}".format(baseuri=self.baseuri, uri=uri)
        try:
            resp = requests.get(url, headers=headers, verify=self.sslverify)
        except requests.exceptions.HTTPError as exp:
            _LOG(exp)
        self._close_connection(resp)
        return resp.json()["items"]
    
    def get_autonatrules(self, natpolicy, expanded=False):
        """
        param:: ftdnatpolicy: the name of NAT policy.
        NAT rules are tied to NAT policy. 
        """
        # Get UUID of natpolicy
        natpolicy_uuid = None
        for key, value in enumerate(self.get_ftdnatpolicies()):
            if value["name"] == natpolicy:
                natpolicy_uuid = value["id"]
        # quit if NAT policy was not found
        if not natpolicy_uuid:
            _LOG("NatPolicy {} was not found.".format(natpolicy))
            sys.exit(1)
        # format target uri
        if expanded:
            uri = ("/api/fmc_config/v1/domain/{domain_uuid}/policy/"
                   "ftdnatpolicies/{natpolicy_uuid}/autonatrules?expanded=true".format(
                       domain_uuid=self.domain_uuid,
                       natpolicy_uuid=natpolicy_uuid)
                  )
        else:
            uri = ("/api/fmc_config/v1/domain/{domain_uuid}/policy/"
                   "ftdnatpolicies/{natpolicy_uuid}/autonatrules".format(
                       domain_uuid=self.domain_uuid,
                       natpolicy_uuid=natpolicy_uuid)
                  )
        url = "{baseuri}{uri}".format(baseuri=self.baseuri, uri=uri)
        try:
            resp = requests.get(url, headers=headers, verify=self.sslverify)
        except requests.exceptions.HTTPError as exp:
            _LOG(exp)
        self._close_connection(resp)
        return resp.json()["items"]

    def get_objects(self, objtype):
        """
        """
        # Get object count first so all objects can be retrived at once
        uri = "/api/fmc_config/v1/domain/{}/object/{}?limit=1".format(
            self.domain_uuid, objtype)
        url = "{}{}".format(self.baseuri, uri)
        try:
            resp = requests.get(url, headers=headers, verify=self.sslverify)
        except requests.exceptions.HTTPError as exp:
            _LOG(exp)
            return None
        count = resp.json()["paging"]["count"]
        uri = "/api/fmc_config/v1/domain/{}/object/{}?limit={}".format(
            self.domain_uuid, objtype, count)
        url = "{}{}".format(self.baseuri, uri)
        try:
            resp = requests.get(url, headers=headers, verify=self.sslverify)
        except requests.exceptions.HTTPError as exp:
            _LOG(exp)
            return None
        objects = resp.json()["items"]
        if not objects:
            _LOG("Could not retrieve objects - {}".format(objects))
            return None
        # Collect hosts mapping - a ditionary that mapped host_name to uuid
        COLLECTOR = {}
        for key, value in enumerate(objects):
            COLLECTOR[value["name"]] = value["id"]
        if objtype == "networks":
            global NETWORKS_OBJECTS_MAPPING
            NETWORKS_OBJECTS_MAPPING = COLLECTOR
        elif objtype == "hosts":
            global HOSTS_OBJECTS_MAPPING
            HOSTS_OBJECTS_MAPPING = COLLECTOR
        elif objtype == "interfaceobjects":
            global INTERFACES_OBJECTS_MAPPING
            INTERFACES_OBJECTS_MAPPING = COLLECTOR
        return COLLECTOR

    def create_ftdnatpolicy(self, payload):
        """
        Create NAT policy
        """
        uri = "/api/fmc_config/v1/domain/{}/policy/ftdnatpolicies".format(self.domain_uuid)
        url = "{}{}".format(self.baseuri, uri)
        try:
            msg = "Creating FTD NAT policy {}".format(payload["name"])
            _LOG(msg)
            resp = requests.post(
                url, data=json.dumps(payload),
                headers=headers, verify=self.sslverify
            )
        except requests.exceptions.HTTPError as exp:
            _LOG(exp)
            return resp.status_code, exp
        # close connection before returning
        self._close_connection(resp)
        return resp.status_code, resp.json()

    def create_autonatrule(self, payload):
        """
        Create Auto NAT rule in a target NAT policy
        """
        natpolicies = self.get_ftdnatpolicies()
        for key, value in enumerate(natpolicies):
            if value["name"] == payload["targetNatPolicy"]:
                target_natpolicy_uuid = value["id"]
                del payload["targetNatPolicy"]
                break
        # Reformat payload in a way FMC REST supported
        # Note that get_objects() can/should be made dynamic instead of "hosts" - might
        # need a new param to specify target object
        if self.get_objects("hosts"):
            originalNetwork_uuid = HOSTS_OBJECTS_MAPPING[payload["originalNetwork"]]
        else:
            return (404, "UUID of {} not found.".format(payload["originalNetwork"]))
        if self.get_objects("hosts"):
            translatedNetwork_uuid =  HOSTS_OBJECTS_MAPPING[payload["translatedNetwork"]]
        else:
            return (404, "UUID of {} not found.".format(payload["translatedNetwork"]))
        if self.get_objects("interfaceobjects"):
            sourceInterface_uuid = INTERFACES_OBJECTS_MAPPING[payload["sourceInterface"]]
        else:
            return (404, "UUID of {} not found.".format(payload["sourceInterface"]))
        if self.get_objects("interfaceobjects"):
            destinationInterface_uuid =  INTERFACES_OBJECTS_MAPPING[payload["destinationInterface"]]
        else:
            return (404, "UUID of {} not found.".format(payload["destinationInterface"]))
        payload["originalNetwork"] = {"type": "Host", "id": originalNetwork_uuid}
        payload["translatedNetwork"] = {"type": "Host", "id": translatedNetwork_uuid}
        payload["sourceInterface"] = {"type": "SecurityZone", "id": sourceInterface_uuid}
        payload["destinationInterface"] = {"type": "SecurityZone", "id": destinationInterface_uuid}
        uri = ("/api/fmc_config/v1/domain/{domain_uuid}/policy/ftdnatpolicies/"
               "{nat_id}/autonatrules".format(
                   domain_uuid=self.domain_uuid,
                   nat_id=target_natpolicy_uuid)
            )
        url = "{baseuri}{uri}".format(baseuri=self.baseuri, uri=uri)
        try:
            resp = requests.post(
                url, data=json.dumps(payload),
                headers=headers, verify=self.sslverify
            )
        except requests.exceptions.HTTPError as exp:
            _LOG(exp)
            return resp.status_code, exp
        self._close_connection(resp)
        return resp.status_code, resp.json()

    def create_object(self, payload):
        """
        param:: payload: dictionary of object configuration
        The real object type in FMC.
        """
        # Quit if it's not supported object type
        if not payload["type"].lower() in OBJECTS_TYPE_ALLOWED:
            _LOG("{} is not supported object type.".format(payload["type"]))
            sys.exit(1)
        url = "{baseuri}{uri}{obj_type}".format(
                baseuri=self.baseuri,
                uri="/api/fmc_config/v1/domain/{}/object/".format(self.domain_uuid),
                obj_type=payload["type"]
            )
        try:
            msg = "Creating {name} of type={obj_type} with value={value}".format(
                name=payload["name"],
                obj_type=payload["type"].lower(),
                value=payload["value"]
            )
            _LOG(msg)
            resp = requests.post(
                url, data=json.dumps(payload),
                headers=headers, verify=self.sslverify
            )
        except requests.exceptions.HTTPError as exp:
            _LOG(exp)
            return resp.status_code, exp
        # close connection before returning
        self._close_connection(resp)
        return resp.status_code, resp.json()
