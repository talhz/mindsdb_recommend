
# MongoDBHandler 

### Components

**MongoQuery**

The goal of this class is to store mongo query in structured format without using cumbersome dict.

It contents name of collection and pipeline. 
Pipeline contents list of methods and arguments to apply to collection. 

Also has methods to convert query to mongo query string: 
```
"db_test.fish.find({a:1}, {b:2}).sort({c:3})"
```

**MongodbParser**

Converts mongo query from string format to instance of MongoQuery. 
Parsing is performed by using python ast parser with custom handlers for nodes.

Parser can handle ISODate and ObjectId.

**MongodbRender**

Converts AST-query to MongoQuery

Only "Select" is supported at the moment. 
Select is converted to mongo "aggregate" method.

This method can provide different capabilities to query from mongo:
- simple select query
- grouping
- sorting
- projection

**MongoDBHandler**

native_query method can take string and MongoQuery on input. 
If input is string (for example in case of creating predictor)
it will be parsed to MongoQuery using MongodbParser.

MongoDBHandler has functionality to flatten record up to chosen level.

For example
```
{ 
  'a': 1,
  'b': {
    'c': 2,
    'e': {
       'd': 3,
       'f': {
            'i': 4
        }
    }
  }  
}
```
with flatten_level=2 will be converted to:
```
{ 
  'a': 1,
  'b.c': 2,
  'b.e.d': 3,
  'b.e.f': {'i': 4}
}
```
It can be useful to get more row from collection records 
and use them in joins and predictions.
To enable this function you need to pass flatten_level to connection parameters

Limitations of MongoDBHandler
- get_columns method gets columns from first record of collection.
Because collections is not usual table and don't store information about columns  

### Testing

To run tests:

```
env PYTHONPATH=./ pytest tests/unit/test_mongodb_handler.py
```
