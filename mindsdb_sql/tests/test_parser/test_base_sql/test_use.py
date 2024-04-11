import pytest

from mindsdb_sql import parse_sql
from mindsdb_sql.parser.ast import *


@pytest.mark.parametrize('dialect', ['sqlite', 'mysql', 'mindsdb'])
class TestUse:
    def test_use(self, dialect):
        sql = "USE my_integration"
        ast = parse_sql(sql, dialect=dialect)
        expected_ast = Use(value=Identifier('my_integration'))

        assert str(ast).lower() == sql.lower()
        assert str(ast) == str(expected_ast)
        assert ast.to_tree() == expected_ast.to_tree()

