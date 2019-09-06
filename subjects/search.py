from elasticsearch_dsl.connections import connections
from elasticsearch.helpers import bulk
from elasticsearch_dsl import DocType, InnerDoc, Text, Keyword, Search
from elasticsearch import Elasticsearch

from . import models

connections.create_connection(hosts=['https://32ee85x1wy:p44kph0n9k@amadeus-elastic-6982239049.us-east-1.bonsaisearch.net'])

class TagIndex(DocType):
    name = Text()

    class Index:
        name = 'tag-index'

class ResourceTagIndex(InnerDoc):
    id = Keyword()
    name = Text()

def bulk_indexing():
    TagIndex.init()

    es = Elasticsearch()

    bulk(client=es, actions=(t.indexing() for t in models.Tag.objects.all().iterator()))

def tags_all():
    s = Search(index='tag-index')

    total = s.count()

    response = s[0:total].execute()

    return response