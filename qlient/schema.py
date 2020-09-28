from typing import Dict, List, Tuple, Union, Optional

from qlient.builder import SelectedField
from qlient.cache import Cache
from qlient.loaders import request_schema
from qlient.settings import Settings
from qlient.transport import Transporter


class OperationArgument:
    """
    Represents an operation argument.
    """

    def __init__(self, name: str, arg_type_name: str, is_required=False):
        """
        Instantiate a new OperationArgument

        :param name: holds the argument name
        :param arg_type_name: holds the argument type
        :param is_required: true if the argument must not be null
        """
        self.key = name
        self._value = arg_type_name
        self.required = is_required

    @property
    def value(self) -> str:
        """
        :return: a concatenated string of the type and an exclamation mark if it is required.o
        """
        return_value = self._value
        if self.required:
            return_value += "!"
        return return_value


class Operation:
    """
    Represents an operation that can be executed on the server.
    """

    def __init__(self, field: "SchemaTypeField", settings: Settings):
        """
        Instantiate a new Operation.

        :param field: holds the schema type field the operation is attached to.
        :param settings: holds the clients settings
        """
        from qlient import helpers
        self.settings = settings
        self.name = field.name
        self.description = field.description
        self.arguments = helpers.adapt_arguments(field.args)
        self.return_type = field.type
        self._return_fields: Union[Tuple[SelectedField], None] = None

    def get_return_fields(self, all_types: "Dict[str, SchemaType]") -> Tuple[SelectedField]:
        """
        Recursively look up a certain amount of return fields depending on the current recursion depth.
        The depth can be set via the settings.

        client = Client("...", settings=Settings(max_recursion_depth=3))

        :param all_types: holds all available schema types
        :return: a tuple of selection fields
        """
        if self._return_fields is None:
            from qlient import helpers
            self._return_fields = helpers.adapt_return_fields(
                self.return_type,
                all_types,
                self.settings.max_recursion_depth
            )
        return self._return_fields


class Directive:
    """
    Represents a typed version of an schema directive
    """

    def __init__(self, raw_directive: Dict):
        """
        Instantiate a new Directive
        :param raw_directive: holds the raw directive data
        """
        self.name: str = raw_directive.get("name")
        self.description: str = raw_directive.get("description")
        self.locations: List[str] = raw_directive.get("locations", [])
        self.args: Dict[str, Argument] = Schema.parse_arguments(raw_directive.get("args", []))


class Argument:
    """
    Represents a typed version of an query argument.
    """

    def __init__(self, raw_arg: Dict):
        """
        Instantiate a new Argument
        :param raw_arg: holds the raw argument data
        """
        self.name = raw_arg.get("name")
        self.description = raw_arg.get("description")
        self.type = TypeDefer(raw_arg.get("type")) if raw_arg.get("type") is not None else None
        self.default_value = raw_arg.get("defaultValue")


class TypeDefer:
    """
    Represents a typed version of an type defer.
    A TypeDefer can also have itself as a child
    """

    def __init__(self, raw_defer: Dict):
        """
        Instantiate a new TypeDefer
        :param raw_defer: holds the raw defer data
        """
        self.kind = raw_defer.get("kind")
        self.name = raw_defer.get("name")
        self.of_type: TypeDefer = TypeDefer(raw_defer.get("ofType")) if raw_defer.get("ofType") is not None else None

    def is_non_null(self) -> bool:
        """
        :return: true if this type defer is of type non null else false
        """
        return self.kind and self.kind == "NON_NULL"

    def is_list(self) -> bool:
        """
        :return: true if this type defer is of type list else false
        """
        return self.kind and self.kind == "LIST"

    def is_scalar(self) -> bool:
        """
        :return: true if this type defer is of type scalar else false
        """
        return self.kind and self.kind == "SCALAR"

    def is_object(self) -> bool:
        """
        :return: true if this type defer is of type object else false
        """
        return self.kind and self.kind == "OBJECT"

    def is_interface(self) -> bool:
        """
        :return: true if this type defer is of type interface else false
        """
        return self.kind and self.kind == "INTERFACE"

    def is_input_object(self) -> bool:
        """
        :return: true if this type defer is of type input object else false
        """
        return self.kind and self.kind == "INPUT_OBJECT"


class SchemaTypeField:
    """
    Represents a typed version of an schema type field
    """

    def __init__(self, raw_field: Dict):
        """
        Instantiate a new SchemaTypeField
        :param raw_field: holds the raw input data
        """
        self.name = raw_field.get("name")
        self.description = raw_field.get("description")
        self.args: Dict[str, Argument] = Schema.parse_arguments(raw_field.get("args", []))
        self.type: TypeDefer = TypeDefer(raw_field.get("type")) if raw_field.get("type") is not None else None
        self.is_deprecated: bool = raw_field.get("isDeprecated")
        self.deprecation_reason: str = raw_field.get("deprecationReason")


class SchemaTypeInputField:
    """
    Represents a typed version of an schema type input field
    """

    def __init__(self, raw_input: Dict):
        """
        Instantiate a new SchemaTypeInputField
        :param raw_input: holds the raw input data
        """
        self.name = raw_input.get("name")
        self.description = raw_input.get("description")
        self.type: TypeDefer = TypeDefer(raw_input.get("type")) if raw_input.get("type") is not None else None
        self.default_value = raw_input.get("defaultValue")


class SchemaTypeInterface:
    """
    Represents a typed version of a schema type interface.
    Signature yet unknown.
    """

    def __init__(self, raw_interface: Dict):
        """
        Instantiate a new SchemaTypeInterface
        :param raw_interface: holds the raw interface data
        """
        pass


class SchemaTypeEnum:
    """
    Represents a typed version of an schema type enum value
    """

    def __init__(self, raw_enum: Dict):
        """
        Instantiate a new SchemaTypeEnum
        :param raw_enum: holds the raw enum data
        """
        self.name: str = raw_enum.get("name")
        self.description: str = raw_enum.get("description")
        self.is_deprecated: bool = raw_enum.get("isDeprecated")
        self.deprecation_reason: str = raw_enum.get("deprecationReason")


class SchemaType:
    """
    Represents a typed version of an schema type
    """

    def __init__(self, raw_type: Dict):
        """
        Instantiate a new SchemaType
        :param raw_type: holds the raw enum data
        """

        self.kind = raw_type.get("kind")
        self.name = raw_type.get("name")
        self.description = raw_type.get("description")
        self.fields: List[SchemaTypeField] = [SchemaTypeField(f) for f in raw_type.get("fields") or [] if f]
        self.input_fields = [SchemaTypeInputField(i) for i in raw_type.get("inputFields") or [] if i]
        self.interfaces = [SchemaTypeInterface(i) for i in raw_type.get("interfaces") or [] if i]
        self.enum_values = [SchemaTypeEnum(e) for e in raw_type.get("enumValues") or [] if e]
        self.possible_types = raw_type.get("possibleTypes")


SCHEMA_KEY = "SCHEMA"


class Schema:
    """
    A Schema object contains all graphql types and holds the possible queries and mutations.
    The request to the endpoint always is synchronous since we exceptionally use the requests session object
    instead of the transporter itself.
    """

    def __init__(self, endpoint: str, transporter: Transporter, settings: Settings, cache: Optional[Cache]):
        """
        Create a new Schema instance.

        Firstly the schema will be loaded synchronously from the endpoint and stored as raw json for further processing.
        Then the request types will be parsed. Those are "Query", "Mutation" and "Subscription".
        After that the schema types and directives are parsed.

        :param endpoint: holds the endpoint url as a string
        :param transporter: holds the transporter instance
        :param settings: holds the settings
        :param cache: holds an optional caching mechanism
        """
        self.endpoint = endpoint
        self.transport = transporter
        self.settings = settings
        self.cache = cache

        if self.cache is not None:
            schema_introspection = self.cache.retrieve(self.endpoint, SCHEMA_KEY)
            if schema_introspection is None:
                schema_introspection = self.introspect_schema(endpoint, transporter)
                self.cache.store(self.endpoint, SCHEMA_KEY, schema_introspection)
        else:
            schema_introspection = self.introspect_schema(endpoint, transporter)

        # graphql schema properties
        self.raw_schema = schema_introspection.get(self.settings.default_response_key, {}).get("__schema", {})
        self.query_type: str = self.parse_query_type(self.raw_schema)
        self.mutation_type: str = self.parse_mutation_type(self.raw_schema)
        self.subscription_type: str = self.parse_subscription_type(self.raw_schema)

        self.types: Dict[str, SchemaType] = self.parse_types(self.raw_schema.get("types", []))
        self.directives: Dict[str, Directive] = self.parse_directives(self.raw_schema.get("directives", []))

        # custom schema properties
        self.queries: Tuple[Operation] = self.parse_operations(self.query_type)
        self.mutations: Tuple[Operation] = self.parse_operations(self.mutation_type)
        self.subscriptions: Tuple[Operation] = self.parse_operations(self.subscription_type)

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"<Schema(endpoint={self.endpoint})>"

    @classmethod
    def introspect_schema(cls, endpoint: str, transport: Transporter) -> Dict:
        """
        Make a synchronous request to the endpoint and return the response as json.

        :param endpoint: holds the endpoint url as a string
        :param transport: holds the transporter instance
        :return: the raw schema in json
        """
        return request_schema(endpoint, transport.session)

    @staticmethod
    def parse_query_type(raw_schema: Dict) -> Union[str, None]:
        """
        Parse the query type from the root schema.
        This can either return a string or None.
        The latter when the endpoint does not support queries.

        :param raw_schema: holds the raw schema
        :return: either the name or None
        """
        return Schema.parse_operation_type(raw_schema, "queryType")

    @staticmethod
    def parse_mutation_type(raw_schema: Dict) -> Union[str, None]:
        """
        Parse the mutation type from the root schema.
        This can either return a string or None.
        The latter when the endpoint does not support mutations.

        :param raw_schema: holds the raw schema
        :return: either the name or None
        """
        return Schema.parse_operation_type(raw_schema, "mutationType")

    @staticmethod
    def parse_subscription_type(raw_schema: Dict) -> Union[str, None]:
        """
        Parse the subscription type from the root schema.
        This can either return a string or None.
        The latter when the endpoint does not support subscriptions.

        :param raw_schema: holds the raw schema
        :return: either the name or None
        """
        return Schema.parse_operation_type(raw_schema, "subscriptionType")

    @staticmethod
    def parse_operation_type(raw_schema: Dict, op_type: str) -> Union[str, None]:
        """
        Parse an operation type from the root schema.
        This can either return a string or None.
        The latter when the endpoint does not support the passed by operation.

        :param raw_schema: holds the raw schema in json
        :param op_type: holds the operation type
        :return: either the name or None
        """
        query_type = raw_schema.get(op_type, {})
        if not query_type:
            return None
        return query_type.get("name")

    def parse_operations(self, operation_type: str) -> Tuple[Operation]:
        """
        Parse all operations for a given operation type.

        :param operation_type: holds the operation type name.
        :return: a tuple of all available operations for this operation type
        """
        if operation_type is None:
            return tuple()
        query_type: SchemaType = self.types.get(operation_type)
        if query_type is None:
            return tuple()
        return tuple([Operation(f, self.settings) for f in query_type.fields])

    @staticmethod
    def parse_types(schema_types: List[Dict]) -> Dict[str, SchemaType]:
        """
        Parse all types from the raw schema response.

        :param schema_types: holds a list of all available types.
        :return: a dictionary with the types name as a key and the type itself as a value
        """
        result = {}
        for schema_type in schema_types:
            new_type = SchemaType(schema_type)
            result[new_type.name] = new_type
        return result

    @staticmethod
    def parse_arguments(args: List[Dict]) -> 'Dict[str, Argument]':
        """
        Parse a list of arguments into a dictionary where the key is the name of the argument and
        the argument itself is the value.

        :param args: holds the list of arguments to parse
        :return: a dictionary with mapped arguments
        """
        if not args:
            return {}
        result = {}
        for a in args:
            if not a:
                continue
            arg = Argument(a)
            result[arg.name] = arg
        return result

    @staticmethod
    def parse_directives(schema_directives: List[Dict]) -> Dict[str, Directive]:
        """
        Parse a list of directives into a dictionary where the key is the name of the directive and
        the value is the directive itself.o

        :param schema_directives: holds the schema directives
        :return: a dictionary with mapped directives
        """
        result = {}
        for schema_directive in schema_directives:
            new_directive = Directive(schema_directive)
            result[new_directive.name] = new_directive
        return result
