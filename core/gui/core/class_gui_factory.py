# class GUIModelFactory:
#     def __init__(self):
#         self._registry=dict()
#     def registry(self,type_):
#         pass
# class GUIControllerFactory:
#     def __init__(self):
#         self._registry=dict()
#     def registry(self,type_):
#         pass
class GUIViewFactory:
    def __init__(self):
        self._modelRegistry = dict()
        self._controllerRegistry = dict()
        self._viewRegistry = dict()

    def register_model(self,model_type):
        self._modelRegistry[model_type.__name__]=model_type

    def unregister(self):
        pass

    def create_view(self, view_type, parent=None, content=None):
        pass
