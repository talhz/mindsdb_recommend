Instructions related to our new syntax


# Installation (after git clone this repository)

```
conda create -n py39 python=3.9
conda activate py39

cd mindsdb
pip3 install -e .
pip install mindsdb[lightwood]
cd ..

cd mindsdb_sql
pip3 install -e .
cd ..
```

# After installation, to directly execute

```
cd mindsdb
python -m mindsdb
```

To exit from virtual environment and stop all
```
conda deactivate
```

# Recommend syntax:

The following query will recommend the suitable model types of the selecting data.
```
RECOMMEND MODEL project_name.predictor_name
FROM integration_name
    (SELECT column_name, ... FROM table_name)
PREDICT target_column
```
- project_name.predictor_name is the name of model we want to create
- FROM ... is the syntax to get x (sample) data to be used in model
- PREDICT ... is the syntax to define y (label) data to be used in model

To check the recommendation result, simply use the following query:
```
DRSCRIBE project_name.predictor_name;
```

The recommendation result is given in the last column, as well as other information of the best model.

# Parser
 
## Psuedo logic of connections between sql and machine learning related codes

```
from mindsdb_sql import parse_sql
from mindsdb.api.executor.command_executor import ExecuteCommands

query = parse_sql(sql, dialect="mindsdb")
ret = command_executor.execute_command(query)
```

- parse_sql: parse sql query to the mindsdb
- execute_command: execute the parsed results and return the output

## To simply test parser without executing mindsdb in local server:

Make sure that you are in the root directory.

```
python test.py
```

## To add RECOMMEND related syntax, I changed/added the following files. Search 'recommend' to see where we can add syntax about recommend (in parser.py and lexer.py)

- mindsdb_sql\mindsdb_sql\parser\dialects\mindsdb\parser.py
- mindsdb_sql\mindsdb_sql\parser\dialects\mindsdb\lexer.py
- mindsdb_sql\mindsdb_sql\parser\ast\recommend.py
- mindsdb_sql\mindsdb_sql\parser\dialects\mindsdb\recommend_model.py

recommend.py and recommend_model.py are the places to interpret semantics and to output interpreted strings. To parse sql query to the mindsdb readable contents, edit recommend.py and recommend_model.py. 

**This is the code for parsing sql query to mindsdb**

## To read parsed contents, we need to do some modifications in mindsdb repository. 

- mindsdb\mindsdb\api\mysql\mysql_proxy\executor\mysql_executor.py
- mindsdb\mindsdb\api\executor\command_executor.py

**This is the code for executing the parsed results and return the execution output**
