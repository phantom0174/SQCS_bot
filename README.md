![](https://img.shields.io/uptimerobot/status/m786417212-72995a6e32a6e120933f8255)
![](https://img.shields.io/uptimerobot/ratio/7/m786417212-72995a6e32a6e120933f8255)
![](https://img.shields.io/uptimerobot/ratio/m786417212-72995a6e32a6e120933f8255)
# HSQCC_bot
## 🛠 Builder


### Event update
- 2020/11/18: Bot 24/7 online.
- 2020/11/25: Intents activate.
- 2020/11/28: Quiz event automize.
- 2020/11/29: Member full info sqlite3-lize.
- 2020/11/29: MVisualizer via score API functions set.
- 2020/12/04: Bot communication guild set, lecture function work normally.
- 2020/12/06: Set up event log feature.
- 2020/12/07: Bot Cog-lized.
- 2020/12/13: Emoji Added.
- 2020/12/14: Fix repl update.
- 2020/12/21: Move database to MongoDB.


### Bot Info
 - Bot set by phantom0174
 - This bot manages event-related tasks in DC guild.
 - If using relevent data, please cite the data source.

### Command list
* help
  * Show all command & command group
  * Authority requirements: none

* ping
  * Basic ping command
  * Authority requirements: none

* m_check (Member check)
  * Show the list of all members in guild.
  * Authority requirements: General Coordinator, Administrator
  * Results can only be seen at host.

* clear \<quantity\>
  * The command that deletes message.
  * Authority requirements: none

---

* **Quiz event group** (group name: quiz)

  * quiz_push \<stand-by answer\> (Quiz standby-answer pushback)
    * Push the answer of the next quiz event.
    * Authority requirements: General Coordinator

  * **Start & End command had already been automized**


* **Lecture event group** (group name: lect)

  * start \<week\>
    * The command that starts the lecture.
    * Authority requirements: General Coordinator, Administrator

  * ans_check \<\[correct answer list\]\>
    * To check if the members' answer is right or not.
    * Authority requirements: General Coordinator, Administrator

  * end
    * The command that ends the lecture.
    * Authority requirements: General Coordinator, Administrator


* **Picture group** (group name: pic)

  * p_m \<mode(0 -> delete || 1 -> pushback)\> \<manipulate object(0 -> index || 1 -> url)\> (Picture manipulate)
    * Manipulates the pictures in the database.
    * Authority requirements: General Coordinator, Administrator

  * p_check (Picture check)
    * Show all the pictures in the database.
    * Authority requirements: none

  * rpic (Random picture)
    * Send a random picture.
    * Authority requirements: none
