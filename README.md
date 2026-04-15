# X Auto Poster 🚀

Autonomous X (Twitter) marketing bot for indie app developers.  
Reads your project folder → uses Gemini AI to write posts → schedules 5-6 tweets/day automatically.

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure your .env
```bash
cp .env.example .env
# Then edit .env with your real API keys
```

Get your keys:
- **X API keys**: https://developer.x.com/en/portal/dashboard  
  (Your app needs **Read and Write** permissions)
- **Gemini API key**: https://aistudio.google.com/app/apikey

### 3. Point it at your project folder
Set `PROJECT_FOLDER` in `.env` to the path of your app's folder.  
It will read `.md`, `.txt`, `.py`, `.json`, `.html` files automatically.

---

## Usage

```bash
# Test your X API connection
python main.py test

# Preview AI-generated posts (no saving)
python main.py preview

# Generate 6 posts and schedule them for today
python main.py generate

# Generate and schedule for tomorrow
python main.py generate tomorrow

# View the pending queue
python main.py queue

# Start the autonomous scheduler (runs 24/7, posts at scheduled times)
python main.py run

# View post history
python main.py history

# Delete a post from the queue
python main.py delete <id>
```

---

## Post Tones

The AI rotates through these tones across your 6 daily posts:

| Tone | Description |
|---|---|
| `funny` | Witty, relatable humour |
| `informative` | Tips, features, "did you know" |
| `business` | Value/ROI focused |
| `hype` | Energy, launches, milestones |
| `behind-the-scenes` | Authentic builder story |
| `question` | Engagement-driving questions |

Edit `POST_TONES` in `config.py` to customise or add your own.

---

## Running Autonomously (24/7)

For continuous operation, run with `nohup` or as a system service:

```bash
# Run in background (Linux/Mac)
nohup python main.py run > poster.log 2>&1 &

# Or with screen
screen -S poster
python main.py run
# Ctrl+A then D to detach
```

**Recommended workflow:**
1. `python main.py generate` each morning (or automate it)
2. `python main.py run` keeps running in the background and fires posts at the right times

---

## Gemini Models

Set `GEMINI_MODEL` in `.env` to switch models:

| Model | Best for |
|---|---|
| `gemini-3.1-flash-lite-preview` | Fastest, cheapest (recommended) |
| `gemini-2.5-flash` | Best quality/cost balance |
| `gemma-4-31b-it` | Open model, strong performance |

---

## File Structure

```
x-auto-poster/
├── main.py            # CLI entry point
├── config.py          # Loads .env settings
├── folder_reader.py   # Reads your project folder
├── ai_generator.py    # Gemini post generation
├── post_queue.py      # SQLite queue management
├── x_poster.py        # X API v2 (tweepy)
├── scheduler.py       # APScheduler engine
├── .env               # Your secrets (never commit!)
├── .env.example       # Template
├── requirements.txt
└── posts.db           # Auto-created SQLite database
```
