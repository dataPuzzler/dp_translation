from .key_logic import TranslationKeyBuilder
from typing import List
from abc import abstractmethod

class TranslatableModelMixin:
    
    @classmethod
    @property
    def translation_context(self):
        return self._get_translation_context()
    
    @classmethod
    @property
    def translateable_attrs(self):
        return self._get_translateable_attrs()

    def get_logical_key_for_attr_value(self, attr_name: str):
        return TranslationKeyBuilder.construct_translation_key(
            context=self.translation_context,
            concept=type(self).__name__,
            instance_id=self.choose_instance_id(),
            attr=attr_name)
    

    def choose_instance_id(self) -> str:
        if hasattr(self, "name"):
            return self.name
        else:
            return str(self.id )

    @classmethod
    def get_logical_key_for_attr(cls, attr_name):
        assert attr_name in cls._get_translateable_attrs()
        return TranslationKeyBuilder.construct_translation_key(
            context=cls._get_translation_context(),
            concept=cls.__name__,
            instance_id=TranslationKeyBuilder.NULL_VALUE,
            attr=attr_name)
    
    @classmethod
    def get_logical_key_for_concept(cls):
        return TranslationKeyBuilder.construct_translation_key(
            context=cls._get_translation_context(),
            concept=cls.__name__,
            instance_id=TranslationKeyBuilder.NULL_VALUE,
            attr=TranslationKeyBuilder.NULL_VALUE)
    

    @classmethod
    @abstractmethod
    def _get_translation_context(cls) -> str:
        pass


    @classmethod
    @abstractmethod
    def _get_translateable_attrs(cls) -> List[str]:
        pass
