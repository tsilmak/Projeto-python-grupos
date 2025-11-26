import functools
import inspect
import typing

def validate_types(func):
    """
    Decorator to enforce type hints at runtime.
    Raises TypeError if arguments or return value do not match type hints.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get type hints
        try:
            hints = typing.get_type_hints(func)
        except Exception:
            # If we can't resolve hints (e.g. forward refs not in scope), skip validation
            return func(*args, **kwargs)

        # Get argument values
        sig = inspect.signature(func)
        try:
            bound_args = sig.bind(*args, **kwargs)
        except TypeError as e:
            raise TypeError(f"Erro na chamada da função: {e}")
            
        bound_args.apply_defaults()

        for arg_name, value in bound_args.arguments.items():
            if arg_name in hints:
                expected_type = hints[arg_name]
                if arg_name == 'self':
                    continue
                
                if not check_type(value, expected_type):
                    raise TypeError(
                        f"Argumento '{arg_name}' esperava {expected_type}, "
                        f"mas recebeu {type(value).__name__} (valor: {value})."
                    )

        result = func(*args, **kwargs)

        if 'return' in hints:
            expected_return = hints['return']
            if expected_return is not None and expected_return is not type(None):
                 if not check_type(result, expected_return):
                    raise TypeError(
                        f"Retorno esperava {expected_return}, "
                        f"mas retornou {type(result).__name__}."
                    )
        
        return result
    return wrapper

def check_type(value, expected_type):
    if expected_type is typing.Any:
        return True

    # Handle Optional/Union
    origin = typing.get_origin(expected_type)
    args = typing.get_args(expected_type)

    if origin is typing.Union:
        # Optional[T] is Union[T, NoneType]
        for arg in args:
            if check_type(value, arg):
                return True
        return False

    # Handle List
    if origin is list or origin is typing.List:
        if not isinstance(value, list):
            return False
        return True

    # Handle Dict
    if origin is dict or origin is typing.Dict:
        if not isinstance(value, dict):
            return False
        return True
        
    # Handle TYPE_CHECKING imports (strings)
    if isinstance(expected_type, str):
        # Best effort: check class name
        if value is None:
             return False # Unless it was Optional, handled above
        return type(value).__name__ == expected_type

    # Handle simple types
    try:
        return isinstance(value, expected_type)
    except TypeError:
        return True # Fallback

