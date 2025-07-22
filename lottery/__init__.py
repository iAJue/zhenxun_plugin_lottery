import random

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.plugin import PluginMetadata

from zhenxun.configs.utils import Command, PluginExtraData
from zhenxun.services.log import logger
from zhenxun.utils.message import MessageUtils

__plugin_meta__ = PluginMetadata(
    name="群抽奖禁言",
    description="参与抽奖，被随机禁言",
    usage="""
    指令：
      - 抽奖                 (直接参与抽奖并被随机禁言)
    """.strip(),
    extra=PluginExtraData(
        author="阿珏酱", version="1.0", commands=[
            Command(command="抽奖")
        ]
    ).to_dict(),
)

# 命令注册
direct_lottery_cmd = on_command("抽奖", priority=5, block=True)

# 直接设置禁言时长范围（分钟）
MIN_MUTE_TIME = 1  # 最短1分钟
MAX_MUTE_TIME = 480  # 最长8小时

@direct_lottery_cmd.handle()
async def handle_direct_lottery(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    user_id = event.user_id
    
    # 随机禁言时长（分钟）
    mute_time = random.randint(MIN_MUTE_TIME, MAX_MUTE_TIME)
    
    try:
        # 获取用户昵称
        user_name = await get_member_nickname(bot, group_id, user_id)
        
        # 执行禁言
        await bot.set_group_ban(group_id=group_id, user_id=user_id, duration=mute_time * 60)
        
        # 返回成功消息并结束处理
        return await MessageUtils.build_message(
            f"恭喜 {user_name}({user_id}) 参与\"抽奖\"！\n"
            f"🎉 获得了 {mute_time}分钟禁言大礼包 🎉"
        ).finish()
    except Exception as e:
        logger.error(f"直接抽奖禁言失败: {e}", "群抽奖禁言")
        await MessageUtils.build_message(f"抽奖禁言失败，可能是机器人没有禁言权限").finish()

# 辅助函数：获取群成员昵称
async def get_member_nickname(bot: Bot, group_id: int, user_id: int) -> str:
    try:
        member_info = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
        return member_info.get("card", "") or member_info.get("nickname", str(user_id))
    except Exception as e:
        logger.error(f"获取成员昵称失败: {e}", "群抽奖禁言")
        return str(user_id)
