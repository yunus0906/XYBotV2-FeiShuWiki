# 飞书知识库多维表查询 (FeiShuWiki)

> **本插件是 [XYBotv2](https://github.com/HenryXiaoYang/XYBotv2) 的一个插件。**

> 获取飞书知识库多维表中内容。
> 
> 飞书多维表存在线展示的数据非常好用，类似于SQL表，查询数据很方便，这个插件可以快速接入你的多维表并查询。

## 使用

> 该文档仅提供解题思路，小白可根据文档操作，大佬可根据自己需求自定义

```bash 
pip install lark_oapi
```

1. 首先要有一个wiki知识库，然后知识库里准备好多维数据表，本插件是将多维数据表内的数据输出给XYBotV2的 
   - 如果你的文档开启了高级权限，需要在多维表右上角【...】=>【更多】=>【添加文档应用】
   - 创建应用后别忘记开启权限，贴一下我这里的权限
   `base:app:read、base:record:retrieve、base:table:read、bitable:app、wiki:node:read、wiki:wiki:readonly`
2. 请登录 https://open.feishu.cn/app 飞书开发者后台新建自建应用，获取应用凭证
   
3. 获取 app_token 和 table_id
   - app_token 可以通过utils.py获取，或者在飞书官网获取 https://open.feishu.cn/document/server-docs/docs/wiki-v2/space-node/get_node
   - table_id 在url地址栏获取，通常是地址栏中的table https://xxx000.feishu.cn/wiki/L0Q5w***mnYe?fromScene=spaceOverview&table=tbl**ZGiV&view=ve**vaI

## 配置

在`config.toml`中设置：

```toml
[FeiShuWiki]

# 获取飞书wiki(知识库)中数据表的内容
# > 该文档仅提供解题思路，小白可根据文档操作，大佬可根据自己需求自定义

enable = true # 是否启用插件
command = ["群搜"] # 搜索关键词

app_id = "" # 飞书开放平台 应用凭证 App ID
app_secret = "" # 飞书开放平台 应用凭证 App Secret

wiki_token = "" # wiki的token，地址栏中 wiki/后的字符串就是
table_id = "" # 地址栏中获取table_id
view_id = "" # 地址栏中获取view_id

app_token = "" # 可以在utils中获取，获取AppToken需要准备好AppID、AppSecret、WikiToken。返回json中 obj_token就是当前值

search_name = "资源名" # 查询的列表名
search_size = 20 # 查询页数
```

## 开发日志

- v1.0.0: 202500331 第一版发布。

## 许可证

MIT License
