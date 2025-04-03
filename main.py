import tomllib  # 确保导入tomllib以读取配置文件
import os  # 确保导入os模块

from WechatAPI import WechatAPIClient
from utils.decorators import *
from utils.plugin_base import PluginBase
from loguru import logger
import json

import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *

from database.XYBotDB import XYBotDB

class FeiShuWiki(PluginBase):
    description = "获取飞书Wiki多维表内容"
    author = "yunus"
    version = "1.0.0"

    # 同步初始化
    def __init__(self):
        super().__init__()

        # 获取配置文件路径
        config_path = os.path.join(os.path.dirname(__file__), "config.toml")

        try:

            with open("main_config.toml", "rb") as f:
                config = tomllib.load(f)

            self.admins = config["XYBot"]["admins"]

            with open(config_path, "rb") as f:
                config = tomllib.load(f)

            basic_config = config.get("FeiShuWiki", {})
            self.enable = basic_config.get("enable", False)  # 读取插件开关
            self.command = basic_config.get("command", ["群搜"])
            self.appId = basic_config.get("app_id", "")
            self.appSecret = basic_config.get("app_secret", "")
            self.tableId = basic_config.get("table_id", "")
            self.viewID = basic_config.get("view_id", "")
            self.appToken = basic_config.get("app_token", "")

            self.searchName = basic_config.get("search_name", "资源名")
            self.searchSize = basic_config.get("search_size", 20)

            self.price = basic_config.get("price", 0)
            self.admin_ignore = basic_config.get("admin_ignore", False)
            self.whitelist_ignore = basic_config.get("whitelist_ignore", False)

            self.db = XYBotDB()

        except Exception as e:
            logger.error(f"加载FeiShuWiki配置文件失败: {str(e)}")
            self.enable = False  # 如果加载失败，禁用插件

    @on_text_message
    async def handle_text(self, bot: WechatAPIClient, message: dict):
        if not self.enable:
            return

        content = str(message["Content"]).strip()
        command = content.split(" ")

        if not len(command) or command[0] not in self.command:
            return

        if len(command) == 1:
            await bot.send_at_message(message["FromWxid"], f"❌命令格式错误！{self.command_format}",
                                      [message["SenderWxid"]])
            return

        try:
            if await self._check_point(bot, message):
                search_name = content[len(command[0]):].strip()
                await self.feishu_wiki(bot, message, search_name)
                return
        except Exception as e:
            logger.error(e)

    async def feishu_wiki(self, bot: WechatAPIClient, message: dict, search_name):
        logger.info(f"飞书查询开始: {search_name}")
        try:
            client = lark.Client.builder().app_id(self.appId).app_secret(self.appSecret).log_level(
                lark.LogLevel.DEBUG).build()

            request: SearchAppTableRecordRequest = (
                SearchAppTableRecordRequest.builder()
                .app_token(self.appToken)
                .table_id(self.tableId)
                .user_id_type("open_id")
                .page_size(self.searchSize)
                .request_body(
                    SearchAppTableRecordRequestBody.builder()
                    .view_id(self.viewID)
                    .filter(FilterInfo.builder().conjunction("and").conditions([Condition.builder().field_name(
                        self.searchName).operator("contains").value([search_name]).build()]).build())
                    .automatic_fields(False)
                    .build()
                )
                .build()
            )

            response: SearchAppTableRecordResponse = client.bitable.v1.app_table_record.search(request)

            if not response.success():
                logger.error(
                    f"client.bitable.v1.app_table_record.search failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}"
                )
                await bot.send_at_message(message["FromWxid"], f"❌查询错误，请联系管理员", [message["SenderWxid"]])
                return

            data = response.data
            items = data.items
            total = data.total

            # 根据你的多维表返回信息自定义推送内容
            output_message = "\n-----XYBotV2-----\n"
            output_message += f"查询资源：{search_name}\n"
            output_message += f"共查询到：{total} 条\n"
            # output_message += f"扣除积分：{self.price}\n"

            if total > 0:
                output_message += "---\n"
                for item in items:
                    fields = item.fields
                    resource_name = fields.get("资源名", [{}])[0].get("text", "未知资源") if isinstance(
                        fields.get("资源名"), list) else "未知资源"
                    link_info = fields.get("网盘链接", {})
                    link = link_info.get("link", "无链接") if isinstance(link_info, dict) else "无链接"

                    output_message += f"{resource_name}\n{link}\n---\n"

                output_message += f"\n更多请点击链接查看：https://github.com/yunus0906/XYBotV2-FeiShuWiki"

            await bot.send_at_message(message["FromWxid"], output_message, [message["SenderWxid"]])

        except Exception as e:
            logger.error(e)

    async def _check_point(self, bot: WechatAPIClient, message: dict) -> bool:
        wxid = message["SenderWxid"]

        logger.error(f"{self.admin_ignore} {self.admins}, {wxid}")

        if wxid in self.admins and self.admin_ignore:
            return True
        elif self.db.get_whitelist(wxid) and self.whitelist_ignore:
            return True
        else:
            if self.db.get_points(wxid) < self.price:
                await bot.send_at_message(message["FromWxid"],
                                          f"\n"
                                          f"😭你的积分不够啦！需要 {self.price} 积分",
                                          [wxid])
                return False

            self.db.add_points(wxid, -self.price)
            return True