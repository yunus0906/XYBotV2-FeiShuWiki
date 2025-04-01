import tomllib  # 确保导入tomllib以读取配置文件
import os  # 确保导入os模块
from loguru import logger
import json

import lark_oapi as lark
from lark_oapi.api.wiki.v2 import *


# 使用说明: https://open.feishu.cn/document/server-docs/docs/wiki-v2/space-node/get_node
def main():

    # 获取配置文件路径
    config_path = os.path.join(os.path.dirname(__file__), "config.toml")

    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    # 读取基本配置
    basic_config = config.get("FeiShuWiki", {})
    enable = basic_config.get("enable", False)
    appId = basic_config.get("app_id", "")
    appSecret = basic_config.get("app_secret", "")
    wikiToken = basic_config.get("wiki_token", "")

    if(enable):
        # 创建client
        client = lark.Client.builder() \
            .app_id(appId) \
            .app_secret(appSecret) \
            .log_level(lark.LogLevel.DEBUG) \
            .build()

        # 构造请求对象
        request: GetNodeSpaceRequest = GetNodeSpaceRequest.builder() \
            .token(wikiToken) \
            .obj_type("wiki") \
            .build()

        # 发起请求
        response: GetNodeSpaceResponse = client.wiki.v2.space.get_node(request)

        # 处理失败返回
        if not response.success():
            logger.error(
                f"client.wiki.v2.space.get_node failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return

        # 处理业务结果
        logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
    main()
