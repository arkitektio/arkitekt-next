from arkitekt_next.apps.types import App, Fakts, Herre, Manifest
from typing import List, Callable, Dict, Any


class QtApp(App):
    """An app that is built with the easy builder"""

    hooks: Dict[str, List[Callable]] = {
        "on_start": [],
        "on_stop": [],
        "on_error": [],
        "on_message": [],
        "on_warning": [],
        "on_info": [],
        "on_debug": [],
        "on_enter": [],
    }

    def register_hook(self, hook_name: str, hook: Callable):
        """Register a hook"""
        self.hooks[hook_name].append(hook)

    def register(self, *args, **kwargs):
        """Register a function with the app (not in the Qt event loop)

        This is useful for functions that do not need access to the Qt event loop
        and can be run in a separate thread. This is the default behavior for
        functions registered with the app.


        """
        self.services["rekuest"].register(*args, **kwargs)

    def register_in_qt_loop(self, function: Callable, **kwargs):
        """Register a function in the Qt event loop

        This is useful for functions that need to be resolved in the Qt event loop and are
        able to block the main thread (e.g. when prompting a necessary user input, or
        when displaying a blocking dialog).

        """

        from rekuest_next.qt.builders import qtinloopactifier

        return self.services["rekuest"].register(
            function, actifier=qtinloopactifier, **kwargs
        )

    def register_with_qt_future(self, function: Callable, **kwargs):
        """Register a function with a future that can be resolved in the Qt event loop

        This is useful for functions that need to be resolved in the Qt event loop, but
        might cause a blocking call if they are run in the same thread.

        Example:

        ```python

            class MyWidget(QtWidgets.QWidget):

                def __init__(self, app: QtApp):
                    super().__init__()
                    self.my_widget = QtWidgets.QWidget()
                    self.my_widget.setWindowTitle("Do you accept?")
                    self.my_widget.setWindowModality(QtCore.Qt.ApplicationModal)
                    self.my_widget.setFixedSize(200, 100)

                    self.my_widget.accept_button = QtWidgets.QPushButton("Accept")
                    self.my_widget.reject_button = QtWidgets.QPushButton("Reject")
                    self.my_widget.layout = QtWidgets.QVBoxLayout()
                    self.my_widget.layout.addWidget(self.my_widget.accept_button)
                    self.my_widget.layout.addWidget(self.my_widget.reject_button)

                    self.app.register_with_qt_future(self.my_function)



                def my_function(self, future: QtFuture, *args, **kwargs):
                    self.my_widget.setText("Do you accept?")
                    self.my_widget.show()

                    self.current_future = future


                def on_accept(self):
                    self.current_future.set_result(True)

                def on_reject(self):
                    self.current_future.set_result(False)


        """
        from rekuest_next.qt.builders import qtwithfutureactifier

        return self.services["rekuest"].register(
            function, actifier=qtwithfutureactifier, **kwargs
        )

    def register_with_qt_generator(self, function: Callable, **kwargs):
        from rekuest_next.qt.builders import qtwithgeneratoractifier

        return self.services["rekuest"].register(
            function, actifier=qtwithgeneratoractifier, **kwargs
        )

    def run(self):
        """Run the app"""
        self.services["rekuest"].run()

    async def __aenter__(self):
        await super().__aenter__()
        for service in self.services.values():
            await service.__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        for service in self.services.values():
            await service.__aexit__(exc_type, exc_value, traceback)
