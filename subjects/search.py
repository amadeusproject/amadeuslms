from elasticsearch_dsl.connections import connections
from elasticsearch.helpers import bulk
from elasticsearch_dsl import DocType, InnerDoc, Text, Keyword, Search
from elasticsearch import Elasticsearch
from elastic.models import ElasticSearchSettings
from . import models

config = ElasticSearchSettings.objects.get()

if config:
    conn = connections.create_connection(hosts=[config.host], timeout = 60)
else:
    conn = ''

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
