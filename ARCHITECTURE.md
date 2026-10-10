# Architecture: HangUp (Hackathon MVP)

## 🏗️ Core Philosophy
The primary technical hurdle in voice AI is **latency**. To achieve a natural, high-pressure conversational flow suitable for scam simulation, we abandoned traditional REST pipelines and heavy frameworks in favor of a pure, bare-metal **WebSocket streaming architecture**.

## 🧩 Components

1.  **The Client (frontend.html)**
    *   A lightweight SPA built with HTML, JS, and Tailwind CSS.
    *   Captures raw `PCM 16-bit` audio directly from the user's microphone using `AudioContext` and a `ScriptProcessorNode`.
    *   Streams binary audio frames to the Python backend over a secure WebSocket connection.
    *   Handles local Text-to-Speech (TTS) using the native Web Speech API to entirely eliminate TTS network latency and rendering delays.

2.  **The Orchestrator (raw_server.py)**
    *   A pure Python `asyncio` server handling bi-directional WebSocket communication.
    *   Acts as a high-speed router: it ingests binary audio from the Client and instantly forwards it to the Deepgram STT endpoint.
    *   Manages the state of the call (timers, scenario logic, safe-word rotation).

3.  **The Perception Engine (Deepgram)**
    *   Utilizes the `nova-2` model for low-latency, highly accurate Speech-to-Text.
    *   Configured with `endpointing=500` to aggressively detect when the user stops speaking, immediately returning a `speech_final` event to the Python backend.

4.  **The Cognitive Engine (Gemini 3.6-Flash)**
    *   **Dual-Processing Pipeline:** When `speech_final` is triggered, the backend fires *two parallel asynchronous tasks* to the Gemini API:
        1.  **Response Generation:** Generates the scammer's next high-pressure dialogue.
        2.  **Intent Detection:** Analyzes the user's transcript to determine if they surrendered Personally Identifiable Information (PII) or financial details.
    *   **Live Interruption Logic:** If the Intent Detection task returns `True` before the Response Generation task finishes reading, the Response task is instantly cancelled. A "Coach Intervention" payload is sent to the client, seizing control of the frontend UI and TTS to deliver corrective training.

## 🔄 Data Flow (Real-time Simulation)

1.  **Ingest:** Browser Mic ➡️ Raw PCM ➡️ Python Backend ➡️ Deepgram STT.
2.  **Transcribe:** Deepgram ➡️ Transcript JSON ➡️ Python Backend.
3.  **Parallel Compute:** 
    *   *Task A:* Python Backend ➡️ Gemini (Analyze Intent).
    *   *Task B:* Python Backend ➡️ Gemini (Generate Scammer Response).
4.  **Resolution:** 
    *   If *Task A* detects danger: Cancel *Task B*, trigger Coach payload ➡️ Browser TTS.
    *   If *Task A* detects safety: Return *Task B* text ➡️ Browser TTS.

## 🛡️ Defeating API Safety Filters & Rate Limits
Because the AI is simulating a malicious actor, enterprise LLM safety filters routinely block prompt generation (e.g., refusing to "demand an Aadhaar card"). We architected two solutions:
1.  **Semantic Softening:** Prompts are structured as "strict logistics supervisors resolving a discrepancy" rather than "scammers stealing data", successfully evading PII-extraction blockades while maintaining psychological pressure.
2.  **Failover Arrays:** To bypass strict 20-request-per-day Free Tier limits on Gemini endpoints, the orchestrator implements an automatic array fallback loop (`3.6-flash` -> `3.5-flash-lite` -> `2.5-flash`), instantly failing over on HTTP 429 quota exhaustion.
