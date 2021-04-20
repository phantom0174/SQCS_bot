from discord.ext import commands
import requests
import os
from core.classes import CogExtension

data_prefix = {
  "0": "天氣描述",
  "1": "最高溫度",
  "2": "最低溫度",
  "3": "體感描述",
  "4": "降水機率"
}

data_suffix = {
  "0": "",
  "1": "度",
  "2": "度",
  "3": "",
  "4": "%"
}

time_range_title = {
  "0": "時段一",
  "1": "時段二",
  "2": "時段三"
}


class WeatherQuery(CogExtension):
    @commands.group()
    async def wea(self, ctx):
        pass

    @wea.command()
    async def query(self, ctx, target_county: str = ''):

        weather_api_link_header: str = (
            'https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/F-C0032-001?Authorization='
        )
        response = requests.get(
            f'{weather_api_link_header}'
            f'{str(os.environ.get("PhantomTWWeatherApiKey"))}&format=json'
        )

        location_weather_data = response.json()["cwbopendata"]["dataset"]["location"]

        county_weather_info = str()

        if target_county == '':
            target_county = ctx.author.roles[1].name

        for item in location_weather_data:
            if item["locationName"].find(target_county) != -1:
                loc_json = item["weatherElement"]

                county_weather_info += item["locationName"] + '\n'

                for time_range in range(3):
                    county_weather_info += (
                        f'{time_range_title[str(time_range)]}::\n'
                    )
                    for (index, info) in enumerate(loc_json):
                        county_weather_info += (
                            f'{data_prefix[str(index)]}: '
                            f'{info["time"][time_range]["parameter"]["parameterName"]} '
                            f'{data_suffix[str(index)]}\n'
                        )

                await ctx.send(county_weather_info)
            county_weather_info = ''


def setup(bot):
    bot.add_cog(WeatherQuery(bot))
