from signal import signal, SIGINT
from os import path as ospath, remove as osremove, execl as osexecl
from subprocess import run as srun, check_output
from psutil import disk_usage, cpu_percent, swap_memory, cpu_count, virtual_memory, net_io_counters, boot_time
from time import time
from sys import executable
from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler

from bot import bot, dispatcher, updater, botStartTime, IGNORE_PENDING_REQUESTS, LOGGER, Interval, INCOMPLETE_TASK_NOTIFIER, DB_URI, app, main_loop
from .helper.ext_utils.fs_utils import start_cleanup, clean_all, exit_clean_up
from .helper.ext_utils.telegraph_helper import telegraph
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.ext_utils.db_handler import DbManger
from .helper.telegram_helper.bot_commands import BotCommands
from .helper.telegram_helper.message_utils import sendMessage, sendMarkup, editMessage, sendLogFile
from .helper.telegram_helper.filters import CustomFilters
from .helper.telegram_helper.button_build import ButtonMaker

from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, shell, eval, delete, count, leech_settings, search, rss , speedtest


def stats(update, context):
    if ospath.exists('.git'):
        last_commit = check_output(["git log -1 --date=short --pretty=format:'%cd <b>From</b> %cr'"], shell=True).decode()
    else:
        last_commit = 'No UPSTREAM_REPO'
    currentTime = get_readable_time(time() - botStartTime)
    osUptime = get_readable_time(time() - boot_time())
    total, used, free, disk= disk_usage('/')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(net_io_counters().bytes_sent)
    recv = get_readable_file_size(net_io_counters().bytes_recv)
    cpuUsage = cpu_percent(interval=0.5)
    p_core = cpu_count(logical=False)
    t_core = cpu_count(logical=True)
    swap = swap_memory()
    swap_p = swap.percent
    swap_t = get_readable_file_size(swap.total)
    memory = virtual_memory()
    mem_p = memory.percent
    mem_t = get_readable_file_size(memory.total)
    mem_a = get_readable_file_size(memory.available)
    mem_u = get_readable_file_size(memory.used)
    stats = f'<b>Commit Date:</b> {last_commit}\n\n'\
            f'<b>Bot Uptime:</b> {currentTime}\n'\
            f'<b>OS Uptime:</b> {osUptime}\n\n'\
            f'<b>Total Disk Space:</b> {total}\n'\
            f'<b>Used:</b> {used} | <b>Free:</b> {free}\n\n'\
            f'<b>Upload:</b> {sent}\n'\
            f'<b>Download:</b> {recv}\n\n'\
            f'<b>CPU:</b> {cpuUsage}%\n'\
            f'<b>RAM:</b> {mem_p}%\n'\
            f'<b>DISK:</b> {disk}%\n\n'\
            f'<b>Physical Cores:</b> {p_core}\n'\
            f'<b>Total Cores:</b> {t_core}\n\n'\
            f'<b>SWAP:</b> {swap_t} | <b>Used:</b> {swap_p}%\n'\
            f'<b>Memory Total:</b> {mem_t}\n'\
            f'<b>Memory Free:</b> {mem_a}\n'\
            f'<b>Memory Used:</b> {mem_u}\n'
    sendMessage(stats, context.bot, update.message)


def start(update, context):
    buttons = ButtonMaker()
    buttons.buildbutton("Repo", "https://www.github.com/iamtayky/mirror-bot")
    buttons.buildbutton("Report Group", "https://t.me/picassoneverdie")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        start_string = f'''
Bot c?? th??? chuy???n m???i link qua GoogleDrive!
Type /{BotCommands.HelpCommand} ????? xem t???t c??? c??c l???nh c???a Bot
'''
        sendMarkup(start_string, context.bot, update.message, reply_markup)
    else:
        sendMarkup('Kh??ng x??c th???c , Vui l??ng t??? deploy cho ri??ng m??nh', context.bot, update.message, reply_markup)

def restart(update, context):
    restart_message = sendMessage("Kh???i ?????ng l???i...", context.bot, update.message)
    if Interval:
        Interval[0].cancel()
    clean_all()
    srun(["pkill", "-f", "gunicorn|aria2c|qbittorrent-nox"])
    srun(["python3", "update.py"])
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    osexecl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update.message)
    end_time = int(round(time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update.message)


help_string_telegraph = f'''<br>
<b>/{BotCommands.HelpCommand}</b>: ????? nh???n tin nh???n n??y
<br><br>
<b>/{BotCommands.MirrorFshare}</b> [download_url][magnet_link]: T???i link Fshare qua Google Drive
<br><br>
<b>/{BotCommands.MirrorCommand}</b> [download_url][magnet_link]: Chuy???n qua GoogleDrive. Send <b>/{BotCommands.MirrorCommand}</b> for more help
<br><br>
<b>/{BotCommands.ZipMirrorCommand}</b> [download_url][magnet_link]: Chuy???n File/Folder d?????i d???ng n??n .zip qua GoogleDrive
<br><br>
<b>/{BotCommands.UnzipMirrorCommand}</b> [download_url][magnet_link]: Chuy???n File/Folder ???? ???????c gi???i n??n qua GoogleDrive
<br><br>
<b>/{BotCommands.QbMirrorCommand}</b> [magnet_link][torrent_file][torrent_file_url]: Get File Torrent b???ng qBittorrent , Use <b>/{BotCommands.QbMirrorCommand} s</b> Ch???n File tr?????c khi b???t ?????u
<br><br>
<b>/{BotCommands.QbZipMirrorCommand}</b> [magnet_link][torrent_file][torrent_file_url]: Get File Torrent b???ng qBittorrent v?? Upload l??n d?????i d???ng n??n .zip
<br><br>
<b>/{BotCommands.QbUnzipMirrorCommand}</b> [magnet_link][torrent_file][torrent_file_url]: Get File Torrent b???ng qBittorrent v?? Upload l??n sau khi ???????c gi???i n??n
<br><br>
<b>/{BotCommands.LeechCommand}</b> [download_url][magnet_link]: Chuy???n file l??n Telegram , Use <b>/{BotCommands.LeechCommand} s</b> ????? ch???n file tr?????c khi chuy???n
<br><br>
<b>/{BotCommands.ZipLeechCommand}</b> [download_url][magnet_link]: Chuy???n file l??n Telegram v?? Upload file/folder d?????i d???ng n??n
<br><br>
<b>/{BotCommands.UnzipLeechCommand}</b> [download_url][magnet_link][torent_file]: Chuy???n file l??n Telegram v?? Upload File/Folder sau khi gi???i n??n
<br><br>
<b>/{BotCommands.QbLeechCommand}</b> [magnet_link][torrent_file][torrent_file_url]: Chuy???n File torrent l??n telegram b???ng qBittorrent, Use <b>/{BotCommands.QbLeechCommand} s</b> ????? ch???n tr?????c khi chuy???n
<br><br>
<b>/{BotCommands.QbZipLeechCommand}</b> [magnet_link][torrent_file][torrent_file_url]: Chuy???n File torrent l??n telegram b???ng qBittorrent v?? Upload File/Folder ???? ???????c n??n
<br><br>
<b>/{BotCommands.QbUnzipLeechCommand}</b> [magnet_link][torrent_file][torrent_file_url]: Chuy???n File torrent l??n telegram b???ng qBittorrent v?? Upload File/Folder ???? ???????c gi???i n??n
<br><br>
<b>/{BotCommands.CloneCommand}</b> [drive_url][gdtot_url]: Copy File/Folder c???a Google Drive
<br><br>
<b>/{BotCommands.CountCommand}</b> [drive_url][gdtot_url]: ?????m File/Folder c???a Google Drive
<br><br>
<b>/{BotCommands.DeleteCommand}</b> [drive_url]: X??a File/Folder tr??n Google Drive (Only Owner & Sudo)
<br><br>
<b>/{BotCommands.WatchCommand}</b> [yt-dlp supported link]: Mirror yt-dlp supported link. Send <b>/{BotCommands.WatchCommand}</b> for more help
<br><br>
<b>/{BotCommands.ZipWatchCommand}</b> [yt-dlp supported link]: Mirror yt-dlp supported link as zip
<br><br>
<b>/{BotCommands.LeechWatchCommand}</b> [yt-dlp supported link]: Leech yt-dlp supported link
<br><br>
<b>/{BotCommands.LeechZipWatchCommand}</b> [yt-dlp supported link]: Leech yt-dlp supported link as zip
<br><br>
<b>/{BotCommands.LeechSetCommand}</b>: Leech settings
<br><br>
<b>/{BotCommands.SetThumbCommand}</b>: Reply photo to set it as Thumbnail
<br><br>
<b>/{BotCommands.RssListCommand}</b>: List all subscribed rss feed info
<br><br>
<b>/{BotCommands.RssGetCommand}</b>: [Title] [Number](last N links): Force fetch last N links
<br><br>
<b>/{BotCommands.RssSubCommand}</b>: [Title] [Rss Link] f: [filter]: Subscribe new rss feed
<br><br>
<b>/{BotCommands.RssUnSubCommand}</b>: [Title]: Unubscribe rss feed by title
<br><br>
<b>/{BotCommands.RssSettingsCommand}</b>: Rss Settings
<br><br>
<b>/{BotCommands.CancelMirror}</b>: Tr??? l???i tin nh???n c???n d???ng v?? file ???? s??? ???????c d???ng
<br><br>
<b>/{BotCommands.CancelAllCommand}</b>: D???ng t???t c??? c??c c??ng vi???c
<br><br>
<b>/{BotCommands.ListCommand}</b> [query]: T??m ki???m trong GoogleDrive
<br><br>
<b>/{BotCommands.SearchCommand}</b> [query]: Search for torrents with API
<br>sites: <code>rarbg, 1337x, yts, etzv, tgx, torlock, piratebay, nyaasi, ettv</code><br><br>
<b>/{BotCommands.StatusCommand}</b>: Xem t??nh tr???ng c???a bot
<br><br>
<b>/{BotCommands.StatsCommand}</b>: Xem dung l?????ng c???a server
'''

help = telegraph.create_page(
        title='Mirror-Leech-Bot Help',
        content=help_string_telegraph,
    )["path"]

help_string = f'''
/{BotCommands.PingCommand}: Ki???m tra ping c???a Server

/{BotCommands.AuthorizeCommand}: X??c th???c nh??m Chat ho???c ng?????i d??ng (Can only be invoked by Owner & Sudo of the bot)

/{BotCommands.UnAuthorizeCommand}: H???y x??c th???c nh??m Chat ho???c ng?????i d??ng (Can only be invoked by Owner & Sudo of the bot)

/{BotCommands.AuthorizedUsersCommand}: Xem user ???? ???????c x??c th???c (Only Owner & Sudo)

/{BotCommands.AddSudoCommand}: Th??m sudo user (Only Owner)

/{BotCommands.RmSudoCommand}: X??a sudo user (Only Owner)

/{BotCommands.RestartCommand}: Kh???i ?????ng l???i v?? C???p nh???t Bot

/{BotCommands.LogCommand}: L???y log c???a bot

/{BotCommands.ShellCommand}: Ch???y commands trong Shell (Only Owner)

/{BotCommands.ExecHelpCommand}: Get help for Executor module (Only Owner)
'''

def bot_help(update, context):
    button = ButtonMaker()
    button.buildbutton("Other Commands", f"https://telegra.ph/{help}")
    reply_markup = InlineKeyboardMarkup(button.build_menu(1))
    sendMarkup(help_string, context.bot, update.message, reply_markup)

botcmds = [

        (f'{BotCommands.MirrorCommand}', 'Mirror'),
        (f'{BotCommands.ZipMirrorCommand}','Mirror v?? Upload nh?? .zip'),
        (f'{BotCommands.UnzipMirrorCommand}','Mirror v?? gi???i n??n Files'),
        (f'{BotCommands.QbMirrorCommand}','Mirror torrent b???ng qBittorrent'),
        (f'{BotCommands.QbZipMirrorCommand}','Mirror torrent v?? upload .zip b???ng qb'),
        (f'{BotCommands.QbUnzipMirrorCommand}','Mirror torrent v?? gi???i n??n Files b???ng qb'),
        (f'{BotCommands.WatchCommand}','Mirror yt-dlp supported link'),
        (f'{BotCommands.ZipWatchCommand}','Mirror yt-dlp supported link as zip'),
        (f'{BotCommands.CloneCommand}','Copy file/folder ?????n Drive'),
        (f'{BotCommands.LeechCommand}','Upload l??n Telegram'),
        (f'{BotCommands.ZipLeechCommand}','Upload l??n Telegram n??n .zip'),
        (f'{BotCommands.UnzipLeechCommand}','Upload l??n Telegram ???? ???????c gi???i n??n'),
        (f'{BotCommands.QbLeechCommand}','Upload Telegram b???ng qBittorrent'),
        (f'{BotCommands.QbZipLeechCommand}','Upload File Torrent l??n Telegram b???ng qb'),
        (f'{BotCommands.QbUnzipLeechCommand}','Upload File Torrent l??n Telegram v?? gi???i n??n b???ng qb'),
        (f'{BotCommands.LeechWatchCommand}','Leech yt-dlp supported link'),
        (f'{BotCommands.LeechZipWatchCommand}','Leech yt-dlp supported link as zip'),
        (f'{BotCommands.CountCommand}','?????m file/folder c???a link Drive'),
        (f'{BotCommands.DeleteCommand}','X??a file/folder t??? Drive'),
        (f'{BotCommands.CancelMirror}','H???y task'),
        (f'{BotCommands.CancelAllCommand}','H???y t???t c??? c??c task'),
        (f'{BotCommands.ListCommand}','T??m ki???m trong Drive'),
        (f'{BotCommands.LeechSetCommand}','Leech settings'),
        (f'{BotCommands.SetThumbCommand}','Set thumbnail'),
        (f'{BotCommands.StatusCommand}','T??nh tr???ng Bot'),
        (f'{BotCommands.StatsCommand}','Dung l?????ng server'),
        (f'{BotCommands.PingCommand}','Ki???m tra Ping'),
        (f'{BotCommands.RestartCommand}','Kh???i ?????ng l???i bot'),
        (f'{BotCommands.LogCommand}','L???y log c???a Bot'),
        (f'{BotCommands.HelpCommand}','Xem t???t c??? c??c l???nh')
    ]

def main():
    # bot.set_my_commands(botcmds)
    start_cleanup()
    if INCOMPLETE_TASK_NOTIFIER and DB_URI is not None:
        notifier_dict = DbManger().get_incomplete_tasks()
        if notifier_dict:
            for cid, data in notifier_dict.items():
                if ospath.isfile(".restartmsg"):
                    with open(".restartmsg") as f:
                        chat_id, msg_id = map(int, f)
                    msg = 'Restarted successfully!'
                else:
                    msg = 'Bot Restarted!'
                for tag, links in data.items():
                     msg += f"\n\n{tag}: "
                     for index, link in enumerate(links, start=1):
                         msg += f" <a href='{link}'>{index}</a> |"
                         if len(msg.encode()) > 4000:
                             if 'Restarted successfully!' in msg and cid == chat_id:
                                 bot.editMessageText(msg, chat_id, msg_id, parse_mode='HTMl', disable_web_page_preview=True)
                                 osremove(".restartmsg")
                             else:
                                 try:
                                     bot.sendMessage(cid, msg, 'HTML')
                                 except Exception as e:
                                     LOGGER.error(e)
                             msg = ''
                if 'Restarted successfully!' in msg and cid == chat_id:
                     bot.editMessageText(msg, chat_id, msg_id, parse_mode='HTMl', disable_web_page_preview=True)
                     osremove(".restartmsg")
                else:
                    try:
                        bot.sendMessage(cid, msg, 'HTML')
                    except Exception as e:
                        LOGGER.error(e)

    if ospath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Kh???i ?????ng th??nh c??ng!", chat_id, msg_id)
        osremove(".restartmsg")

    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("Bot Started!")
    signal(SIGINT, exit_clean_up)

app.start()
main()

main_loop.run_forever()
