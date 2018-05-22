#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    tool-queue.server
    ~~~~~~~~~~~~~~
    Tool and Classroom queue api server
    :copyright: © 2018 by Dallas Makerspace. All Rights Reserved.
    :license: BSD, see LICENSE for more details.
"""

__author__     = "Dwight Spencer"
__copyright__  = "Copyright ©2018 Dallas Makerspace. All Rights Reserved"
__credits__    = ["Dwight Spencer <denzuko@dallasmakerspace.org>"]
__license__    = 'BSD 3-clause "New" or "Revised License"'
__maintainer__ = "Dwight spencer"
__email__      = "infrastructure@dallasmakerspace.org"
__status__     = "5 - Production/Stable"
__audience__   = [
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research'
]
__language__   = 'Programming Language :: Python :: 2.7'

__major__   = 1
__minor__   = 0
__patch__   = 0
__version__ = '.'.join([str(__major__), str(__minor__), str(__patch__)])

# See https://pypi.python.org/pypi?%3Aaction=list_classifiers
__classifiers__ = [ __status__, __language__ ] + __audience__

import os
from redis import StrictRedis

from eve import Eve
from flask.ext.bootstrap import Bootstrap
from eve_docs import eve_docs

## Schema
class SchemaObject(dict):
    def __init__(self):
        self['item_title'] = self.__class__.__name__.lower()
        self['schema'] = {}
        
    def add_field(self, field={}):
        self['schema'].update(field)
        
    def add_lookup(self, lookup={}):
        self['additional_lookup'] = lookup
        
class Schema(dict):
    def __init__(self):
        self['people'] = People()
        self['computers'] = Computers()

## Caching
class Caching(StrictRedis):
    def __init__(self, app):
        super(self).__init__()
        super(self).from_url(os.environ.get('MONGO_HOST', 'redis://cache:6379'))

## Models
class People(SchemaObject):
    def __init__(self):
        super(People, self).__init__()
        self.addlookup({
            'url': 'regex("[\w]+")',
            'field': 'lastname'
        })
        self.add_field({'firstname': { 'type': str(), 'maxlength': int(10), 'minlength': int(1) })
        self.add_field({'lastname':  { 'type': str(), 'maxlength': int(10), 'minlength': int(1), 'required': True, 'unique': True })
        
### AWS lambda, sensible DB connection settings are stored in environment variables.
class ApiSettings(dict):
    def __init__(self):
        self['URL_PREFIX'] = '/api'
        self['API_VERSION'] = str(__version__)

        self.database()
        self.methods()
        self.media()
        self.cache()
        self.schema()
        
    def database(self):
        self['MONGO_HOST']       = os.environ.get('MONGO_HOST')
        self['MONGO_PORT']       = os.environ.get('MONGO_PORT')
        self['MONGO_USERNAME']   = os.environ.get('MONGO_USERNAME')
        self['MONGO_PASSWORD']   = os.environ.get('MONGO_PASSWORD')
        self['MONGO_DBNAME']     = os.environ.get('MONGO_DBNAME')
        
    def methods(self, methods=list())
    
        if not methods: 
          methods = ['GET', 'POST', 'DELETE']
        
        self['RESOURCE_METHODS'] = methods
        self['ITEM_METHODS'] = methods
        
    def media(self, media_info=[], as_base64=False, as_url=True)
    
        if not media_info:
          media_info = ['content_type', 'name', 'length']
          
        self['EXTENDED_MEDIA_INFO']           = media_info
        self['RETURN_MEDIA_AS_BASE64_STRING'] = as_base64
        self['RETURN_MEDIA_AS_URL']           = as_url
        
    def cache(self, age=20):
        self['CACHE_CONTROL'] = '='.join("max-age",age)
        self['CACHE_EXPIRES'] = age
        
    def schema(self):
      self['DOMAIN'] = Schema

## Runner
def main():
    app = Eve(settings=ApiSettings(), redis=Caching())
    Bootstrap(app)
    app.register_blueprint(eve_docs, url_prefix='/docs')
  
if __name__ == '__main__':
    main()
