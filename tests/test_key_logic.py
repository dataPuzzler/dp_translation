import pytest
from dp_sqlalchemy_wrapper.base_db import BaseDB
from sqlalchemy.orm import clear_mappers

@pytest.fixture(scope="module")
def TranslationKeyBuilder():
    from dp_translation.key_logic import TranslationKeyBuilder
    return TranslationKeyBuilder


@pytest.fixture(scope="module")
def TranslationKeyRetriever():
    from dp_translation.key_logic import TranslationKeyRetriever
    return TranslationKeyRetriever


@pytest.fixture(scope="module")
def valid_construction_kwargs():
    return {
        "context": "domain_db_",
        "concept": "_exercise",
        "instance_id": "benchpress",
        "attr": "exercise_name"
    }


@pytest.fixture(scope="module")
def valid_translation_key():
    return "domain_db__%__exercise_%_benchpress_%_exercise_name"

@pytest.fixture(scope="module")
def TestConfig():
    from dp_sqlalchemy_wrapper.base_config import BaseDBConfig
    class TestDBConfig(BaseDBConfig):
        db_url = "sqlite+pysqlite:///:memory:"
    
    return TestDBConfig

@pytest.fixture(scope="function")
def emptyTestDB(TestConfig) -> BaseDB:
    import sqlalchemy as sa
    from dp_sqlalchemy_wrapper.declarative_util import makeBase
    from dp_translation.model_mixin import TranslatableModelMixin
    Base = makeBase()
        

    class TestDB(BaseDB):
        def _populate_all_tables(self, session):
            pass
            
    
    testDB = TestDB(TestConfig, Base)
    yield testDB
    clear_mappers()

def test_translation_key_regex(TranslationKeyBuilder, valid_translation_key):
    regex = TranslationKeyBuilder.REGEX
    valid_key_instance = valid_translation_key
    m = regex.match(valid_key_instance)
    assert m.group(0) == valid_translation_key


def test_translation_key_construction(TranslationKeyBuilder, valid_construction_kwargs, valid_translation_key):
    assert TranslationKeyBuilder.construct_translation_key(**valid_construction_kwargs) == valid_translation_key


def test_translation_key_deconstruction(TranslationKeyBuilder, valid_construction_kwargs, valid_translation_key):
    assert TranslationKeyBuilder.destruct_translation_key(valid_translation_key) == valid_construction_kwargs

def test_translation_key_retriever_finds_correct_keys_for_model_without_name_field(TranslationKeyRetriever, emptyTestDB):
    import sqlalchemy as sa
    from dp_translation import TranslatableModelMixin

    class SampleTable(emptyTestDB.Base, TranslatableModelMixin):
        some_attr = sa.Column(sa.String, unique=True)
    
        @classmethod
        def get_translation_context(cls):
            return "test_db"
        
        @classmethod
        def get_translateable_attrs(cls) -> str:
            return ["some_attr"]

    def fill_sample_table(session):
        s1 = SampleTable(some_attr="fst_key")
        s2 = SampleTable(some_attr="snd_key")
        session.add_all([s1, s2])
        session.commit()

    emptyTestDB.create_all_tables()
    emptyTestDB.run_in_session_context(fill_sample_table)
    key_result = TranslationKeyRetriever.get_all_translation_keys_of_translateable_model(emptyTestDB.Session, SampleTable)
    assert key_result == [
        'test_db_%_SampleTable_%_null_%_null', 
        'test_db_%_SampleTable_%_null_%_some_attr', 
        'test_db_%_SampleTable_%_1_%_some_attr', 
        'test_db_%_SampleTable_%_2_%_some_attr'
    ]

def test_translation_key_retriever_finds_correct_keys_for_model_with_unique_name_field(TranslationKeyRetriever, emptyTestDB):
    import sqlalchemy as sa
    from dp_translation import TranslatableModelMixin

    class SampleTable(emptyTestDB.Base, TranslatableModelMixin):
        name = sa.Column(sa.String, unique=True)
    
        @classmethod
        def get_translation_context(cls):
            return "test_db"
        
        @classmethod
        def get_translateable_attrs(cls) -> str:
            return ["name"]

    def fill_sample_table(session):
        s1 = SampleTable(name="fst_key")
        s2 = SampleTable(name="snd_key")
        session.add_all([s1, s2])
        session.commit()

    emptyTestDB.create_all_tables()
    emptyTestDB.run_in_session_context(fill_sample_table)
    key_result = TranslationKeyRetriever.get_all_translation_keys_of_translateable_model(emptyTestDB.Session, SampleTable)
    assert key_result == [
        'test_db_%_SampleTable_%_null_%_null', 
        'test_db_%_SampleTable_%_null_%_name', 
        'test_db_%_SampleTable_%_fst_key_%_name', 
        'test_db_%_SampleTable_%_snd_key_%_name'
    ]
