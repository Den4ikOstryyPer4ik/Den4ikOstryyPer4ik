# requires: 

import os

from telethon.tl.types import DocumentAttributeAudio
from youtube_dl import YoutubeDL
from youtube_dl.utils import (
    DownloadError,
    ContentTooShortError,
    ExtractorError,
    GeoRestrictedError,
    MaxDownloadsReached,
    PostProcessingError,
    UnavailableVideoError,
    XAttrMetadataError,
)

from .. import loader, utils


@loader.tds
class YTDlMod(loader.Module):
    """Скачать музычку или видосичек"""

    strings = {
        "name": "Скачать музычку или видосичек",
        "preparing": "<b>[Жди]</b> Подготовка...",
        "downloading": "<b>[Еще жди]</b> Загрузка...",
        "working": "<b>[ЖДИИИ]</b> Working...",
        "exporting": "<b>[ЕЩЕ ЖДИИИ]</b> Exporting...",
        "reply": "<b>[АФИГЕЛ ПИСАТЬ КОМАНДУ БЕЗ ССЫЛКИ]</b> Нет ссылки, проверь ещё пару раз!",
        "noargs": "<b>[ТЫ ТУПОЙ]</b> Нет аргументов!",
        "content_too_short": "<b>[YouTube-Dl]</b> Downloading content too short!",
        "geoban": "<b>[YouTube-Dl]</b> Видео недоступно для вашего географического местоположения из-за географических ограничений, установленных сайтом! Крч, ютуб ахуел!",
        "maxdlserr": '<b>[YouTube-Dl]</b> The download limit is as follows: " oh ahah"',
        "pperr": "<b>[YouTube-Dl]</b> Error in post-processing!",
        "noformat": "<b>[Считай, что ты тупой]</b> Media is not available in the requested format",
        "xameerr": "<b>[YouTube-Dl]</b> {0.code}: {0.msg}\n{0.reason}",
        "exporterr": "<b>[YouTube-Dl]</b> Error when exporting video",
        "err": "<b>[YouTube-Dl]</b> {}",
        "err2": "<b>[YouTube-Dl]</b> {}: {}",
    }

    async def ytdlvcmd(self, m):
        """.ytdlv <ссыл04ка / reply_на_ссыло04ку> - Видосик скачай с ютубика"""
        await ytdler(self, m, "video")

    async def ytdlacmd(self, m):
        """.ytdla <ссыл04ка / reply_на_ссыло04ку> - скачать музычку/аудио с ютубика"""
        await ytdler(self, m, "audio")


async def ytdler(self, m, type):
    reply = await m.get_reply_message()
    args = utils.get_args_raw(m)
    url = args or reply.raw_text
    if not url:
        return await utils.answer(m, self.strings("noargs", m))
    m = await utils.answer(m, self.strings("preparing", m))
    if type == "audio":
        opts = {
            "format": "bestaudio",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "writethumbnail": True,
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ],
            "outtmpl": "%(id)s.mp3",
            "quiet": True,
            "logtostderr": False,
        }
        video = False
        song = True
    elif type == "video":
        opts = {
            "format": "best",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [
                {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
            ],
            "outtmpl": "%(id)s.mp4",
            "logtostderr": False,
            "quiet": True,
        }
        song = False
        video = True
    try:
        await utils.answer(m, self.strings("downloading", m))
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url)
    except DownloadError as DE:
        return await utils.answer(m, self.strings("err", m).format(str(DE)))
    except ContentTooShortError:
        return await utils.answer(m, self.strings("content_too_short", m))
    except GeoRestrictedError:
        return await utils.answer(m, self.strings("geoban", m))
    except MaxDownloadsReached:
        return await utils.answer(m, self.strings("maxdlserr", m))
    except PostProcessingError:
        return await utils.answer(m, self.strings("pperr", m))
    except UnavailableVideoError:
        return await utils.answer(m, self.strings("noformat", m))
    except XAttrMetadataError as XAME:
        return await utils.answer(m, self.strings("xameerr", m).format(XAME))
    except ExtractorError:
        return await utils.answer(m, self.strings("exporterr", m))
    except Exception as e:
        return await utils.answer(
            m, self.strings("err2", m).format(str(type(e)), str(e))
        )
    if song:
        u = ytdl_data["uploader"] if "uploader" in ytdl_data else "Northing"
        await utils.answer(
            m,
            open(f"{ytdl_data['id']}.mp3", "rb"),
            supports_streaming=True,
            reply_to=reply.id if reply else None,
            attributes=[
                DocumentAttributeAudio(
                    duration=int(rip_data["duration"]),
                    title=str(ytdl_data["title"]),
                    performer=u,
                )
            ],
        )
        os.remove(f"{ytdl_data['id']}.mp3")
    elif video:
        await utils.answer(
            m,
            open(f"{ytdl_data['id']}.mp4", "rb"),
            reply_to=reply.id if reply else None,
            supports_streaming=True,
            caption=ytdl_data["title"],
        )
        os.remove(f"{ytdl_data['id']}.mp4")
