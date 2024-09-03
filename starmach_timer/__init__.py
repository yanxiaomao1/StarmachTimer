'''Plugin'''

import json
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy import inspect

from RHUI import UIField, UIFieldType
import requests
import Database

def initialize(rhapi):

    # rhapi.fields.register_pilot_attribute( UIField("uuid", "飞手ID", UIFieldType.TEXT) )

    rhapi.ui.register_panel("format", "数据上传", "format")
    rhapi.fields.register_option( UIField("event_uuid", "赛事秘钥", UIFieldType.TEXT), "format" )
    rhapi.ui.register_quickbutton("format", "upload", "上传成绩", runUploadBtn, {"rhapi": rhapi})

def runUploadBtn(args):
    args['rhapi'].ui.message_notify(args['rhapi'].__('开始上传数据.'))

    keys = Database.GlobalSettings.query.filter_by(option_name='event_uuid').first().option_value

    SavedRaceLap = Database.SavedRaceLap.query.all()
    SavedRaceMeta = Database.SavedRaceMeta.query.all()
    RaceClass = Database.RaceClass.query.all()
    Heat = Database.Heat.query.all()
    HeatNode = Database.HeatNode.query.all()
    Pilot = Database.Pilot.query.all()
    RaceFormat = Database.RaceFormat.query.all()

    datas = {
        'key': keys,
        'Pilot': Pilot,
        'Heat': Heat,
        'HeatNode': HeatNode,
        'RaceClass': RaceClass,
        'SavedRaceMeta': SavedRaceMeta,
        'SavedRaceLap': SavedRaceLap,
        'RaceFormat': RaceFormat,
    }

    res = requests.post('https://timer.fpvone.cn/app/race_data/submit', json=json.loads(json.dumps(datas, cls=AlchemyEncoder)))
    args['rhapi'].ui.message_notify(args['rhapi'].__(res.json()['message']))

class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        custom_vars = []
        if isinstance(obj.__class__, DeclarativeMeta):
            mapped_instance = inspect(obj)
            fields = {}
            for field in dir(obj):
                if field in [*mapped_instance.attrs.keys(), *custom_vars]:
                    data = obj.__getattribute__(field)
                    if field != 'query' \
                        and field != 'query_class':
                        try:
                            json.dumps(data)
                            fields[field] = data
                        except TypeError:
                            fields[field] = None
            return fields

        return json.JSONEncoder.default(self, obj)
