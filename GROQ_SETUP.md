# Setting up Groq API Key in Streamlit Cloud

## Steps to add the secret:

1. Go to your Streamlit Cloud dashboard: https://share.streamlit.io/
2. Click on your app: **sentimentxdashboard**
3. Click the **⚙️ Settings** button (three dots menu)
4. Select **Secrets**
5. Add the following in the secrets editor:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

Replace `your_groq_api_key_here` with your actual Groq API key.

6. Click **Save**
7. Click **Reboot app**

## What changed:

- ✅ Integrated **Groq AI** (Llama 3.3 70B model) for realistic tweet generation
- ✅ Tweets are now contextually relevant to the searched brand
- ✅ More diverse and natural-sounding social media content
- ✅ Free tier: 14,400 requests/day (plenty for this use case)
- ✅ Cached results for 1 hour to save API calls

## Local Testing:

The secret is already configured in `.streamlit/secrets.toml` for local development.
This file is gitignored for security.

## Features:

- AI generates tweets with realistic:
  - Customer reviews
  - News reactions  
  - Questions and discussions
  - Complaints and praise
  - Emojis and hashtags
  - Natural typos and language
