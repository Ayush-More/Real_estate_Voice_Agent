#
# Real Estate Voice Agent — Phase 1 (Local Testing)
#
# Pipeline: Microphone → Deepgram STT → Gemini LLM → Cartesia TTS → Speaker
# Transport: SmallWebRTC (browser mic/speaker via custom frontend)
#
# Run:
#   cd server
#   uv sync
#   uv run bot.py
#

import os
import sys
from pathlib import Path

# Windows consoles default to cp1252; Pipecat's startup banner uses Unicode.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from config.prompts import REAL_ESTATE_GREETING_TRIGGER, REAL_ESTATE_SYSTEM_PROMPT
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.google.llm import GoogleLLMService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.workers.runner import WorkerRunner

# Load API keys from server/.env
load_dotenv(override=True)

# Paths for serving the custom test frontend
SERVER_DIR = Path(__file__).resolve().parent
CLIENT_DIR = SERVER_DIR.parent / "client"


def _mount_custom_frontend() -> None:
    """Serve our custom start/stop UI instead of the default Pipecat prebuilt page."""
    from pipecat.runner.run import app

    # Static assets (CSS, JS)
    app.mount("/assets", StaticFiles(directory=str(CLIENT_DIR)), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        return FileResponse(CLIENT_DIR / "index.html")


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments) -> None:
    """Build and run the voice agent pipeline for one browser session."""

    logger.info("Starting Real Estate Voice Agent session")

    # --- Speech-to-Text: converts microphone audio to text ---
    stt = DeepgramSTTService(api_key=os.environ["DEEPGRAM_API_KEY"])

    # --- LLM: Gemini generates salesperson responses ---
    llm = GoogleLLMService(
        api_key=os.environ["GOOGLE_API_KEY"],
        settings=GoogleLLMService.Settings(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            system_instruction=REAL_ESTATE_SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=1024,
        ),
    )

    # --- Text-to-Speech: converts agent text to natural voice ---
    tts = CartesiaTTSService(
        api_key=os.environ["CARTESIA_API_KEY"],
        settings=CartesiaTTSService.Settings(
            voice=os.getenv(
                "CARTESIA_VOICE_ID",
                "71a7ad14-091c-4e8e-a314-022ece01c121",  # Friendly professional voice
            ),
        ),
    )

    # Conversation memory + voice activity detection for turn-taking
    context = LLMContext()
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=SileroVADAnalyzer(),
        ),
    )

    # --- Pipeline: audio flows through each processor in order ---
    pipeline = Pipeline(
        [
            transport.input(),       # 1. Receive audio from browser mic
            stt,                     # 2. Transcribe speech to text
            user_aggregator,         # 3. Aggregate user message + VAD
            llm,                     # 4. Generate agent response
            tts,                     # 5. Synthesize speech
            transport.output(),      # 6. Play audio in browser speaker
            assistant_aggregator,    # 7. Track assistant messages in context
        ]
    )

    worker = PipelineWorker(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
    )

    # When the browser client is ready, kick off the opening greeting
    @worker.rtvi.event_handler("on_client_ready")
    async def on_client_ready(_rtvi):
        context.add_message({"role": "developer", "content": REAL_ESTATE_GREETING_TRIGGER})
        await worker.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_connected")
    async def on_client_connected(_transport, _client):
        logger.info("Client connected — conversation started")

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(_transport, _client):
        logger.info("Client disconnected — cleaning up session")
        await worker.cancel()

    runner = WorkerRunner(handle_sigint=False)
    await runner.add_workers(worker)
    await runner.run()


async def bot(runner_args: RunnerArguments):
    """Main entry point called by the Pipecat development runner."""

    # WebRTC transport: browser mic/speaker (works on Windows)
    transport_params = {
        "webrtc": lambda: TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
        ),
    }

    transport = await create_transport(runner_args, transport_params)
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    _mount_custom_frontend()

    from pipecat.runner.run import main

    main()
