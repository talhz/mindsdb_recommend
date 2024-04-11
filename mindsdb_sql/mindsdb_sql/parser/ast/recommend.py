from mindsdb_sql.parser.ast.base import ASTNode
from mindsdb_sql.parser.utils import indent

class Recommend(ASTNode):
    def __init__(self,
                 value,
                 type=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = type
        self.value = value 
        print("Succesfully each the basic implementation layer of \'recommend identifier\' rule.")
        print("It is empty now.")

    
    def to_tree(self, *args, level=0, **kwargs):
        ind = indent(level)
        value_str = f'value={self.value.to_tree()}'

        type_str = ''
        if self.type is not None:
            type_str = f'type={self.type}, '

        out_str = f'{ind}recommend(' \
                  f'{type_str}' \
                  f'{value_str}' \
                  f'{ind})'
        return out_str

    def get_string(self, *args, **kwargs):
        type_str = ''
        if self.type is not None:
            type_str = f' {self.type}'
        return f'Recommend{type_str} {str(self.value)}'