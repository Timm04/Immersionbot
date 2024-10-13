# TheMoeWay Immersion Bot

📢 **New contributors [welcome](contribute.md)!**

## What is the Immersion Bot?
The Immersion bot helps you track and manage your language learning journey.

Powerful features that it provides:
- 📝 Logging your learning progress with the ability to use APIs like Anilist and VNDB to get more details for your immersion.
- 🔍 Visualizes your own and others progress with graphs.
- 💪 Compete with everyone in a friendly environment on the leaderboard and get a reward at the end of each month. 
- 🔑 Allows you to export your progress so you can analyze it even better
- ⚙️ Built in log deletion in case you make a mistake with your logs.
- 🙋‍♂️ Streak counts and achievements to motivate you to immerse more.

![image](https://github.com/user-attachments/assets/4e6973ed-e13f-4222-967b-c3712b0af86f)![Discord_qAaMhCHKcP](https://github.com/user-attachments/assets/715751b8-de6b-447a-ad47-1c2a3249fa7b)![Discord_CugvmcF4Oj](https://github.com/user-attachments/assets/a25e72c0-4c9d-4537-9519-27246ac44758)![Discord_1slmR1tO1L](https://github.com/user-attachments/assets/d3155e29-49b1-4746-b117-8265eb31e639)

## Installation

Before you can install and run the bot, make sure you have the following:
1. Python 3.9.0
   You can download Python from [here](https://www.python.org/downloads/release/python-390/).
2. Discord Developer Account
   You need a Discord account and a registered bot in the Discord Developer Portal.
3. Git (to clone this  repository)
   Download Git from [here](https://git-scm.com/).
4. A text editor
   You can use any text editor (e.g., VC code, Sublime Text, Atom).

## Steps to Install
### 1. Clone the Repository
First, clone the bot repository to your local machine.
```
git clone https://github.com/themoeway/Immersionbot.git
cd Immersionbot
```
### 2. Create a Virtual Environment (Optional but Recommended)
It is recommended to create a virtual environment to manage dependencies cleanly.
```
python -m venv venv
source venv/bin/activate   # For Linux/MacOS
# or
venv\Scripts\activate      # For Windows
```
### 3. Install Dependencies
Use pip to install the required dependencies specified in the requirements.txt file.
```
pip install -r requirements.txt
```
### 4. Create a Discord Bot Application
  1. Go to the Discord Developer Portal and log in.
  2. Click New Application and give it a name.
  3. In the Bot section, create a new bot and copy its Token.
  4. Tick `Presence Intent`, `Server Members Intent` and `Message Content Intent`.
  5. Under OAuth2 > URL Generator, enable `bot` and `applications.commands` scopes. Assign administrator permissions and copy the link and add the bot to your server.
  6. Paste the token at the bottom of the `launch_bot.py` file.
### 6. Run the Bot
To start the bot, run the following command:
```
python launch_bot.py
```
### 7. Verify the Bot is Working
Once the bot is running, you can test its functionality by interacting with it on your Discord server.

## Contributing

🚀 **Dip your toes into contributing by looking at issues with the label [good first issue](https://github.com/yomidevs/yomitan/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).**

Since this is a distributed effort, we **highly welcome new contributors**! Feel free to browse the [issue tracker]([https://github.com/yomidevs/yomitan/issues](https://github.com/themoeway/Immersionbot/issues)), and read our [contributing guidelines](contribute.md).

If you're looking to code, please let us know what you plan on working on before submitting a Pull Request. This gives the core maintainers an opportunity to provide feedback early on before you dive too deep. You can do this by opening a Github Issue with the proposal.


