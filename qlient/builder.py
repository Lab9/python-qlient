from typing import Dict, Union, List, Tuple

from qlient import utils


class SelectedField:
    """
    Used for selection response fields in a request query.
    Fields can be selected via arguments and key word arguments by using the fields() method
    """

    def __init__(self, name: str, children: List = None):
        """
        Instantiate a new SelectedField.

        :param name: holds the name of the selected field
        :param children: holds a list of optional children
        """
        self.name: str = name
        self.children: List = children

    def __str__(self):
        """
        Return the field selection as used in query language
        :return: string of field selection
        """
        result = self.name
        if self.children:
            result += " { " + " ".join([str(c) for c in self.children]) + " } "
        return result


class GraphQLBuilder:
    """ The graph query language builder is used for building the actual queries in the end. """

    def __init__(self):
        """ Instantiate a new GraphQLBuilder """
        self.object: str = ""
        self.return_field: str = ""
        self.query_field: str = ""
        self.operation_field: str = ""
        self.fragment_field: str = ""

    def fields(self, selection: Tuple[SelectedField]):
        """
        Set the fields selection of the query

        :param selection: holds a tuple of all selected fields
        :return: itself
        """
        if selection is None or len(selection) == 0:
            self.return_field = ""
            return self

        self.return_field = "{ " + " ".join([str(s) for s in selection if s]) + " }"
        return self

    def query(self, name: str, alias: str = '', params: Dict[str, Union[str, int]] = None):
        """
        Set the query type.

        :param name: holds name of the query/mutation
        :param alias: holds an optional alias
        :param params: holds optional params that can be passed byo
        :return: itself
        """
        if params is None:
            params = {}
        self.query_field = name
        inputs: List[str] = []
        if params != {}:
            for key, value in params.items():
                inputs.append(f'{key}: {value}')
            self.query_field = self.query_field + ' (' + ", ".join(inputs) + ') '
        if alias != '':
            self.query_field = f'{alias}: {self.query_field}'

        return self

    def operation(self, query_type: str = 'query', name: str = '',
                  params: Dict[str, Union[str, int]] = None,
                  queries: List[str] = None):
        """
        Set the operation type.

        :param query_type: holds the operation type (query/mutation)
        :param name: holds the name of the operation
        :param params: holds optional params
        :param queries: holds optional queries
        :return: itself
        """
        if params is None:
            params = {}

        if queries is None:
            queries = []
        self.operation_field = query_type
        inputs: List[str] = []
        if name != '':
            self.operation_field = f'{self.operation_field} {name}'
            if params != {}:
                for key, value in params.items():
                    inputs.append(f'{key}: {value}')
                self.operation_field = self.operation_field + ' (' + ", ".join(inputs) + ') '

        if len(queries) != 0:
            self.object = self.operation_field + ' { ' + " ".join(queries) + ' }'

        return self

    def generate(self) -> str:
        """
        Generate and return the overall query string
        :return: query string
        """
        if self.fragment_field != '':
            self.object = f'{self.fragment_field} {self.return_field}'
        else:
            if self.object == '' and self.operation_field == '' and self.query_field == '':
                self.object = self.return_field
            elif self.object == '' and self.operation_field == '':
                self.object = self.query_field + ' ' + self.return_field
            elif self.object == '':
                self.object = self.operation_field + ' { ' + self.query_field + ' ' + self.return_field + ' }'

        return utils.remove_duplicate_spaces(self.object)

    def __str__(self) -> str:
        """
        Invoke and return generate method.
        :return: query string
        """
        return self.generate()


def fields(*args, **kwargs) -> Tuple[SelectedField]:
    """
    Function to make a deeper selection.
    :param args: holds list for flat selections
    :param kwargs: holds dictionary for deep selection
    :return: a tuple of all selected fields.
    """
    result = []
    for arg in args:
        if arg is None:
            continue
        result.append(SelectedField(str(arg)))
    for key, value in kwargs.items():
        if value is None:
            continue
        result.append(
            SelectedField(
                key,
                children=[v if isinstance(v, SelectedField) else SelectedField(str(v)) for v in value if v]
            )
        )
    return tuple(result)
