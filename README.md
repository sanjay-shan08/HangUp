<div align="center">
  <h1>🛡️ HangUp</h1>
  <p><strong>An AI-powered scam inoculation coach protecting vulnerable individuals against social engineering.</strong></p>
  
  <p>
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/Architecture-WebSockets-green.svg" alt="Architecture">
    <img src="https://img.shields.io/badge/AI-Gemini_3.6_Flash-orange.svg" alt="Gemini AI">
  </p>
</div>

<br/>

> **Digital arrest, fake bank officer, and logistics block scams cost millions every year. Existing defenses (like spam filters) are entirely reactive, and enterprise vishing simulators aren't built for consumers.**

**HangUp** is a proactive, zero-latency solution that lets vulnerable individuals safely rehearse scam scenarios with an AI agent *before* a real scammer calls. It features a **Live Hang-Up Coach** that interrupts the simulation the exact moment a user makes a dangerous mistake (like sharing an OTP or ID number), followed by an automated **Safe-Word Drill** to establish robust family verification protocols.

---

## ✨ Core Features

* 🎭 **Hyper-Realistic Personas:** Powered by Gemini, the AI simulates high-pressure scams (e.g., FedEx Customs Blocks, Digital Arrests) with a terrifyingly conversational sense of urgency.
* 🚨 **Live Coaching Intervention:** Dual-LLM parallel processing checks user intent in real-time. If the user yields sensitive data (Aadhaar, Credit Card), the AI instantly seizes control, flashes a red alert, and intervenes with corrective voice coaching.
* 🔒 **Automated Safe-Word Drills:** At the conclusion of a session, the system seamlessly transitions into a guided training exercise to practice the family's secret verification word.
* 📊 **Resistance Scoring:** Quantifiable tracking out of 100 based on time-to-hang-up and sensitive data leaked.
* ⚡ **Low-Latency Voice Architecture:** Pure WebSocket architecture connecting Deepgram STT, Gemini Flash endpoints, and Browser TTS for near-instant conversational flow.

---

## 🏗️ Technical Architecture (Hackathon MVP)

To achieve a natural, high-pressure conversational flow, we abandoned heavy HTTP REST frameworks in favor of a **pure WebSocket streaming architecture**.

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | `Python (asyncio / websockets)` | High-speed async router managing call state and routing audio chunks. |
| **Frontend** | `HTML / Tailwind CSS` | Single Page App (SPA) capturing raw PCM 16-bit audio via `AudioContext`. |
| **STT** | `Deepgram Nova-2` | Streaming WebSockets for ultra-low latency speech-to-text. |
| **LLM / Brain** | `Google Gemini 3.6-Flash` | Parallel API calls for simultaneously generating responses and detecting danger intent. |
| **TTS** | `Web Speech API` | Native browser speech synthesis to entirely eliminate TTS network latency. |

> 💡 **Hackathon Innovation:** To bypass strict 20-request-per-day Free Tier limits on beta endpoints, the orchestrator implements a custom dynamic model failover array (`3.6-flash` ➡️ `3.5-flash-lite` ➡️ `2.5-flash`), instantly failing over on HTTP 429 quota exhaustion to ensure zero downtime.

---

## 🚀 Quick Start Guide

### Prerequisites
* Python 3.10+
* A Deepgram API Key
* A Google Gemini API Key

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/HangUp.git
   cd HangUp
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the `backend/` directory:
   ```env
   GEMINI_API_KEY=your_gemini_key_here
   DEEPGRAM_API_KEY=your_deepgram_key_here
   ```

3. **Install Dependencies:**
   ```bash
   cd backend
   pip install websockets aiohttp python-dotenv
   ```

4. **Launch the Orchestrator:**
   ```bash
   python raw_server.py
   ```

5. **Start the Dashboard:**
   Open `backend/frontend.html` in any modern web browser to access the Family Dashboard and begin a simulation.

---

<div align="center">
  <sub><i>Crafted by <a href="https://www.linkedin.com/in/sanjay-shan">Sanjay Shan</a></i></sub>
</div>