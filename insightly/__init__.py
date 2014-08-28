#__init__.py

import requests
import copy
import json
from pprint import pformat
import urllib


class ResourceManager(object):
    """
    A class to manage sub resources (Resource)
    """
    id_field = None
    managed_class = None


    def __init__(self, base_url, headers):
        """ All the params are passed in by the Connection manager """
        self.base_url = base_url
        self.headers = headers

        self.url ="%s/%s" % (self.base_url, self.__class__.__name__)
        self.managed_class = self.__class__.__name__[0:-1]
        self.id_field = "%s_ID" % (self.managed_class.upper())


    def __get_managed_class_name(self):
        """ Gets the Resource class name this ResourceManager manages """
        self.managed_class = self.__class__.__name__[0:-1]
        # De-pluralize to get the Resource class name
        if len(self.__class__.__name__)>3 and self.__class__.__name__[-3]=="ies":
            self.managed_class = "%sy" % self.__class__.__name__[0:-3]


    def find(self, _id=None, query={}):
        """ Finds a sub resource this ResourceManager manages """
        url = self.url
        if _id:
            url = "%s/%s" % (url, _id)

        qs = ""
        if query and isinstance(query, dict) and len(query.keys())>0:
            qs = "?%s" % urllib.urlencode(query)

        # TODO: Handle pagination for large data sets
        results = requests.get("%s%s" % (url, qs), headers=self.headers)
        if not _id:
            for res in results.json():
                yield globals()[self.managed_class](self.base_url, self.headers, data=res)
        else:
            yield globals()[self.managed_class](self.base_url, self.headers, data=results.json())


class Resource(object):
    """ The Resource class """

    id_field = None
    details = {}
    url = None
    default_details = {}

    def __init__(self, base_url, headers, data={}):
        """ All the params are passed in from the Resource Manager """
        object.__setattr__(self, 'base_url', base_url)
        object.__setattr__(self, 'headers', headers)
        object.__setattr__(self, 'details', copy.deepcopy(self.default_details))
        if data and isinstance(data,dict) and len(data.keys())>0:
            details = copy.deepcopy(self.details)
            details.update(data)
            object.__setattr__(self, 'details', details)

        object.__setattr__(self, 'klassname', self.__class__.__name__)
        object.__setattr__(self, 'url', "%s/%s" % (self.base_url, self.__get_url_from_class(self.klassname)))
        object.__setattr__(self, 'id_field', "%s_ID" % (self.klassname.upper()))


    def __get_url_from_class(self, klassname):
        """ Gets the url based on the class name """
        if klassname[-1]=="y":
            return "%sies" % klassname[0:-1]
        else:
            return "%ss" % klassname


    def save(self):
        """ Persists the resource """
        results = None
        data = copy.deepcopy(self.details)

        if self.id_field in self.details.keys() and not self.details[self.id_field]==0:
            # Update with PUT
            results = requests.put(self.url, data=json.dumps(data), headers=self.headers)
        else:
            # Create new
            data[self.id_field] = 0
            results = requests.post(self.url, data=json.dumps(data), headers=self.headers)

        if results:
            #self.details = results.json()
            object.__setattr__(self, 'details', results.json())

        if results.status_code>399:
            raise Exception("HTTP %d on %s - %s" % (results.status_code, self.url, results.reason))


    def delete(self):
        """ Deletes the resource """
        results = None
        if self.id_field in self.details.keys():
            results = requests.delete("%s/%s" % (self.url, self.details[self.id_field]), headers=self.headers)

            if results.status_code>399:
                raise Exception("HTTP %d on %s - %s" % (results.status_code, self.url, results.reason))


    def __getattr__(self, key):
        if self.details and key in self.details.keys():
            return self.details[key]
        return None


    def __setattr__(self, key, value):
        if key in dir(self):
            super(self.__class__, self).__setattr__(key, value)
        else:
            self.details[key] = value
  

    def set(self, key, value):
        self.details[key] = value


class User(Resource):
    pass

class Users(ResourceManager):
    pass

class Contacts(ResourceManager):
    pass

class Contact(Resource):
    #default_details = {"ADDRESSES":[], "CONTACTINFOS":[], "CUSTOMFIELDS":[], "DATES":[], "TAGS":[], "LINKS":[], "CONTACTLINKS":[],  "EMAILLINKS":[] }
    pass

class Task(Resource):
    pass

class Opportunities(ResourceManager):
    pass

class Opportunity(Resource):
    pass


class Connection(object):
    """
    The connection class to hold information about the connection

    base_url = the API url
    headers = {
        "Content-type":"application/json", 
        "Authorization":"Basic %s" % base64.b64encode("%s:" % APIKEY)
        }

    """
    base_url = None
    headers = {}

    def __init__(self, base_url, headers):
        self.base_url = base_url
        self.headers = headers

    def __getattr__(self, key):
        obj = globals()[key](self.base_url, self.headers)
        return obj

