from discord.ext import commands
import requests
import os
from ..core.cog_config import CogExtension


# This extension is for school h.w. of phantom0174.


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


class WeatherQuery(CogExtension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.weather_api_link_header: str = (
            'https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/F-C0032-001?Authorization='
        )

    @commands.group()
    async def wea(self, ctx):
        pass

    @wea.command()
    async def query(self, ctx, target_county: str = ''):
        """cmd
        查詢 城市<target_county> 的天氣狀況，如果沒有輸入即為使用者地區身分組之城市。

        .target_county: 臺灣的縣市
        """
        response = requests.get(
            f'{self.weather_api_link_header}'
            f'{str(os.environ.get("PHANTOM_TW_WEATHER_TOKEN"))}&format=json'
        )

        location_weather_data = response.json()["cwbopendata"]["dataset"]["location"]

        county_weather_info = ''

        if target_county == '':
            target_county = ctx.author.roles[1].name

        for item in location_weather_data:
            if item["locationName"].find(target_county) != -1:
                loc_json = item["weatherElement"]

                county_weather_info += item["locationName"] + '\n'

                for time_range in range(3):
                    start_time_str = loc_json[0]["time"][time_range]["startTime"]
                    end_time_str = loc_json[0]["time"][time_range]["endTime"]
                    county_weather_info += (
                        f'{start_time_str.split("T")[0]} {start_time_str.split("T")[1].split("+")[0]} ～ '
                        f'{end_time_str.split("T")[0]} {end_time_str.split("T")[1].split("+")[0]}::\n'
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
