from mindsdb_sql import parse_sql




def test_parser_functionality_using_existing_syntax():
    predictor_sql_query = "CREATE MODEL mindsdb.house_sales_model \
        FROM example_db \
        (SELECT * FROM house_sales) \
        PREDICT ma \
        "
    query = parse_sql(predictor_sql_query,dialect="mindsdb")
    print(query)

def test_recommend_identifier():
    test_recommend_query = "RECOMMEND identifier"
    query = parse_sql(test_recommend_query,dialect="mindsdb")
    print(query)

def test_recommend_model():
    test_recommend_sql_query = "RECOMMEND MODEL mindsdb.house_sales_model \
        FROM example_db \
        (SELECT * FROM house_sales) \
        PREDICT ma \
        "
    query = parse_sql(test_recommend_sql_query,dialect="mindsdb")
    print(query)

# To see the complete interpretation of recommend syntax
# You should see the output: RECOMMEND PREDICTOR mindsdb.house_sales_model FROM example_db (SELECT * FROM house_sales) PREDICT ma
print("Test starts")
print("=========================================================================================")
print("Test 1: test simple recommend syntax with existing identifier")
test_recommend_identifier()
print("=========================================================================================")
print("Test 2: check whether it can output the complete interpretation of recommend model syntax")
test_recommend_model()
print("=========================================================================================")