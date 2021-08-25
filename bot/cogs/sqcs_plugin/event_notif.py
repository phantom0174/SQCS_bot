from discord.ext import tasks
from ...core.cog_config import CogExtension
from ...core.db.mongodb import Mongo
from gcsa.google_calendar import GoogleCalendar
from gcsa.serializers.event_serializer import EventSerializer
import os
import pendulum as pend


class GoogleCalendarNotif(CogExtension):
    pass  # TOKEN expired error
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     credentials_path = os.path.abspath("./.credentials/credentials.json")
    #     token_path = os.path.abspath("./.credentials/token.pickle")

    #     self.gc = GoogleCalendar(
    #         calendar='hsqcc819@gmail.com',
    #         credentials_path=credentials_path,
    #         token_path=token_path
    #     )

    #     self.gc_cursor = Mongo('sqcs-bot').get_cur('GCEvents')

    #     self.collect_event.start()
    #     self.notify_event.start()
    #     self.update_event.start()

    @tasks.loop(hours=1)
    async def collect_event(self):
        await self.bot.wait_until_ready()

        for event in self.gc:
            event_data = self.gc_cursor.find_one({"_id": event.id})
            if event_data:
                continue

            event_obj = dict(EventSerializer.to_json(event))

            event_start_time = pend.parse(str(event.start), tz='Asia/Taipei').to_datetime_string()
            event_end_time = pend.parse(str(event.end), tz='Asia/Taipei').to_datetime_string()

            event_data = {
                "_id": event.id,
                "etag": event_obj["etag"],
                "summary": event.summary,
                "location": event.location,
                "start": event_start_time,
                "end": event_end_time,
                "msg_id": None,
                "notify_stage": None
            }
            self.gc_cursor.insert_one(event_data)

    @tasks.loop(hours=1)
    async def notify_event(self):
        await self.bot.wait_until_ready()

        notify_channel = self.bot.get_channel(None)

        event_data = self.gc_cursor.find_one({})

        def get_notify_msg():
            pass

        for event in event_data:
            now_time = pend.now('Asia/Taipei')
            event_start_time = pend.parse(event["start"])

            if (event_start_time - now_time).in_days() == 5 and event["msg_id"] is None:
                notify_msg = get_notify_msg()
                notify_dc_msg = await notify_channel.send(notify_msg)

                execute = {
                    "$set": {
                        "msg_id": notify_dc_msg.id,
                        "notify_stage": 5
                    }
                }
                self.gc_cursor.update_one({"_id": event["_id"]}, execute)
            elif (event_start_time - now_time).in_days() == 3 and event["notify_stage"] == 5:
                notify_msg = get_notify_msg()
                old_notify_dc_msg = notify_channel.fetch_message(event["msg_id"])
                notify_dc_msg = await old_notify_dc_msg.edit(notify_msg)

                execute = {
                    "$set": {
                        "notify_stage": 3
                    }
                }
            elif (event_start_time - now_time).in_days() == 1 and event["notify_stage"] == 3:
                notify_msg = get_notify_msg()
                old_notify_dc_msg = notify_channel.fetch_message(event["msg_id"])
                notify_dc_msg = await old_notify_dc_msg.edit(notify_msg)

                execute = {
                    "$set": {
                        "notify_stage": 1
                    }
                }

    @tasks.loop(hours=1)
    async def update_event(self):
        await self.bot.wait_until_ready()

        notify_channel = self.bot.get_channel(None)

        def get_new_notify_msg():
            pass

        for event in self.gc:
            event_data = self.gc_cursor.find_one({"_id": event.id})

            if not event_data:
                continue

            event_obj = dict(EventSerializer.to_json(event))

            # etag has been modified => event has been modified
            if event_obj["etag"] != event_data["etag"]:
                # renew all info of event
                event_start_time = pend.parse(str(event.start), tz='Asia/Taipei')
                event_end_time = pend.parse(str(event.end), tz='Asia/Taipei')

                execute = {
                    "$set": {
                        "etag": event_obj["etag"],
                        "summary": event.summary,
                        "location": event.location,
                        "start": event_start_time,
                        "end": event_end_time
                    }
                }
                self.gc_cursor.update_one({"_id": event.id}, execute)

                # repost notify
                old_notify_dc_msg = notify_channel.fetch_message(event_data["msg_id"])
                await old_notify_dc_msg.delete()

                notify_msg = get_new_notify_msg()
                notify_dc_msg = await notify_channel.send(notify_msg)

                execute = {
                    "$set": {
                        "msg_id": notify_dc_msg.id
                    }
                }
                self.gc_cursor.update_one({"_id": event.id}, execute)


def setup(bot):
    bot.add_cog(GoogleCalendarNotif(bot))
