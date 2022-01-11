from typing import List, Callable
from functools import wraps

from ninja import Router


class SavageRouter(Router):
    def __init__(self, *args, **kwrags):
        self._before_request_queue: Callable = []
        self._after_request_queue: Callable = []
        super().__init__(*args, **kwrags)

    def api_operation(
        self,
        methods: List[str],
        path: str,
        *,
        before_request: List[str] = [],
        after_request: List[str] = [],
        **kwargs
    ) -> Callable:
        """
            Rewrite parent function to call add_api operation in child
        """
        def decorator(view_func: Callable):
            self.add_api_operation(
                path,
                methods,
                view_func,
                before_request=before_request,
                after_request=after_request,
                **kwargs,
            )
            return view_func

        return decorator

    def add_api_operation(
        self,
        path: str,
        methods: List[str],
        view_func: Callable,
        *args,
        **kwargs
    ) -> Callable:
        def decorator(view_func: Callable) -> Callable:
            # ^ this function don't do decorator stuff, just a wrapper
            @wraps(view_func)
            def wrap(request, *args, **kwargs):
                # before request
                if self._before_request_queue:
                    # ^ if list is not empty
                    for before_request_func in self._before_request_queue:
                        before_request_func(request, *args, **kwargs)
                response = view_func(request, *args, **kwargs)
                if self._after_request_queue:
                    # ^ if list is not empty
                    for after_request_func in self._after_request_queue:
                        after_request_func(request, *args, **kwargs)
                # after request
                return response
            return wrap
        view_func = decorator(view_func)
        return super().add_api_operation(path, methods, view_func, *args, **kwargs)

    def before_reqeust(self):
        def decorator(func: Callable) -> Callable:
            self._before_request_queue.append(func)
            return func
        return decorator

    def after_request(self):
        def decorator(func: Callable) -> Callable:
            self._after_request_queue.append(func)
            return func
        return decorator
