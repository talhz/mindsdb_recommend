import pandas as pd

from mindsdb_sql.parser import ast

from mindsdb.integrations.libs.api_handler import APIHandler, APITable
from mindsdb.integrations.utilities.sql_utils import extract_comparison_conditions, project_dataframe

from mindsdb.integrations.libs.response import (
    HandlerStatusResponse as StatusResponse,
    HandlerResponse as Response,
    RESPONSE_TYPE
)
from mindsdb.utilities.security import is_private_url
from mindsdb.utilities.config import Config

from .urlcrawl_helpers import get_df_from_query_str, get_all_websites


class CrawlerTable(APITable):

    def select(self, query: ast.Select) -> pd.DataFrame:

        conditions = extract_comparison_conditions(query.where)
        urls = []
        for op, arg1, arg2 in conditions:

            if op == 'or':
                raise NotImplementedError(f'OR is not supported')

            if arg1 == 'url':
                url = arg2

                if op == '=':
                    urls = [str(url)]
                elif op == 'in':
                    if type(url) == str:
                        urls = [str(url)]
                    else:
                        urls = url
                else:
                    raise NotImplementedError(
                        f'url can be url = "someurl", you can also crawl multiple sites, as follows:'
                        f' url IN ("url1", "url2", ..)'
                    )

            else:
                pass

        if len(urls) == 0:
            raise NotImplementedError(
                f'You must specify what url you want to crawl, for example: SELECT * FROM crawl WHERE url IN ("someurl", ..)')

        if query.limit is None:
            raise NotImplementedError(f'You must specify a LIMIT which defines the number of pages to crawl')
        limit = query.limit.value

        if limit < 0:
            limit = 0

        config = Config()
        is_cloud = config.get("cloud", False)
        if is_cloud:
            urls = [
                url
                for url in urls
                if not is_private_url(url)
            ]

        result = get_all_websites(urls, limit, html=False)
        if len(result) > limit:
            result = result[:limit]
        # filter targets
        result = project_dataframe(result, query.targets, self.get_columns())
        return result

    def get_columns(self):
        return [
            'url',
            'text_content',
            'error'
        ]


class WebHandler(APIHandler):
    """A class for handling crawling content from websites.

    Attributes:
        
    """

    def __init__(self, name=None, **kwargs):
        super().__init__(name)

        self.api = None
        self.is_connected = True
        crawler = CrawlerTable(self)
        self._register_table('crawler', crawler)

    def check_connection(self) -> StatusResponse:

        response = StatusResponse(False)
        response.success = True

        return response

    def native_query(self, query_string: str = None):

        df = get_df_from_query_str(query_string)

        return Response(
            RESPONSE_TYPE.TABLE,
            data_frame=df
        )
