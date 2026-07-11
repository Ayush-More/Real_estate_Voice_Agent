/**
 * Real Estate Voice Agent — Frontend Controller
 *
 * Uses Pipecat's SmallWebRTCTransport to connect the browser microphone/speakers
 * to the Python bot server. The user can start and stop conversations from here.
 */

import { PipecatClient } from "https://cdn.jsdelivr.net/npm/@pipecat-ai/client-js@1.2.0/+esm";
import { SmallWebRTCTransport } from "https://cdn.jsdelivr.net/npm/@pipecat-ai/small-webrtc-transport@1.2.0/+esm";

// --- DOM elements ---
const startBtn = document.getElementById("start-btn");
const stopBtn = document.getElementById("stop-btn");
const statusDot = document.getElementById("status-dot");
const statusText = document.getElementById("status-text");
const statusDetail = document.getElementById("status-detail");
const transcriptEl = document.getElementById("transcript");

// Pipecat client instance (created on first connect)
let pcClient = null;
let remoteAudioEl = null;
let remoteAudioContext = null;

/** Update the UI status indicator */
function setStatus(state, text, detail = "") {
  statusDot.className = `status-dot ${state}`;
  statusText.textContent = text;
  if (detail) statusDetail.textContent = detail;
}

/** Append a line to the live transcript panel */
function appendTranscript(speaker, text) {
  // Remove placeholder on first message
  const placeholder = transcriptEl.querySelector(".transcript-placeholder");
  if (placeholder) placeholder.remove();

  const line = document.createElement("p");
  line.className = `transcript-line ${speaker}`;
  line.innerHTML = `<strong>${speaker === "user" ? "You" : "Agent"}:</strong> ${text}`;
  transcriptEl.appendChild(line);
  transcriptEl.scrollTop = transcriptEl.scrollHeight;
}

/** Clear transcript when starting a new session */
function clearTranscript() {
  transcriptEl.innerHTML =
    '<p class="transcript-placeholder">Transcript will appear here during the conversation…</p>';
}

function ensureRemoteAudioPlayback() {
  if (!remoteAudioEl) {
    remoteAudioEl = document.createElement("audio");
    remoteAudioEl.autoplay = true;
    remoteAudioEl.playsInline = true;
    remoteAudioEl.setAttribute("playsinline", "true");
    remoteAudioEl.volume = 1.0;
    document.body.appendChild(remoteAudioEl);
  }

  if (!remoteAudioContext) {
    remoteAudioContext = new (window.AudioContext || window.webkitAudioContext)();
  }

  if (remoteAudioContext.state === "suspended") {
    remoteAudioContext.resume().catch((err) => {
      console.warn("AudioContext resume failed:", err);
    });
  }
}

function attachRemoteAudioTrack(track) {
  if (!track || track.kind !== "audio") return;

  ensureRemoteAudioPlayback();

  const stream = new MediaStream();
  stream.addTrack(track);

  remoteAudioEl.srcObject = stream;
  remoteAudioEl.muted = false;
  remoteAudioEl.volume = 1.0;

  const playPromise = remoteAudioEl.play();
  if (playPromise) {
    playPromise.catch((err) => {
      console.warn("Remote audio play failed; retrying on next interaction:", err);
      document.addEventListener(
        "click",
        () => remoteAudioEl.play().catch(() => {}),
        { once: true }
      );
    });
  }
}

/** Create and configure the Pipecat client */
function createClient() {
  return new PipecatClient({
    transport: new SmallWebRTCTransport({
      // STUN server helps establish WebRTC connection on local networks
      iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
    }),
    enableCam: false,  // No camera needed for voice-only agent
    enableMic: true,   // Use laptop microphone
    callbacks: {
      // --- Connection lifecycle events ---
      onConnected: () => {
        ensureRemoteAudioPlayback();
        setStatus("connected", "Connected — agent is listening", "Speak naturally. The agent will respond when you pause.");
        startBtn.disabled = true;
        stopBtn.disabled = false;
      },
      onDisconnected: () => {
        if (remoteAudioEl) {
          remoteAudioEl.pause();
          remoteAudioEl.srcObject = null;
        }
        setStatus("idle", "Idle — ready to connect", "Click Start Conversation to begin a new session.");
        startBtn.disabled = false;
        stopBtn.disabled = true;
      },
      onError: (error) => {
        console.error("Pipecat error:", error);
        setStatus("error", "Error occurred", error?.message || "Something went wrong. Try again.");
        startBtn.disabled = false;
        stopBtn.disabled = true;
      },

      onTrackStarted: (track, participant) => {
        console.log("TRACK STARTED:", track.kind, track.readyState, track.muted, participant);
        if (participant?.local || track.kind !== "audio") return;
        attachRemoteAudioTrack(track);
      },
      // --- Transcript events (when bot/user speaks) ---
      onUserTranscript: (data) => {
        if (data?.text) appendTranscript("user", data.text);
      },
      onBotTranscript: (data) => {
        if (data?.text) appendTranscript("agent", data.text);
      },
    },
  });
}

/** Start a new voice conversation with the agent */
async function startConversation() {
  try {
    setStatus("connecting", "Connecting…", "Requesting microphone access and starting the agent.");
    startBtn.disabled = true;
    clearTranscript();

    pcClient = createClient();

    // Connect via WebRTC to the Python server's /api/offer endpoint
    await pcClient.connect({
      webrtcUrl: "/api/offer",
    });
  } catch (err) {
    console.error("Failed to start:", err);
    setStatus("error", "Failed to connect", err.message || "Check that the server is running.");
    startBtn.disabled = false;
    stopBtn.disabled = true;
  }
}

/** Stop the current conversation and release resources */
async function stopConversation() {
  try {
    setStatus("disconnecting", "Stopping…", "Ending the conversation.");
    stopBtn.disabled = true;

    if (pcClient) {
      await pcClient.disconnect();
      pcClient = null;
    }
  } catch (err) {
    console.error("Failed to stop:", err);
    setStatus("error", "Error while stopping", err.message);
  } finally {
    startBtn.disabled = false;
    stopBtn.disabled = true;
    setStatus("idle", "Idle — ready to connect");
  }
}

// Wire up button click handlers
startBtn.addEventListener("click", startConversation);
stopBtn.addEventListener("click", stopConversation);
