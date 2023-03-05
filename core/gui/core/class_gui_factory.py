import weakref
from core.application.core.base import is_singleton_object
from core.application.class_application_context import ApplicationContext
from .class_base import ZViewManager, ZViewContentContainer, ZView


class GUIZViewFactoryRegistryError(Exception):
    pass


class GUIZViewFactoryCreationError(Exception):
    pass


class GUIZViewFactory:
    def __init__(self):
        self._registry = dict()
        self._appCtx = ApplicationContext()
        self._cache = weakref.WeakValueDictionary()

    def has_registered(self, name):
        return name in self._registry

    def register(self, name, view_cls: ZView, content_container_cls: type(ZViewContentContainer) = None, manager_cls: type(ZViewManager) = None,
                 override=False):
        assert view_cls is not None, 'ZView is required'
        if not override and name in self._registry:
            raise GUIZViewFactoryRegistryError('name {} already exist'.format(name))
        self._registry[name] = (manager_cls, view_cls, content_container_cls)

    def unregister(self, name):
        if name in self._registry:
            self._registry.pop(name)

    def create_view(self, view_name, **kwargs) -> [ZView, None]:
        if view_name not in self._registry:
            raise GUIZViewFactoryCreationError('the view with name {} not registered.'.format(view_name))
        _m_cls, _v_cls, _cc_cls = self._registry.get(view_name)
        if _v_cls is None:
            return None
        _cached = self._cache.get(view_name)
        if _cached:
            # fixme: if content or viewParent is difference, how handle this case?
            return _cached
        if _cc_cls is not None:
            _content_container = _cc_cls()
        else:
            _content_container = None

        _view_parent = kwargs.get('parent')
        # _view_content = kwargs.get('content')
        _view = _v_cls(_view_parent)
        if is_singleton_object(_v_cls):
            self._cache[view_name] = _view
        if _m_cls is None:
            return _view
        _mgr_parent = kwargs.get('manager_parent')
        _view_id = kwargs.get('view_id')
        _view_title = kwargs.get('view_title')
        _manager = _m_cls(view=_view, content_container=_content_container,
                          parent=_mgr_parent,
                          view_name=view_name,
                          view_title=_view_title,
                          view_id=_view_id)
        if _manager.aliveWithProject and self._appCtx.project is not None and _content_container is not None:
            if not self._appCtx.project.is_content_container_registered(_content_container.get_id()):
                if _manager.parent() is not None:
                    _cc_parent = _manager.parent().content_container
                else:
                    _cc_parent = None
                self._appCtx.project.register_with_project(_content_container, _cc_parent)
        # _manager.set_content(_view_content)

        return _view
