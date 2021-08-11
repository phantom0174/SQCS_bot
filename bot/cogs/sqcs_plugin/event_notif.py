from discord.ext import tasks
from ...core.cog_config import CogExtension
from ...core.db.mongodb import Mongo
from gcsa.google_calendar import GoogleCalendar
from gcsa.serializers.event_serializer import EventSerializer
import os



class GoogleCalendarNotif(CogExtension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        credentials_path = os.path.abspath("./.credentials/credentials.json")
        token_path = os.path.abspath("./.credentials/token.pickle")

        self.gc = GoogleCalendar(
            calendar='hsqcc819@gmail.com',
            credentials_path=credentials_path,
            token_path=token_path
        )

        self.gc_cursor = Mongo('sqcs-bot').get_cur('GCEvents')

        self.collect_event.start()
        self.notify_event.start()
        self.update_event.start()

    @tasks.loop(hours=1)
    async def collect_event(self):
        await self.bot.wait_until_ready()

        for event in self.gc:
            event_data = self.gc_cursor.find_one({"_id": event.id})
            if event_data:
                continue

            event_obj = dict(EventSerializer.to_json(event))

            event_data = {
                "_id": event.id,
                "etag": event_obj["etag"],
                "summary": event.summary,
                "location": event.location,
                "start": event.start,
                "end": event.end,
                "msg_id": None,
                "notify_stage": None
            }
            self.gc_cursor.insert_one(event_data)

        pass

    @tasks.loop(hours=1)
    async def notify_event(self):
        await self.bot.wait_until_ready()

        pass

    @tasks.loop(hours=1)
    async def update_event(self):
        await self.bot.wait_until_ready()
        
        # first db, then discord
        pass


def setup(bot):
    bot.add_cog(GoogleCalendarNotif(bot))
