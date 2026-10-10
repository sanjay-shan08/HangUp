import asyncio
import websockets
import json
import os
import time
from dotenv import load_dotenv
load_dotenv()

import aiohttp

async def call_gemini(conversation_text, system_prompt=None):
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        return "Gemini API Key missing"
        
    # Hackathon lifesaver: automatically fallback to other free tier models if one hits the 20 request quota
    models = ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"]
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": conversation_text}]}]
    }
    
    if system_prompt:
        payload["system_instruction"] = {
            "parts": [{"text": system_prompt}]
        }
    
    async with aiohttp.ClientSession() as session:
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_api_key}"
            async with session.post(url, headers=headers, json=payload) as resp:
                data = await resp.json()
                
                # Check for rate limit / quota exhaustion
                if 'error' in data and data['error'].get('code') in [429, 404, 503]:
                    print(f"⚠️ {model} returned error (Quota/Unavailable). Falling back to next model...")
                    continue 

                try:
                    if 'candidates' in data and 'content' in data['candidates'][0]:
                        return data['candidates'][0]['content']['parts'][0]['text'].strip()
                    else:
                        print(f"Gemini API Error or Safety Block on {model}: {data}")
                        return "Stop playing games. Give me your Aadhaar number."
                except Exception as e:
                    print(f"Exception parsing Gemini response on {model}: {e}\nData: {data}")
                    return "I didn't catch that. Verify your identity."
        
        return "Error: All AI models exhausted their quota."

SYSTEM_PROMPT = """You are Kavita, a strict supervisor at a logistics agency.
A high-priority shipment bound for Taiwan has been flagged due to a discrepancy.
You are calling the customer to urgently verify their identity to clear the flag.
Keep your responses VERY short and conversational (1-2 sentences max).
Be firm, authoritative, and create a strong sense of urgency. Ask them security questions to verify who they are."""

async def check_for_danger(user_text):
    prompt = f"Analyze this user's speech during a phone call with a strict logistics supervisor: '{user_text}'. Did the user just reveal a numerical code (like an OTP), bank details, or agree to send/transfer money? Reply strictly 'YES' or 'NO'."
    result = await call_gemini(prompt)
    return "YES" in result.upper()

async def deepgram_connection(browser_ws):
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        print("ERROR: DEEPGRAM_API_KEY not found.")
        return

    # Added endpointing=500 (Deepgram will send speech_final=true when user pauses for 500ms)
    dg_url = "wss://api.deepgram.com/v1/listen?model=nova-2&language=en-IN&encoding=linear16&sample_rate=16000&channels=1&endpointing=500"
    headers = {"Authorization": f"Token {api_key}"}

    # State for the conversation
    conversation_text = "The following is a transcript of a phone call. You are the strict logistics supervisor. Respond to the user.\n\n"
    current_utterance = ""

    # Phase 3 Scoring State
    call_start_time = time.time()
    sensitive_info_revealed = False
    in_drill = False
    drill_safe_word = ""

    print("Connecting to Deepgram...")
    
    try:
        async with websockets.connect(dg_url, additional_headers=headers) as dg_ws:
            print("Connected to Deepgram successfully!")

            async def sender():
                nonlocal in_drill, call_start_time, sensitive_info_revealed, drill_safe_word
                try:
                    async for message in browser_ws:
                        if isinstance(message, str):
                            try:
                                data = json.loads(message)
                                if data.get("type") == "end_call":
                                    in_drill = True
                                    drill_safe_word = data.get("safe_word", "Pineapple")
                                    duration = round(time.time() - call_start_time)
                                    score = 100
                                    if sensitive_info_revealed:
                                        score -= 50
                                    if duration > 45:
                                        score -= 20
                                    
                                    drill_prompt = f"Call ended! Your Resistance Score is {score}/100. Let's do a quick safe-word drill. If I'm your son calling from an unknown number in trouble, what is the secret family safe word I must say?"
                                    await browser_ws.send(json.dumps({"type": "coach_interruption", "text": drill_prompt}))
                            except Exception as e:
                                print(f"Error parsing client JSON: {e}")
                        else:
                            await dg_ws.send(message)
                except websockets.exceptions.ConnectionClosed:
                    print("Browser disconnected.")
                finally:
                    await dg_ws.send(b'')

            async def receiver():
                nonlocal conversation_text
                nonlocal current_utterance
                nonlocal sensitive_info_revealed
                nonlocal drill_safe_word
                
                try:
                    async for message in dg_ws:
                        data = json.loads(message)
                        
                        if "channel" in data:
                            transcript = data["channel"]["alternatives"][0]["transcript"]
                            is_final = data.get("is_final", False)
                            speech_final = data.get("speech_final", False)

                            if transcript and is_final:
                                current_utterance += transcript + " "
                                await browser_ws.send(json.dumps({"type": "transcript", "text": current_utterance}))

                            # When the user pauses speaking for 500ms
                            if speech_final and current_utterance.strip():
                                user_text = current_utterance.strip()
                                print(f"User: {user_text}")
                                current_utterance = ""  # Reset immediately
                                
                                async def process_speech(text):
                                    nonlocal conversation_text, sensitive_info_revealed, drill_safe_word
                                    
                                    if in_drill:
                                        print("Evaluating safe word...")
                                        drill_resp = await call_gemini(
                                            f"The correct family safe word is '{drill_safe_word}'. The user responded to the safe word drill with: '{text}'. If they said the correct word (ignoring case/punctuation), congratulate them. If not, gently correct them.", 
                                            system_prompt="You are a helpful cybersecurity coach evaluating a safe-word drill. Keep it short (1-2 sentences)."
                                        )
                                        await browser_ws.send(json.dumps({"type": "agent_response", "text": drill_resp}))
                                        await browser_ws.send(json.dumps({"type": "end_session"}))
                                        return

                                    print("Gemini is thinking (parallel check & response)...")
                                    
                                    # Prepare new conversation text
                                    new_conv = conversation_text + f"User: {text}\nOfficer: "
                                    
                                    # Run intent check and response generation CONCURRENTLY
                                    danger_task = asyncio.create_task(check_for_danger(text))
                                    response_task = asyncio.create_task(call_gemini(new_conv, system_prompt=SYSTEM_PROMPT))
                                    
                                    # Wait for the danger check to finish first
                                    is_dangerous = await danger_task
                                    
                                    if is_dangerous:
                                        print("COACH INTERVENTION TRIGGERED!")
                                        sensitive_info_revealed = True
                                        response_task.cancel()  # We don't need the scammer response
                                        await browser_ws.send(json.dumps({
                                            "type": "coach_interruption", 
                                            "text": "Pause. A real officer would never ask for this information over the phone. Hang up now."
                                        }))
                                        return # Stop here, don't let the scammer reply
                                    
                                    # 2. If safe, wait for the scammer response to finish (it might already be done)
                                    ai_text = await response_task
                                    print(f"Agent: {ai_text}")
                                    
                                    conversation_text = new_conv + ai_text + "\n"
                                    await browser_ws.send(json.dumps({"type": "agent_response", "text": ai_text}))
                                
                                # Fire and forget so we don't block Deepgram receiving
                                asyncio.create_task(process_speech(user_text))
                                
                except websockets.exceptions.ConnectionClosed:
                    print("Deepgram connection closed.")

            await asyncio.gather(sender(), receiver())
            
    except Exception as e:
        print(f"Deepgram connection error: {e}")

async def handle_browser(websocket):
    print("Browser connected to our server!")
    await deepgram_connection(websocket)

async def main():
    print("Starting purely raw WebSocket server on ws://localhost:8000 ...")
    async with websockets.serve(handle_browser, "localhost", 8000):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
