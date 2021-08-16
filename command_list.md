# SQCS_bot command list

Bot version: 1.32.8.16

此文件為由程式自動生成的，如果有使用上的疑慮請直接詢問總召。

## channel.py

### +protect on <channel_id: int>

權限：`總召` `Administrator`

描述：開啟 頻道<channel_id> 的保護模式，如果沒有輸入代表目前的頻道。

```markdown
<channel_id: Discord 中頻道的id>
```

### +protect off <channel_id: int>

權限：`總召` `Administrator`

描述：關閉 頻道<channel_id> 的保護模式，如果沒有輸入代表目前的頻道。

```markdown
<channel_id: Discord 中頻道的id>
```

### +protect all_on

權限：`總召` `Administrator`

描述：開啟伺服器中所有頻道的保護模式。

### +protect all_off

權限：`總召` `Administrator`

描述：關閉伺服器中所有頻道的保護模式。

### +protect clear_list

權限：`總召` `Administrator`

描述：清除資料庫中的頻道保護列表。

### +meeting on <channel_id: int>

權限：`總召` `Administrator`

描述：開啟 語音頻道<channel_id> 的開會模式。

```markdown
<channel_id: Discord 中頻道的id>
```

### +meeting off <channel_id: int>

權限：`總召` `Administrator`

描述：關閉 語音頻道<channel_id> 的開會模式。

```markdown
<channel_id: Discord 中頻道的id>
```

## cogs.py

### +cogs load <target_cog: str>

權限：`總召` `Administrator`

描述：加載 插件<target_cog>。

### +cogs unload <target_cog: str>

權限：`總召` `Administrator`

描述：卸載 插件<target_cog>。

### +cogs reload <target_cog: str>

權限：`總召` `Administrator`

描述：重新加載 插件<target_cog>。

### +shut_down

權限：`總召` `Administrator`

描述：安全關閉機器人。

## database.py

### +db refresh_db

權限：`總召` `Administrator`

描述：重新整理搖光資料庫。

### +db copy <ori_db_name: str> <ori_coll_name: str> <target_db_name: str> <target_coll_name: str>

權限：`總召` `Administrator`

描述：複製集合中的資料。

### +db move <ori_db_name: str> <ori_coll_name: str> <target_db_name: str> <target_coll_name: str>

權限：`總召` `Administrator`

描述：移動集合中的資料。

## kick.py

### +kick list

權限：`總召` `Administrator`

描述：列出待踢除名單。

### +kick add <target_member: Union[discord.Member, int]>

權限：`總召` `Administrator`

描述：將 成員<target_member> 加入待踢除名單。

```markdown
<target_member: 可直接標註成員，或是成員在Discord中的id>
```

### +kick remove <target_member: Union[discord.Member, int]>

權限：`總召` `Administrator`

描述：將 成員<target_member> 移出待踢除名單。

```markdown
<target_member: 可直接標註成員，或是成員在Discord中的id>
```

### +kick kick_single <target_member: Union[discord.Member, int]> <kick_reason: str>

權限：`總召` `Administrator`

描述：將 成員<target_member> 踢除（需要在待踢除名單中）。

```markdown
<target_member: 可直接標註成員，或是成員在Discord中的id>
<kick_reason: 踢除原因>
```

### +kick kick_all

權限：`總召` `Administrator`

描述：將所有在踢除名單中的成員踢除。

### +list

權限：`總召` `Administrator`

描述：列出黑名單。

### +add <user_id: int>

權限：`總召` `Administrator`

描述：將 成員<user_id> 加入黑名單。

```markdown
<user_id: 成員的Discord id>
```

## logger.py

### +log query_len <title: str>

權限：`總召` `Administrator`

描述：查詢在 日誌<title> 中的資料。

```markdown
<title: 可為 `CmdLogging` 或是 `LectureLogging`>
```

### +log release <title: str>

權限：`總召` `Administrator`

描述：釋放在 日誌<title> 中的資料。

```markdown
<title: 可為 `CmdLogging` 或是 `LectureLogging`>
```

## main.py

### +info

權限：`無`

描述：查詢SQCS_bot的資料。

### +ping

權限：`無`

描述：戳一下機器人。

### +fix_role

權限：`總召` `Administrator`

描述：手動修復身分組。

## picture.py

### +pic list

權限：`無`

描述：查詢資料庫中所有的圖片。

### +pic add <link: str>

權限：`無`

描述：將一張圖片加入到資料庫中。

```markdown
<link: 圖片的超連結>
```

### +pic remove <index: int>

權限：`無`

描述：將一張圖片從資料庫中移除。

```markdown
<index: 圖片的位置（可利用list進行查詢）>
```

### +pic random

權限：`無`

描述：發送一張隨機的圖片。

## text.py

### +text clear <msg_id: int>

權限：`總召` `Administrator`

描述：從目前的訊息往上刪除至 訊息<msg_id>

```markdown
<msg_id: 訊息在Discord中的id>
```

## voice.py

### +voice timer <channel_id: int> <countdown: int>

權限：`總召` `Administrator`

描述：在 <countdown>秒後將 語音頻道<channel_id> 中的所有成員移出。

```markdown
<channel_id: 語音頻道的Discord id>
<countdown: 倒數的時間>
```

### +voice default_role_connect <channel_id: int> <mode: int>

權限：`總召` `Administrator`

描述：將 語音頻道<channel_id> 設置為普通成員 可/否 連結

```markdown
<channel_id: 語音頻道的id>
<mode: 1 -> 可； 0 -> 不可>
```

### +personal make_channel <members: commands.Greedy[discord.Member]>

權限：`無`

描述：在語音終端機時使用指令，便可為 成員們<members> 創立私人語音包廂。

```markdown
<members: 一次性@所有要加入的成員>
```

## weather.py

### +wea query <target_county: str>

權限：`無`

描述：查詢 城市<target_county> 的天氣狀況，如果沒有輸入即為使用者地區身分組之城市。

```markdown
<target_county: 臺灣的縣市>
```

## tools.py

## cadre.py

### +ca apply <cadre: str>

權限：`無`

描述：於幹部申請區申請 幹部<cadre>

```markdown
<cadre: 可為SQCS現在有的幹部部門>
```

### +ca list

權限：`總召` `Administrator`

描述：列出現在的所有幹部申請。

### +ca permit <permit_id: int>

權限：`總召` `Administrator`

描述：批准 成員<permit_id> 的幹部申請。

```markdown
<permit_id: 要批准成員的Discord id>
```

### +ca search <search_id: int>

權限：`總召` `Administrator`

描述：查詢 成員<permit_id> 的幹部申請。

```markdown
<permit_id: 要查詢成員的Discord id>
```

### +ca remove <delete_id: int>

權限：`總召` `Administrator`

描述：移除 成員<permit_id> 的幹部申請。

```markdown
<permit_id: 要移除的成員之Discord id>
```

## deep_freeze.py

### +df mani <member_id: int> <status: int>

權限：`總召` `Administrator`

描述：將 成員<member_id> 的深度凍結狀態設定為 status

```markdown
<member_id: 成員在Discord中的id>
<status: 0 -> 無凍結； 1 -> 凍結>
```

### +df list

權限：`總召` `Administrator`

描述：列出所有目前在深度凍結中的成員。

## fluctlight.py

### +fluct create <member_id: int>

權限：`總召` `Administrator`

描述：幫 成員<member_id> 手動產生搖光。

```markdown
<member_id: 成員在Discord中的id>
```

### +fluct delete <member_id: int>

權限：`總召` `Administrator`

描述：幫 成員<member_id> 手動刪除搖光。

```markdown
<member_id: 成員在Discord中的id>
```

### +fluct reset <member_id: int>

權限：`總召` `Administrator`

描述：幫 成員<member_id> 手動重新設定搖光。

```markdown
<member_id: 成員在Discord中的id>
```

## lecture.py

### +lect_config list

權限：`總召` `Administrator`

描述：列出所有有註冊的講座。

### +lect_config add

權限：`總召` `Administrator`

描述：註冊講座資料。

### +lect_config remove <del_lect_week: int>

權限：`總召` `Administrator`

描述：刪除講座資料。

### +lect start <week: int>

權限：`總召` `Administrator`

描述：開始講座。

```markdown
<week: 星期數>
```

### +lect end <week: int>

權限：`總召` `Administrator`

描述：結束講座。

```markdown
<week: 星期數>
```

### +lect_verify attend <token: str>

權限：`無`

描述：尚未啟用。

## query.py

### +query quiz

權限：`總召` `Administrator`

描述：查詢懸賞活動的目前狀態。

### +query my_data

權限：`無`

描述：查詢個人搖光資料。

### +query member_data <target_id: int>

權限：`總召` `Administrator`

描述：查詢 成員<target_id> 的搖光資料。

```markdown
<target_id: 成員的Discord id>
```

### +query guild_active

權限：`無`

描述：查詢伺服器活躍度。

## quiz.py

### +quiz alter_standby_ans <alter_answer: str>

權限：`總召` `Administrator` `學術`

描述：修改下次的懸賞答案。

```markdown
<alter_answer: 下次的懸賞答案>
```

### +quiz alter_formal_ans <alter_answer: str>

權限：`總召` `Administrator` `學術`

描述：修改本次的懸賞答案。

```markdown
<alter_answer: 新的本次的懸賞答案>
```

### +quiz set_qns_link <qns_link: str>

權限：`總召` `Administrator` `學術`

描述：設定問題連結。

```markdown
<qns_link: 問題連結>
```

### +quiz set_ans_link <ans_link: str>

權限：`總召` `Administrator` `學術`

描述：設定答案連結。

```markdown
<qns_link: 答案連結>
```

### +quiz repost_qns

權限：`總召` `Administrator` `學術`

描述：重新公告問題。

### +quiz repost_ans

權限：`總召` `Administrator` `學術`

描述：重新公告答案。

## verify.py

### +lect_generate_token <lecture_week: int>

權限：`總召` `Administrator`

描述：尚未啟用。

## workshop.py

### +ws snapshot <voice_id: int>

權限：`總召` `Administrator`

描述：將 語音頻道<voice_id> 設定為目前在頻道中的成員所屬。

```markdown
<voice_id: 語音頻道的id>
```

