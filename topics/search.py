from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Q, DocType, Text, Boolean, Integer, Object, Long, Nested, Date, Search
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch

from subjects.search import ResourceTagIndex

from . import models

connections.create_connection(hosts=['https://32ee85x1wy:p44kph0n9k@amadeus-elastic-6982239049.us-east-1.bonsaisearch.net'])

class ResourceIndex(DocType):
    name = Text()
    slug = Text()
    brief_description = Text()
    show_window = Boolean()
    visible = Boolean()
    order = Integer()
    topic_id = Long()
    subejct_id = Long()
    nested_tags = Nested(ResourceTagIndex)
    create_date = Date()
    last_update = Date()
    subclass = Text()

    class Index:
        name = 'resource-index'

def bulk_indexing():
    ResourceIndex.init()

    es = Elasticsearch()

    bulk(client=es, actions=(r.indexing() for r in models.Resource.objects.all().iterator()))

def resources_by_tag(tagid, subject):
    s = Search(index='resource-index')

    s = s.query('bool', must=[Q('match', subject_id=subject.id), Q('nested', path='nested_tags', query=Q('match', nested_tags__id=tagid))])

    response = []
    response.append(s.count())
    response.append(s.execute())

    return response