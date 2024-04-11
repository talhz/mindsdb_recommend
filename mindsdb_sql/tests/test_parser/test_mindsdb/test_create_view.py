import pytest

from mindsdb_sql import parse_sql, ParsingException
from mindsdb_sql.parser.dialects.mindsdb import *
from mindsdb_sql.parser.ast import *
from mindsdb_sql.parser.dialects.mindsdb.lexer import MindsDBLexer

class TestCreateView:
    def test_create_view_lexer(self):
        sql = "CREATE VIEW my_view FROM integration AS ( SELECT * FROM pred )"
        tokens = list(MindsDBLexer().tokenize(sql))
        assert tokens[0].value == 'CREATE'
        assert tokens[0].type == 'CREATE'

        assert tokens[1].value == 'VIEW'
        assert tokens[1].type == 'VIEW'

    def test_create_view_raises_wrong_dialect_error(self):
        sql = "CREATE VIEW my_view FROM integr AS ( SELECT * FROM pred )"
        for dialect in ['sqlite', 'mysql']:
            with pytest.raises(ParsingException):
                ast = parse_sql(sql, dialect=dialect)

    def test_create_view_full(self):
        sql = "CREATE VIEW IF NOT EXISTS my_view FROM integr AS ( SELECT * FROM pred )"
        ast = parse_sql(sql, dialect='mindsdb')
        expected_ast = CreateView(name=Identifier('my_view'),
                                  if_not_exists=True,
                                  from_table=Identifier('integr'),
                                  query_str="SELECT * FROM pred")

        assert str(ast).lower() == sql.lower()
        assert str(ast) == str(expected_ast)
        assert ast.to_tree() == expected_ast.to_tree()

    def test_create_view_nofrom(self):
        sql = "CREATE VIEW my_view ( SELECT * FROM pred )"
        ast = parse_sql(sql, dialect='mindsdb')
        expected_ast = CreateView(name=Identifier('my_view'),
                                  query_str="SELECT * FROM pred")

        assert str(ast) == str(expected_ast)
        assert ast.to_tree() == expected_ast.to_tree()

    # def test_create_dataset_full(self):
    #     sql = "CREATE DATASET my_view FROM integr AS ( SELECT * FROM pred )"
    #     ast = parse_sql(sql, dialect='mindsdb')
    #     expected_ast = CreateView(name='my_view',
    #                               from_table=Identifier('integr'),
    #                               query_str="SELECT * FROM pred")
    #
    #     assert str(ast) == str(expected_ast)
    #     assert ast.to_tree() == expected_ast.to_tree()

    # def test_create_dataset_nofrom(self):
    #     sql = "CREATE DATASET my_view ( SELECT * FROM pred )"
    #     ast = parse_sql(sql, dialect='mindsdb')
    #     expected_ast = CreateView(name='my_view',
    #                               query_str="SELECT * FROM pred")

        # assert str(ast) == str(expected_ast)
        # assert ast.to_tree() == expected_ast.to_tree()
