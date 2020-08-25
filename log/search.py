from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import (
    Q,
    DocType,
    Text,
    Date,
    Integer,
    Long,
    Object,
    Search,
    MultiSearch,
)
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from django.utils import formats, timezone

from elastic.models import ElasticSearchSettings

from . import models

config = ElasticSearchSettings.objects.get()

if config:
    conn = connections.create_connection(hosts=[config.host], timeout=60)
else:
    conn = ""


class LogIndex(DocType):
    component = Text()
    action = Text()
    resource = Text()
    user = Text()
    user_id = Long()
    datetime = Date()
    context = Object()

    class Index:
        name = "log-index"


def bulk_indexing():
    LogIndex.init()

    es = Elasticsearch()

    logs = models.Log.objects.filter(
        datetime__date__gte=timezone.now() - timedelta(hours=7 * 24 + 3),
        datetime__date__lt=timezone.now() - timedelta(hours=3),
    ).all()

    bulk(client=es, actions=(b.indexing() for b in logs.iterator()))


def count_logs(resources, userid=0):
    s = Search().extra(size=0)

    conds = []

    for res in resources:
        conds.append(Q("match", **{"context__" + res._my_subclass + "_id": res.id}))

    if userid != 0:
        s = s.query(
            "bool",
            must=[
                Q(
                    "range",
                    datetime={"time_zone": "-03:00", "gte": "now-7d", "lte": "now"},
                ),
                Q("match", component="resources"),
                Q(
                    "bool",
                    should=[Q("match", action="access"), Q("match", action="view")],
                ),
                Q("bool", should=conds),
                Q("match", user_id=userid),
            ],
        )
    else:
        s = s.query(
            "bool",
            must=[
                Q(
                    "range",
                    datetime={"time_zone": "-03:00", "gte": "now-7d", "lte": "now"},
                ),
                Q("match", component="resources"),
                Q(
                    "bool",
                    should=[Q("match", action="access"), Q("match", action="view")],
                ),
                Q("bool", should=conds),
            ],
        )

    return s[0:10000]


def count_logs_period(resources, data_ini, data_end, userid=0):
    s = Search().extra(size=0)

    conds = []

    for res in resources:
        conds.append(Q("match", **{"context__" + res._my_subclass + "_id": res.id}))

    if userid != 0:
        s = s.query(
            "bool",
            must=[
                Q(
                    "range",
                    datetime={"time_zone": "-03:00", "gte": data_ini, "lte": data_end},
                ),
                Q("match", component="resources"),
                Q(
                    "bool",
                    should=[Q("match", action="access"), Q("match", action="view")],
                ),
                Q("bool", should=conds),
                Q("match", user_id=userid),
            ],
        )

    else:
        s = s.query(
            "bool",
            must=[
                Q(
                    "range",
                    datetime={"time_zone": "-03:00", "gte": data_ini, "lte": data_end},
                ),
                Q("match", component="resources"),
                Q(
                    "bool",
                    should=[Q("match", action="access"), Q("match", action="view")],
                ),
                Q("bool", should=conds),
            ],
        )

    return s[0:10000]


def resource_accessess(resource, userid=0):
    s = Search().extra(size=0)

    if userid != 0:
        s = s.query(
            "bool",
            must=[
                Q(
                    "range",
                    datetime={"time_zone": "-03:00", "gte": "now-7d", "lte": "now"},
                ),
                Q("match", component="resources"),
                Q(
                    "bool",
                    should=[Q("match", action="access"), Q("match", action="view")],
                ),
                Q(
                    "match",
                    **{"context__" + resource._my_subclass + "_id": resource.id}
                ),
                Q("match", user_id=userid),
            ],
        )
    else:
        s = s.query(
            "bool",
            must=[
                Q(
                    "range",
                    datetime={"time_zone": "-03:00", "gte": "now-7d", "lte": "now"},
                ),
                Q("match", component="resources"),
                Q(
                    "bool",
                    should=[Q("match", action="access"), Q("match", action="view")],
                ),
                Q(
                    "match",
                    **{"context__" + resource._my_subclass + "_id": resource.id}
                ),
            ],
        )

    return s[0:10000]


def resource_accessess_period(resource, dataIni, dataEnd, userid=0):
    s = Search().extra(size=0)
    if userid != 0:
        s = s.query(
            "bool",
            must=[
                Q(
                    "range",
                    datetime={"time_zone": "-03:00", "gte": dataIni, "lte": dataEnd},
                ),
                Q("match", component="resources"),
                Q(
                    "bool",
                    should=[Q("match", action="access"), Q("match", action="view")],
                ),
                Q(
                    "match",
                    **{"context__" + resource._my_subclass + "_id": resource.id}
                ),
                Q("match", user_id=userid),
            ],
        )
    else:
        s = s.query(
            "bool",
            must=[
                Q(
                    "range",
                    datetime={"time_zone": "-03:00", "gte": dataIni, "lte": dataEnd},
                ),
                Q("match", component="resources"),
                Q(
                    "bool",
                    should=[Q("match", action="access"), Q("match", action="view")],
                ),
                Q(
                    "match",
                    **{"context__" + resource._my_subclass + "_id": resource.id}
                ),
            ],
        )

    return s[0:10000]


def user_last_interaction(userid):
    s = Search().extra(size=1)

    s = s.query("match", user_id=userid).sort("-datetime")

    return s


def count_access_subject(subject, userid=0):
    s = Search().extra(size=0)

    s = s.query(
        "bool",
        must=[
            Q("range", datetime={"time_zone": "-03:00", "gte": "now-7d", "lte": "now"}),
            Q(
                "bool",
                should=[
                    Q(
                        "bool",
                        must=[
                            Q("match", component="subject"),
                            Q("match", resource="subject"),
                        ],
                    ),
                    Q("match", component="resources"),
                ],
            ),
            Q("match", **{"context__subject_id": subject}),
            Q("match", user_id=userid),
            Q("bool", should=[Q("match", action="access"), Q("match", action="view")]),
        ],
    )

    return s[0:10000]


def count_diff_days(subject, userid):
    s = Search().extra(size=0)

    s = s.query(
        "bool",
        must=[
            Q("range", datetime={"time_zone": "-03:00", "gte": "now-7d", "lte": "now"}),
            Q("match", resource="subject"),
            Q("match", **{"context__subject_id": subject}),
            Q("match", user_id=userid),
            Q("bool", should=[Q("match", action="access"), Q("match", action="view")]),
        ],
    )

    s.aggs.bucket("dt", "date_histogram", field="datetime", interval="day")

    return s[0:10000]


def count_access_resources(subject, userid):
    s = Search().extra(size=0)

    s = s.query(
        "bool",
        must=[
            Q("range", datetime={"time_zone": "-03:00", "gte": "now-7d", "lte": "now"}),
            Q("match", component="resources"),
            Q("match", **{"context__subject_id": subject}),
            Q("match", user_id=userid),
        ],
    )

    return s[0:10000]


def count_access_subject_period(subject, userid, data_ini, data_end):
    s = Search().extra(size=0)

    s = s.query(
        "bool",
        must=[
            Q(
                "range",
                datetime={"time_zone": "-03:00", "gte": data_ini, "lte": data_end},
            ),
            Q("match", **{"context__subject_id": subject}),
            Q("match", user_id=userid),
        ],
    )

    return s[0:10000]


def count_daily_access(subject, students, day):
    s = Search()

    s = s.query(
        "bool",
        must=[
            Q("range", datetime={"time_zone": "-03:00", "gte": day, "lte": day}),
            Q(
                "bool",
                should=[
                    Q(
                        "bool",
                        must=[
                            Q("match", component="subject"),
                            Q("match", resource="subject"),
                        ],
                    ),
                    Q("match", component="resources"),
                ],
            ),
            Q("match", **{"context__subject_id": subject}),
            Q("terms", user_id=students),
            Q("bool", should=[Q("match", action="access"), Q("match", action="view")]),
        ],
    )

    return s[0:10000]


def multi_search(searchs):
    ms = MultiSearch(using=conn, index="log-index")

    for search in searchs:
        ms = ms.add(search)

    response = ms.execute()

    return response


def count_daily_general_logs_access(day):
    s = Search()

    s = s.query(
        "bool",
        must=[Q("range", datetime={"time_zone": "-03:00", "gte": day, "lte": day}),],
    )

    return s


def count_daily_general_logs_access1(day):
    s = Search()

    s = s.query(
        "bool",
        must=[
            Q(
                "range",
                datetime={
                    "time_zone": "-03:00",
                    "gte": day,
                    "lte": day + timedelta(hours=15),
                },
            ),
        ],
    )

    return s


def count_daily_general_logs_access2(day):
    s = Search()

    s = s.query(
        "bool",
        must=[
            Q(
                "range",
                datetime={
                    "time_zone": "-03:00",
                    "gte": day + timedelta(hours=15),
                    "lte": day + timedelta(hours=24),
                },
            ),
        ],
    )

    return s


def user_last_interaction_in_period(userid, data_ini, data_end):
    s = Search().extra(size=1)

    s = s.query(
        "bool",
        must=[
            Q(
                "range",
                datetime={"time_zone": "-03:00", "gte": data_ini, "lte": data_end},
            ),
            Q("match", user_id=userid),
        ],
    )

    return s[0:10000]


def count_general_access_subject_period(subject, data_ini, data_end):
    s = Search().extra(size=0)

    s = s.query(
        "bool",
        must=[
            Q(
                "range",
                datetime={"time_zone": "-03:00", "gte": data_ini, "lte": data_end},
            ),
            Q(
                "bool",
                should=[
                    Q(
                        "bool",
                        must=[
                            Q("match", component="subject"),
                            Q("match", resource="subject"),
                        ],
                    ),
                    Q("match", component="resources"),
                ],
            ),
            Q("match", **{"context__subject_id": subject}),
            Q("bool", should=[Q("match", action="access"), Q("match", action="view")]),
        ],
    )

    return s[0:10000]


def count_general_logs_period(resources, data_ini, data_end):
    s = Search().extra(size=0)

    conds = []

    for res in resources:
        conds.append(Q("match", **{"context__resource_ptr_id": res.id}))

    s = s.query(
        "bool",
        must=[
            Q(
                "range",
                datetime={"time_zone": "-03:00", "gte": data_ini, "lte": data_end},
            ),
            Q("match", component="resources"),
            Q("bool", should=[Q("match", action="access"), Q("match", action="view")],),
            Q("bool", should=conds),
        ],
    )

    return s[0:10000]


def count_general_daily_access(students, day):
    s = Search()

    s = s.query(
        "bool",
        must=[
            Q("range", datetime={"time_zone": "-03:00", "gte": day, "lte": day}),
            Q("terms", user_id=students),
        ],
    )

    return s[0:10000]


def count_general_resource_logs_period(subjects, data_ini, data_end):
    s = Search().extra(size=0)

    conds = []

    for sub in subjects:
        conds.append(Q("match", **{"context__subject_id": sub.id}))

    s = s.query(
        "bool",
        must=[
            Q(
                "range",
                datetime={"time_zone": "-03:00", "gte": data_ini, "lte": data_end},
            ),
            Q(
                "bool",
                should=conds
            ),
            Q("match", component="resources"),
            Q(
                "bool",
                should=[Q("match", action="access"),Q("match", action="create"),Q("match", action="view_statistics"), Q("match", action="view"),Q("match", action="update"),Q("match", action="delete"),Q("match", action="finish"),Q("match", action="watch"),],
            ),
        ],
    )

    return s[0:10000]


def count_general_access_period(user, data_ini, data_end):
    s = Search().extra(size=0)

    s = s.query(
        "bool",
        must=[
            Q(
                "range",
                datetime={"time_zone": "-03:00", "gte": data_ini, "lte": data_end},
            ),
            Q("match", user_id=user),
        ],
    )

    return s[0:10000]

def count_mural_comments(user, data_ini, data_end):
    s = Search().extra(size=0)

    s = s.query(
        "bool",
        must=[
            Q(
                "range",
                datetime={"time_zone": "-03:00", "gte": data_ini, "lte": data_end},
            ),
            Q("match", user_id=user),
            Q("match", action="create_comment"),
        ],
    )

    return s[0:10000]

def count_chat_messages(user, data_ini, data_end):
    s = Search().extra(size=0)

    s = s.query(
        "bool",
        must=[
            Q(
                "range",
                datetime={"time_zone": "-03:00", "gte": data_ini, "lte": data_end},
            ),
            Q("match", user_id=user),
            Q(
                "bool",
                should=[
                    Q("match", action="send"),
                    Q("match", action="create_post"),
                ],
            ),
            Q("match", component="chat"),
        ],
    )

    return s[0:10000]

def count_resources(user, data_ini, data_end):
    s = Search().extra(size=0)

    s = s.query(
        "bool",
        must=[
            Q(
                "range",
                datetime={"time_zone": "-03:00", "gte": data_ini, "lte": data_end},
            ),
            Q("match", user_id=user),
            Q("match", action="create"),
            Q("match", component="resources"),
        ],
    )

    return s[0:10000]


