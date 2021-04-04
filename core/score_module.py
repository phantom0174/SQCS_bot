from core.setup import fluctlight_client


async def active_log_update(member_id):
    fluctlight_cursor = fluctlight_client["light-cube-info"]

    # week active update
    data = fluctlight_cursor.find_one({"_id": member_id}, {"week_active": 1})
    if data["week_active"] == 0:
        fluctlight_cursor.update_one({"_id": member_id}, {"$set": {"week_active": 1}})
