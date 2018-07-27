# encoding: utf-8

from plone.memoize.instance import memoize
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class TestingVocabulary(object):
    implements(IVocabularyFactory)

    @memoize
    def __call__(self, context):
        """Just return a value defined in the REQUEST."""
        res = []
        for value in context.REQUEST.get('vocab_values', []):
            res.append(SimpleTerm(value, value, value))
        return SimpleVocabulary(res)


TestingVocabularyFactory = TestingVocabulary()
