from datetime import datetime, timezone, timedelta
from math import *
import json

def now_time():
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區
    return str(dt2.strftime("%Y-%m-%d %H:%M:%S"))


def weight_main_function(a):
    return float(1/2 + 3/(2*(1+exp(-5*a + log(2)))))


def score_weight_update():
    temp_file = open('score_parameters.json', mode='r', encoding='utf8')
    para = json.load(temp_file)
    temp_file.close()

    temp_file = open('score_log.json', mode='r', encoding='utf8')
    log = json.load(temp_file)
    temp_file.close()

    sll = int(len(log['logs'])) #score logs length

    ScoreSum = float(0)
    for i in range(sll - 1):
        ScoreSum += log['logs'][i]

    AverageScore = ScoreSum/float(sll-1)
    para['average_point'] = str(int(AverageScore))

    ScoreAverageDifference = float(log['logs'][sll - 1]) - AverageScore
    MaxMinScoreDifference = float(para['maxium_point']) - float(para['minium_point'])

    para_a = ScoreAverageDifference/MaxMinScoreDifference
    final_weight = weight_main_function(para_a)

    para['point_weight'] = final_weight

def role_check(roles, t_role):
    Exist = bool(False)
    for role in roles:
        if(role.name == t_role):
            Exist = bool(True)
            break
    return Exist