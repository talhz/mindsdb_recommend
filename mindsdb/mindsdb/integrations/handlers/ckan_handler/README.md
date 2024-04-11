## CKAN Integration handler

This handler is used to integrate with [CKAN](https://ckan.org/).
CKAN is Data Catalogue for Open Data, and it stores data in a [DataStore](http://docs.ckan.org/en/2.9/maintaining/datastore.html). 
To retrieve data from CKAN, you need to use the CKAN [API](https://ckan.org/docs/api/). 


## Creating a CKAN API client
Connecting to CKAN is done by creating a CKAN API client
In this handler, you can create a CKAN API client with [ckanapi](https://github.com/ckan/ckanapi).

*Note: Some CKAN instances will require you to provide API key. You can find it in the CKAN user panel.

```python
from ckanapi import RemoteCKAN
ckan = RemoteCKAN('https://ckan.example.com/', apikey='YOUR_API_KEY')
```

CKANAPI client supports all API methods of CKAN. 
For our handler we are using the [DataStore API](http://docs.ckan.org/en/2.9/maintaining/datastore.html#the-datastore-api)

The [`datastore_search_sql` ](http://docs.ckan.org/en/2.9/maintaining/datastore.html#ckanext.datastore.logic.action.datastore_search_sql) 
action supports raw SQL commands to be used to search for the data 

Example:
```python

ckan.action.datastore_search_sql(sql='SELECT * FROM "resource_id"')
```
