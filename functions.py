from datetime import datetime, timezone, timedelta
from math import *
import json

def now_time_info(mode):
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區

    if(mode == 'whole'):
        return str(dt2.strftime("%Y-%m-%d %H:%M:%S"))
    elif(mode == 'hour'):
        return int(dt2.strftime("%H"))
    elif(mode == 'date'):
        return int(dt2.isoweekday())


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

def list_check(main_list, target_list):
    for main in main_list:
        if((main in target_list) == True):
            return True

    return False