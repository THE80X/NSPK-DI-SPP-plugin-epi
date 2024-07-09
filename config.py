import datetime

from s3p_sdk.plugin.config import (
    PluginConfig,
    CoreConfig,
    TaskConfig,
    trigger,
    MiddlewareConfig,
    modules,
    payload
)
from s3p_sdk.plugin.config.type import SOURCE
from s3p_sdk.module import (
    WEBDRIVER,
)

config = PluginConfig(
    plugin=CoreConfig(
        reference='uniq source name',
        type=SOURCE,
        files=['epi.py', ],
        is_localstorage=False
    ),
    task=TaskConfig(
        trigger=trigger.TriggerConfig(
            type=trigger.SCHEDULE,
            interval=datetime.timedelta(days=7),
        )
    ),
    middleware=MiddlewareConfig(
        modules=[
            modules.TimezoneSafeControlConfig(order=1, is_critical=True),
            modules.CutJunkCharactersFromDocumentTextConfig(order=2, is_critical=True,
                                                            p_fields=['text', 'abstract']),
        ],
        bus=None,
    ),
    payload=payload.PayloadConfig(
        file='epi.py',
        classname='EPIParser',
        entry=payload.entry.EntryConfig(
            method='content',
            params=[
                payload.entry.ModuleParamConfig(key='driver', module_name=WEBDRIVER, bus=True),
                payload.entry.ConstParamConfig(key='max_count_documents', value=50),
                payload.entry.ConstParamConfig(key='urls', value=['https://www.epicompany.eu/news/', 'https://www.epicompany.eu/news-archive-list/']),
                payload.entry.ConstParamConfig(key='timeout', value=20)
            ]
        )
    )
)

__all__ = ['config']
