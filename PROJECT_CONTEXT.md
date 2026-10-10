# Project Context: HangUp

## 🧠 Project Memory
HangUp is an AI-driven scam inoculation coach designed for Indian seniors. It aims to proactively protect vulnerable individuals from digital arrest, fake bank officer, and UPI refund scams by letting them safely rehearse a scam call with an AI agent. 
Unlike reactive spam filters or enterprise-focused vishing simulators, HangUp is a consumer-first, zero-install solution that reaches users via standard phone calls or WhatsApp. The core innovation is the **live hang-up coach**, which interrupts the user mid-call if they exhibit dangerous behaviors (e.g., sharing an OTP or agreeing to transfer money).

## 🛠️ Tech Stack
*   **Frontend (Dashboard):** Next.js (React), Tailwind CSS
*   **Backend (Orchestration):** Python (FastAPI) - Chosen for excellent WebSocket support and AI library ecosystem.
*   **Telephony Gateway:** Twilio (Programmable Voice)
*   **Speech-to-Text (STT):** Deepgram (Low latency, good regional accent support)
*   **LLM (Intelligence):** Gemini 1.5 Pro (or GPT-4o) - Handles persona and intent detection.
*   **Text-to-Speech (TTS):** ElevenLabs (For realistic scammer emotion) or Azure/Bhashini (for regional languages).
*   **Database:** Supabase (PostgreSQL) - For storing session data, scores, and user profiles.

## 🌊 Core Flows
1.  **Call Initiation Flow:** Family member enters details on the dashboard -> Backend triggers Twilio -> Twilio calls the target user.
2.  **Conversational Loop Flow:** Twilio streams audio to Backend (WebSocket) -> Backend sends to STT -> Text sent to LLM -> LLM generates response text -> Text sent to TTS -> Audio streamed back to Twilio.
3.  **Intervention (Coaching) Flow:** LLM detects dangerous intent (e.g., "OTP detected") -> Backend pauses the main TTS stream -> Backend injects pre-recorded or synthesized "Coach" audio ("Pause. A real officer...") -> Resumes or ends scenario.
4.  **Debrief Flow:** Call transitions to a safe-word drill -> Call ends -> Backend calculates Resistance Score -> Dashboard updates via DB listener.

## 📦 Key Dependencies (Planned)
*   `fastapi`, `uvicorn`, `websockets` (Backend framework)
*   `twilio` (Telephony API client)
*   `deepgram-sdk` (STT client)
*   `google-genai` or `openai` (LLM client)
*   `elevenlabs` (TTS client)
*   `supabase` (Database client)
