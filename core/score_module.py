from core.db import fluctlight_client


"""
from core.classes import JsonApi
import math
import asyncio
import threading
import time
"""


async def active_log_update(member_id):
    fluctlight_cursor = fluctlight_client["MainFluctlights"]

    # week active update
    data = fluctlight_cursor.find_one({"_id": member_id}, {"week_active": True})
    if not data["week_active"]:
        execute = {
            "$set": {
                "week_active": True
            }
        }
        fluctlight_cursor.update_one({"_id": member_id}, execute)

"""
async def hurt(member_id, delta_du):
    fluct_cursor = fluctlight_client["light-cube-info"]
    member_fluctlight = fluct_cursor.find_one({"_id": member_id})
    current_du = member_fluctlight["du"]

    if current_du <= delta_du:
        return 'dead'
    else:
        execute = {
            "$inc": {
                "du": -delta_du
            }
        }
        fluct_cursor.update_one({"_id": member_id}, execute)

        regeneration_json = JsonApi().get_json('FluctlightEvent')
        if member_id not in regeneration_json["regen_id_list"]:
            regeneration_json["id_list"].append(member_id)
            JsonApi().put_json('FluctlightEvent', regeneration_json)

            regeneration_task = threading.Thread(target=regeneration, args=(member_id,))
            regeneration_task.start()

        return 'alive'


# def respawn_cool_down(member_id):


def regeneration(member_id):
    fluct_cursor = fluctlight_client["light-cube-info"]

    while True:
        member_fluctlight = fluct_cursor.find_one({"_id": member_id})
        current_du = member_fluctlight["du"]
        mdu = member_fluctlight["mdu"]

        regenerate_du = math.floor(mdu / 100)
        if current_du + regenerate_du < mdu:
            execute = {
                "$inc": {
                    "du": regenerate_du
                }
            }
            fluct_cursor.update_one({"_id": member_id}, execute)
        else:
            execute = {
                "$set": {
                    "du": mdu
                }
            }
            fluct_cursor.update_one({"_id": member_id}, execute)
            break

        # wait 1 tic
        time.sleep(10)
"""
