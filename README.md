# Travel Guide Generator
### AI-Powered Personalized Travel Planning Application

**Developer**: Ahmad Khan

---

## 1️⃣ Project Overview

**Travel Guide Generator** is an intelligent web application that leverages OpenAI's GPT models to create personalized, day-by-day travel itineraries. This project demonstrates the practical application of Large Language Models (LLMs) in solving real-world planning challenges through AI-assisted workflows.

---

## 2️⃣ Purpose

### Problem Statement
Planning a comprehensive travel itinerary is time-consuming and often overwhelming. Travelers must:
- Research destinations and attractions
- Balance time constraints with activities
- Consider accessibility requirements and personal interests
- Organize daily schedules logically
- Account for travel logistics between locations

Traditional travel planning requires hours of manual research across multiple websites, guidebooks, and forums.

### AI-Driven Solution
This application solves the travel planning problem by:
- **Automating Research**: AI aggregates knowledge about destinations, attractions, and local experiences
- **Personalization**: Generates custom itineraries based on individual preferences and constraints
- **Intelligent Scheduling**: Creates realistic day-by-day plans considering time, distance, and activity duration
- **Accessibility Integration**: Respects user-defined guardrails (wheelchair access, kid-friendly, budget constraints)

### AI-Assisted Workflow Benefits
- **Time Efficiency**: Reduces planning time from hours to seconds
- **Comprehensive Coverage**: AI draws from vast training data about global destinations
- **Contextual Understanding**: GPT models understand nuanced requirements like "kid-friendly activities" or "no early morning tours"
- **Structured Output**: Delivers organized, actionable plans ready for execution

---

## 3️⃣ What the Code Does

### High-Level Architecture

This application implements a **conversational AI pipeline** using the following workflow:

1. **User Input Collection** (Streamlit Interface)
   - Destination, trip duration, interests, and constraints are captured through a web form

2. **Prompt Engineering** (AI Integration)
   - User inputs are structured into carefully crafted prompts
   - System prompts define the AI's role as an expert travel planner
   - Context is provided to ensure relevant, practical recommendations

3. **LLM Processing** (OpenAI API)
   - The application sends prompts to OpenAI's GPT models (gpt-4o, gpt-4o-mini, gpt-4-turbo)
   - Implements fallback mechanism: if one model fails, automatically tries alternatives
   - Handles API responses with defensive error checking

4. **Response Processing**
   - Extracts structured markdown content from AI responses
   - Validates completeness and formatting

5. **Multi-Format Output**
   - **Web Display**: Renders formatted itinerary with day-by-day breakdown
   - **PDF Generation**: Converts markdown to professionally formatted PDF using ReportLab
   - Enables offline access and sharing

### AI-Specific Logic

**Prompt Design**:
- System prompt establishes AI persona (experienced travel guide planner)
- Defines output structure (overview, daily itinerary, tips, budget, reminders)
- User prompt provides contextual details for personalization

**Robustness**:
- Multi-model fallback ensures reliability
- Token management (max 2500 tokens per response)
- Temperature setting (0.7) balances creativity with factual accuracy

**Content Extraction**:
- Handles various API response formats
- Safely parses text and list-based content blocks
- Implements defensive programming for SDK changes

---

## 4️⃣ How to Run or Use

### Prerequisites
- **Python 3.8+** installed on your system
- **OpenAI API Key** (obtain from https://platform.openai.com/api-keys)
- Active internet connection

### Installation Steps

1. **Clone or Download the Project**
   ```bash
   cd path/to/travel_guide
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   This installs:
   - `streamlit` - Web application framework
   - `openai` - OpenAI API client
   - `python-dotenv` - Environment variable management
   - `reportlab` - PDF generation library

3. **Configure API Key**
   
   Create a `.env` file in the project directory:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```
   
   ⚠️ **IMPORTANT**: Never commit `.env` to version control (see Security section below)

4. **Launch the Application**
   ```bash
   streamlit run travel_guide.py
   ```
   
   The app will open automatically in your browser at `http://localhost:8501`

### Using the Application

1. **Enter Travel Details**:
   - **Destination**: City/country you're visiting (e.g., "Barcelona, Spain")
   - **Number of Days**: Trip duration (e.g., "5 days")
   - **Special Interests**: Activities you enjoy (e.g., "Architecture, Food & Wine, Beaches")
   - **Guardrails**: Constraints (e.g., "Wheelchair accessible only, Budget under $100/day")

2. **Generate Plan**: Click "🗺️ Generate Travel Plan"

3. **Review Output**: Browse the AI-generated day-by-day itinerary

4. **Download PDF**: Click "⬇️ Download Travel Plan PDF" for offline access

5. **Reset**: Use "🔄 Reset Form" to plan a different trip

### Example Usage

**Input**:
- Destination: *Tokyo, Japan*
- Days: *7*
- Interests: *Technology, Food & Cuisine, Traditional Culture, Shopping*
- Guardrails: *No walking tours (prefer public transit), Vegetarian food options*

**Output**: A complete 7-day itinerary with specific districts, attractions, restaurants, and transit instructions for each day, respecting vegetarian preferences.

---

## 🔒 Security & Safe Sharing

### Protected Information

This repository **DOES NOT** and **MUST NOT** contain:

- ❌ OpenAI API keys
- ❌ Authentication tokens
- ❌ Passwords or credentials
- ❌ `.env` files with actual secrets
- ❌ Private or personally identifiable information (PII)

### Safe Configuration

✅ **What IS included**:
- `.env.example` - Template file showing required variables (with placeholder values)
- Source code without hardcoded secrets
- Documentation on how to configure secrets locally

✅ **What IS in `.gitignore`**:
```
.env
*.pdf
__pycache__/
*.pyc
```

### Best Practices

1. **API Key Storage**:
   - Store API keys in `.env` file (never commit to Git)
   - Use environment variables for sensitive data
   - Rotate keys if accidentally exposed

2. **Version Control**:
   - Always use `.gitignore` to exclude `.env`
   - Review commits before pushing to ensure no secrets leaked
   - Use tools like `git-secrets` or `truffleHog` for automated scanning

3. **Sharing the Project**:
   - Share only source code and documentation
   - Recipients must obtain their own API keys
   - Include clear instructions in README (this document)

4. **If Secrets Are Exposed**:
   - Immediately revoke/regenerate the API key at https://platform.openai.com/api-keys
   - Remove the file from Git history using `git filter-branch` or BFG Repo-Cleaner
   - Notify relevant parties if credential exposure poses risk

---

## 📁 File Structure

```
travel_guide/
├── travel_guide.py          # Main application code
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template (safe to commit)
├── .env                    # Your actual secrets (NEVER COMMIT)
├── .gitignore              # Excludes sensitive files
├── README.md               # This documentation
└── CHANGES_EXPLAINED.md    # Development notes
```

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| **"Missing dependency" error** | Run `pip install -r requirements.txt` |
| **"Invalid API key" (401 error)** | Verify `.env` file exists with correct `OPENAI_API_KEY=sk-...` format |
| **"Model not available" error** | App auto-falls back to alternative models; check OpenAI account status |
| **Empty response from API** | Check API quota/credits at https://platform.openai.com/usage |

---

## 📊 Technical Stack

- **Frontend**: Streamlit (Python web framework)
- **AI/LLM**: OpenAI GPT-4o, GPT-4o-mini, GPT-4-turbo
- **PDF Generation**: ReportLab
- **Environment Management**: python-dotenv
- **Language**: Python 3.8+

---

## 📝 Notes

- Each API call consumes OpenAI credits based on token usage
- Longer trips (more days) require more tokens and cost more
- The application does not persist data between sessions
- PDF files are generated locally in the project directory

---

## 📄 License

This project is free to use and modify for educational, personal, or commercial purposes.

---

**Developer**: Ahmad Khan  
**Course**: AI Practitioner Class - Assignment 6  
**Date**: 2026
