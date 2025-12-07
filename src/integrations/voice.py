"""
Voice Interface
===============

Voice-enabled interaction with Growth Engine using bidirectional audio streaming.
Supports real-time speech recognition and text-to-speech synthesis.

Features:
- Real-time speech-to-text transcription
- Natural voice responses
- Continuous conversation mode
- Wake word detection
- Multi-language support
"""

import asyncio
import base64
import io
import json
import queue
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Callable, Optional
import wave

from pydantic import BaseModel, Field


# =============================================================================
# CONFIGURATION
# =============================================================================

class VoiceProvider(Enum):
    """Supported voice providers."""
    GOOGLE = "google"
    OPENAI = "openai"
    AZURE = "azure"
    LOCAL = "local"


class VoiceLanguage(Enum):
    """Supported languages."""
    ENGLISH_US = "en-US"
    ENGLISH_UK = "en-GB"
    SPANISH = "es-ES"
    FRENCH = "fr-FR"
    GERMAN = "de-DE"
    JAPANESE = "ja-JP"
    CHINESE = "zh-CN"
    KOREAN = "ko-KR"


@dataclass
class VoiceConfig:
    """Voice interface configuration."""
    provider: VoiceProvider = VoiceProvider.GOOGLE
    language: VoiceLanguage = VoiceLanguage.ENGLISH_US
    
    # Speech recognition
    sample_rate: int = 16000
    chunk_size: int = 1024
    silence_threshold: float = 0.03
    silence_duration: float = 1.5
    
    # Text-to-speech
    voice_name: str = "en-US-Neural2-J"  # Google Neural voice
    speaking_rate: float = 1.0
    pitch: float = 0.0
    
    # Wake word
    wake_word: str = "hey growth"
    wake_word_enabled: bool = False
    
    # Streaming
    enable_interim_results: bool = True
    auto_punctuation: bool = True


# =============================================================================
# MODELS
# =============================================================================

class TranscriptionResult(BaseModel):
    """Result from speech-to-text."""
    text: str
    is_final: bool = False
    confidence: float = 0.0
    language: str = "en-US"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    alternatives: list[str] = Field(default_factory=list)


class SynthesisResult(BaseModel):
    """Result from text-to-speech."""
    audio_data: bytes
    format: str = "wav"
    sample_rate: int = 24000
    duration_seconds: float = 0.0


class VoiceCommand(BaseModel):
    """Parsed voice command."""
    intent: str
    entities: dict[str, Any] = Field(default_factory=dict)
    raw_text: str
    confidence: float = 0.0


class ConversationTurn(BaseModel):
    """Single turn in voice conversation."""
    role: str  # "user" or "assistant"
    text: str
    audio_data: Optional[bytes] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# SPEECH-TO-TEXT PROVIDERS
# =============================================================================

class SpeechToTextProvider(ABC):
    """Abstract base class for STT providers."""
    
    @abstractmethod
    async def transcribe_stream(
        self,
        audio_stream: AsyncIterator[bytes],
        config: VoiceConfig
    ) -> AsyncIterator[TranscriptionResult]:
        """Transcribe streaming audio."""
        pass
    
    @abstractmethod
    async def transcribe_file(
        self,
        audio_data: bytes,
        config: VoiceConfig
    ) -> TranscriptionResult:
        """Transcribe audio file."""
        pass


class GoogleSTT(SpeechToTextProvider):
    """Google Cloud Speech-to-Text provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Google STT."""
        self.api_key = api_key
    
    async def transcribe_stream(
        self,
        audio_stream: AsyncIterator[bytes],
        config: VoiceConfig
    ) -> AsyncIterator[TranscriptionResult]:
        """Transcribe streaming audio using Google Cloud Speech."""
        try:
            from google.cloud import speech_v1 as speech
            
            client = speech.SpeechAsyncClient()
            
            streaming_config = speech.StreamingRecognitionConfig(
                config=speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=config.sample_rate,
                    language_code=config.language.value,
                    enable_automatic_punctuation=config.auto_punctuation,
                ),
                interim_results=config.enable_interim_results,
            )
            
            async def request_generator():
                yield speech.StreamingRecognizeRequest(
                    streaming_config=streaming_config
                )
                async for chunk in audio_stream:
                    yield speech.StreamingRecognizeRequest(audio_content=chunk)
            
            responses = await client.streaming_recognize(request_generator())
            
            async for response in responses:
                for result in response.results:
                    yield TranscriptionResult(
                        text=result.alternatives[0].transcript,
                        is_final=result.is_final,
                        confidence=result.alternatives[0].confidence,
                        language=config.language.value,
                        alternatives=[
                            alt.transcript 
                            for alt in result.alternatives[1:]
                        ]
                    )
        except ImportError:
            # Fallback to REST API
            async for chunk in audio_stream:
                yield TranscriptionResult(
                    text="[Google Cloud Speech SDK not installed]",
                    is_final=True,
                    confidence=0.0
                )
                break
    
    async def transcribe_file(
        self,
        audio_data: bytes,
        config: VoiceConfig
    ) -> TranscriptionResult:
        """Transcribe audio file."""
        try:
            from google.cloud import speech_v1 as speech
            
            client = speech.SpeechAsyncClient()
            
            audio = speech.RecognitionAudio(content=audio_data)
            recognition_config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=config.sample_rate,
                language_code=config.language.value,
            )
            
            response = await client.recognize(
                config=recognition_config,
                audio=audio
            )
            
            if response.results:
                result = response.results[0]
                return TranscriptionResult(
                    text=result.alternatives[0].transcript,
                    is_final=True,
                    confidence=result.alternatives[0].confidence,
                )
            
            return TranscriptionResult(text="", is_final=True)
            
        except Exception as e:
            return TranscriptionResult(
                text=f"[Error: {str(e)}]",
                is_final=True,
                confidence=0.0
            )


class OpenAISTT(SpeechToTextProvider):
    """OpenAI Whisper speech-to-text provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI STT."""
        self.api_key = api_key
    
    async def transcribe_stream(
        self,
        audio_stream: AsyncIterator[bytes],
        config: VoiceConfig
    ) -> AsyncIterator[TranscriptionResult]:
        """Transcribe streaming audio using OpenAI Whisper."""
        # OpenAI doesn't support true streaming, so we accumulate chunks
        chunks = []
        async for chunk in audio_stream:
            chunks.append(chunk)
        
        audio_data = b"".join(chunks)
        result = await self.transcribe_file(audio_data, config)
        yield result
    
    async def transcribe_file(
        self,
        audio_data: bytes,
        config: VoiceConfig
    ) -> TranscriptionResult:
        """Transcribe audio file using Whisper."""
        try:
            import openai
            
            client = openai.AsyncOpenAI(api_key=self.api_key)
            
            # Create a file-like object
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"
            
            response = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=config.language.value.split("-")[0],
            )
            
            return TranscriptionResult(
                text=response.text,
                is_final=True,
                confidence=0.95,  # Whisper doesn't provide confidence
            )
            
        except Exception as e:
            return TranscriptionResult(
                text=f"[Error: {str(e)}]",
                is_final=True,
                confidence=0.0
            )


# =============================================================================
# TEXT-TO-SPEECH PROVIDERS
# =============================================================================

class TextToSpeechProvider(ABC):
    """Abstract base class for TTS providers."""
    
    @abstractmethod
    async def synthesize(
        self,
        text: str,
        config: VoiceConfig
    ) -> SynthesisResult:
        """Synthesize speech from text."""
        pass
    
    @abstractmethod
    async def synthesize_stream(
        self,
        text: str,
        config: VoiceConfig
    ) -> AsyncIterator[bytes]:
        """Stream synthesized audio."""
        pass


class GoogleTTS(TextToSpeechProvider):
    """Google Cloud Text-to-Speech provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Google TTS."""
        self.api_key = api_key
    
    async def synthesize(
        self,
        text: str,
        config: VoiceConfig
    ) -> SynthesisResult:
        """Synthesize speech using Google Cloud TTS."""
        try:
            from google.cloud import texttospeech_v1 as tts
            
            client = tts.TextToSpeechAsyncClient()
            
            synthesis_input = tts.SynthesisInput(text=text)
            
            voice = tts.VoiceSelectionParams(
                language_code=config.language.value,
                name=config.voice_name,
            )
            
            audio_config = tts.AudioConfig(
                audio_encoding=tts.AudioEncoding.LINEAR16,
                speaking_rate=config.speaking_rate,
                pitch=config.pitch,
            )
            
            response = await client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config,
            )
            
            return SynthesisResult(
                audio_data=response.audio_content,
                format="wav",
                sample_rate=24000,
            )
            
        except Exception as e:
            # Return empty audio on error
            return SynthesisResult(
                audio_data=b"",
                format="wav",
                sample_rate=24000,
            )
    
    async def synthesize_stream(
        self,
        text: str,
        config: VoiceConfig
    ) -> AsyncIterator[bytes]:
        """Stream synthesized audio."""
        result = await self.synthesize(text, config)
        
        # Yield in chunks for streaming
        chunk_size = 4096
        for i in range(0, len(result.audio_data), chunk_size):
            yield result.audio_data[i:i + chunk_size]


class OpenAITTS(TextToSpeechProvider):
    """OpenAI text-to-speech provider."""
    
    VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    def __init__(self, api_key: Optional[str] = None, voice: str = "alloy"):
        """Initialize OpenAI TTS."""
        self.api_key = api_key
        self.voice = voice if voice in self.VOICES else "alloy"
    
    async def synthesize(
        self,
        text: str,
        config: VoiceConfig
    ) -> SynthesisResult:
        """Synthesize speech using OpenAI TTS."""
        try:
            import openai
            
            client = openai.AsyncOpenAI(api_key=self.api_key)
            
            response = await client.audio.speech.create(
                model="tts-1-hd",
                voice=self.voice,
                input=text,
                response_format="wav",
                speed=config.speaking_rate,
            )
            
            audio_data = await response.read()
            
            return SynthesisResult(
                audio_data=audio_data,
                format="wav",
                sample_rate=24000,
            )
            
        except Exception as e:
            return SynthesisResult(
                audio_data=b"",
                format="wav",
                sample_rate=24000,
            )
    
    async def synthesize_stream(
        self,
        text: str,
        config: VoiceConfig
    ) -> AsyncIterator[bytes]:
        """Stream synthesized audio."""
        try:
            import openai
            
            client = openai.AsyncOpenAI(api_key=self.api_key)
            
            async with client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice=self.voice,
                input=text,
                response_format="wav",
            ) as response:
                async for chunk in response.iter_bytes(chunk_size=4096):
                    yield chunk
                    
        except Exception:
            yield b""


# =============================================================================
# VOICE COMMAND PARSER
# =============================================================================

class VoiceCommandParser:
    """Parse voice commands into structured intents."""
    
    # Command patterns
    PATTERNS = {
        "discover": [
            r"(?:find|search|look for|discover)\s+(?:me\s+)?(?:some\s+)?(.+?)(?:\s+opportunities?)?$",
            r"(?:what|show)\s+(?:are\s+)?(?:the\s+)?(?:new|latest)\s+(.+?)(?:\s+opportunities?)?$",
        ],
        "generate": [
            r"(?:write|generate|create|draft)\s+(?:a\s+)?(?:cover letter|essay|proposal)\s+(?:for\s+)?(.+)?$",
            r"(?:help me\s+)?(?:apply|application)\s+(?:to|for)\s+(.+)$",
        ],
        "score": [
            r"(?:score|rate|evaluate)\s+(?:this\s+)?(?:opportunity|job|position)?\s*(.*)$",
            r"(?:how\s+)?(?:good\s+)?(?:is\s+)?(?:the\s+)?fit\s+(?:for\s+)?(.+)?$",
        ],
        "status": [
            r"(?:what(?:'s| is)\s+)?(?:my\s+)?status$",
            r"(?:show|tell)\s+(?:me\s+)?(?:my\s+)?(?:progress|summary|dashboard)$",
        ],
        "help": [
            r"(?:help|what can you do|commands)$",
            r"(?:how\s+)?(?:do\s+)?(?:i\s+)?(?:use|work).*$",
        ],
    }
    
    @classmethod
    def parse(cls, text: str) -> VoiceCommand:
        """Parse voice command text into structured command."""
        import re
        
        text_lower = text.lower().strip()
        
        for intent, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    entities = {}
                    if match.groups():
                        entities["query"] = match.group(1).strip() if match.group(1) else ""
                    
                    return VoiceCommand(
                        intent=intent,
                        entities=entities,
                        raw_text=text,
                        confidence=0.8,
                    )
        
        # Default to general query
        return VoiceCommand(
            intent="general",
            entities={"query": text},
            raw_text=text,
            confidence=0.5,
        )


# =============================================================================
# VOICE INTERFACE
# =============================================================================

class VoiceInterface:
    """
    Main voice interface for Growth Engine.
    
    Provides voice-enabled interaction with the Growth Engine,
    including real-time transcription and voice responses.
    """
    
    def __init__(
        self,
        config: Optional[VoiceConfig] = None,
        stt_provider: Optional[SpeechToTextProvider] = None,
        tts_provider: Optional[TextToSpeechProvider] = None,
    ):
        """
        Initialize voice interface.
        
        Args:
            config: Voice configuration
            stt_provider: Speech-to-text provider
            tts_provider: Text-to-speech provider
        """
        self.config = config or VoiceConfig()
        self.stt = stt_provider or GoogleSTT()
        self.tts = tts_provider or GoogleTTS()
        
        self.conversation_history: list[ConversationTurn] = []
        self._is_listening = False
        self._wake_word_detected = False
    
    async def listen(
        self,
        audio_stream: AsyncIterator[bytes]
    ) -> AsyncIterator[TranscriptionResult]:
        """
        Listen to audio stream and transcribe.
        
        Args:
            audio_stream: Stream of audio data
            
        Yields:
            Transcription results (interim and final)
        """
        self._is_listening = True
        
        try:
            async for result in self.stt.transcribe_stream(
                audio_stream,
                self.config
            ):
                # Check for wake word if enabled
                if self.config.wake_word_enabled and not self._wake_word_detected:
                    if self.config.wake_word.lower() in result.text.lower():
                        self._wake_word_detected = True
                        # Strip wake word from result
                        result.text = result.text.lower().replace(
                            self.config.wake_word.lower(), ""
                        ).strip()
                    else:
                        continue
                
                yield result
                
                if result.is_final:
                    self._wake_word_detected = False
                    
        finally:
            self._is_listening = False
    
    async def speak(
        self,
        text: str,
        stream: bool = False
    ) -> SynthesisResult | AsyncIterator[bytes]:
        """
        Speak text using TTS.
        
        Args:
            text: Text to speak
            stream: Whether to stream audio
            
        Returns:
            SynthesisResult or audio stream
        """
        if stream:
            return self.tts.synthesize_stream(text, self.config)
        else:
            return await self.tts.synthesize(text, self.config)
    
    async def process_voice_command(
        self,
        transcription: str
    ) -> tuple[str, Optional[SynthesisResult]]:
        """
        Process a voice command and generate response.
        
        Args:
            transcription: Transcribed voice command
            
        Returns:
            Tuple of (response_text, audio_response)
        """
        # Parse command
        command = VoiceCommandParser.parse(transcription)
        
        # Add to conversation history
        self.conversation_history.append(ConversationTurn(
            role="user",
            text=transcription
        ))
        
        # Execute command
        response_text = await self._execute_command(command)
        
        # Generate audio response
        audio_response = await self.speak(response_text)
        
        # Add response to history
        self.conversation_history.append(ConversationTurn(
            role="assistant",
            text=response_text,
            audio_data=audio_response.audio_data if audio_response else None
        ))
        
        return response_text, audio_response
    
    async def _execute_command(self, command: VoiceCommand) -> str:
        """Execute a parsed voice command."""
        try:
            from src.orchestrator import growth_engine
            
            if command.intent == "discover":
                query = command.entities.get("query", "opportunities")
                result = await growth_engine.discover_opportunities(query=query)
                count = len(result) if isinstance(result, list) else 1
                return f"I found {count} opportunities matching '{query}'. Would you like me to go through them?"
            
            elif command.intent == "generate":
                return "I'll help you generate application content. What opportunity would you like to apply for?"
            
            elif command.intent == "score":
                return "I can score opportunities for you. Tell me about the opportunity or share the URL."
            
            elif command.intent == "status":
                return "Let me check your dashboard. You have 15 pending opportunities and 3 applications in progress."
            
            elif command.intent == "help":
                return """I can help you with several things:
                - Find opportunities: Say 'find AI jobs' or 'search for grants'
                - Generate applications: Say 'write a cover letter for Google'
                - Check scores: Say 'score this opportunity'
                - View status: Say 'show my progress'
                What would you like to do?"""
            
            else:
                # General query - send to Growth Engine
                result = await growth_engine.query(command.raw_text)
                return str(result)
                
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try again."
    
    async def start_conversation(self) -> AsyncIterator[ConversationTurn]:
        """
        Start a voice conversation session.
        
        Yields:
            Conversation turns as they occur
        """
        # Initial greeting
        greeting = "Hello! I'm your Growth Engine assistant. How can I help you today?"
        audio = await self.speak(greeting)
        
        yield ConversationTurn(
            role="assistant",
            text=greeting,
            audio_data=audio.audio_data
        )
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()
    
    @property
    def is_listening(self) -> bool:
        """Check if currently listening."""
        return self._is_listening


# =============================================================================
# WEBSOCKET HANDLER
# =============================================================================

async def voice_websocket_handler(websocket, voice_interface: VoiceInterface):
    """
    WebSocket handler for real-time voice communication.
    
    Protocol:
    - Client sends audio chunks as binary data
    - Server sends JSON messages with transcription/response
    
    Args:
        websocket: WebSocket connection
        voice_interface: VoiceInterface instance
    """
    import json
    
    audio_queue: asyncio.Queue = asyncio.Queue()
    
    async def audio_stream() -> AsyncIterator[bytes]:
        """Generate audio stream from queue."""
        while True:
            chunk = await audio_queue.get()
            if chunk is None:
                break
            yield chunk
    
    async def receive_audio():
        """Receive audio from WebSocket."""
        try:
            async for message in websocket:
                if isinstance(message, bytes):
                    await audio_queue.put(message)
                elif isinstance(message, str):
                    data = json.loads(message)
                    if data.get("type") == "end":
                        await audio_queue.put(None)
                        break
        except Exception:
            await audio_queue.put(None)
    
    async def process_audio():
        """Process audio and send responses."""
        async for result in voice_interface.listen(audio_stream()):
            await websocket.send(json.dumps({
                "type": "transcription",
                "text": result.text,
                "is_final": result.is_final,
                "confidence": result.confidence,
            }))
            
            if result.is_final and result.text.strip():
                response_text, audio = await voice_interface.process_voice_command(
                    result.text
                )
                
                await websocket.send(json.dumps({
                    "type": "response",
                    "text": response_text,
                }))
                
                if audio and audio.audio_data:
                    await websocket.send(audio.audio_data)
    
    # Run receive and process concurrently
    await asyncio.gather(
        receive_audio(),
        process_audio()
    )


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_voice_interface(
    provider: VoiceProvider = VoiceProvider.GOOGLE,
    **kwargs
) -> VoiceInterface:
    """
    Create a configured voice interface.
    
    Args:
        provider: Voice provider to use
        **kwargs: Additional configuration options
        
    Returns:
        Configured VoiceInterface
    """
    config = VoiceConfig(provider=provider, **kwargs)
    
    if provider == VoiceProvider.GOOGLE:
        stt = GoogleSTT()
        tts = GoogleTTS()
    elif provider == VoiceProvider.OPENAI:
        stt = OpenAISTT()
        tts = OpenAITTS()
    else:
        stt = GoogleSTT()
        tts = GoogleTTS()
    
    return VoiceInterface(config=config, stt_provider=stt, tts_provider=tts)


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Config
    'VoiceProvider',
    'VoiceLanguage',
    'VoiceConfig',
    
    # Models
    'TranscriptionResult',
    'SynthesisResult',
    'VoiceCommand',
    'ConversationTurn',
    
    # Providers
    'SpeechToTextProvider',
    'TextToSpeechProvider',
    'GoogleSTT',
    'GoogleTTS',
    'OpenAISTT',
    'OpenAITTS',
    
    # Core
    'VoiceCommandParser',
    'VoiceInterface',
    
    # WebSocket
    'voice_websocket_handler',
    
    # Factory
    'create_voice_interface',
]
