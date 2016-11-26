import pytest
from .. import di


def test_injector_get():
    with di.child_scope():
        di.injector.register('once_instance', 'Hello World!')
        assert di.injector.get('once_instance') == 'Hello World!'


def test_lazy_description_should_not_register_class():
    with di.child_scope():
        @di.desc(reg=False)
        class OneClass:
            pass

        assert di.injector.get('one_class') is None


def test_lazy_description_should_simplify_registration():
    with di.child_scope():
        @di.desc(reg=False)
        class OneClass:
            pass

        di.injector.register(instance=OneClass())

        assert isinstance(di.injector.get('one_class'), OneClass)


def test_not_lazy_description_should_simplify_registration():
    with di.child_scope():
        @di.desc(reg=True)
        class OneClass:
            pass

        assert isinstance(di.injector.get('one_class'), OneClass)


def test_fail_if_type_is_not_string():
    with di.child_scope():
        class OneClass:
            pass

        with pytest.raises(ValueError):
            di.injector.register(OneClass)


def test_kebab_string_style_is_synonym_to_underscore():
    with di.child_scope():
        @di.desc()
        class OneClass:
            pass

        assert isinstance(di.injector.get('one-class'), OneClass)


def test_later_binding():
    with di.child_scope():
        @di.desc()
        class OuterClass:
            @di.inject()
            def deps(self, test_class):
                self.test_class = test_class

        @di.desc('test_class', reg=False)
        class InnerClass:
            pass

        outer = OuterClass()
        di.injector.register(instance=outer)
        di.bind(outer, autoupdate=True)

        inner = InnerClass()
        di.injector.register(instance=inner)

        assert outer.test_class == inner
