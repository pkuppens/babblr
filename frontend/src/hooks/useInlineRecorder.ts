import { useState, useRef, useCallback, useEffect } from 'react';

/**
 * State of the inline recorder
 */
export interface InlineRecorderState {
  /** Current status of the recorder */
  status: 'idle' | 'ready' | 'recording' | 'stopped' | 'error';
  /** Recording duration in seconds */
  duration: number;
  /** Recorded audio blob (available when stopped) */
  audioBlob: Blob | null;
  /** Error message if status is 'error' */
  error: string | null;
  /** Audio URL for playback */
  audioUrl: string | null;
  /** Whether microphone permission has been granted */
  permissionGranted: boolean;
}

export interface UseInlineRecorder {
  state: InlineRecorderState;
  /** Pre-initialize microphone (call on component mount) */
  initMicrophone: () => Promise<boolean>;
  /** Start recording immediately (microphone should be pre-initialized) */
  startRecording: () => void;
  /** Stop recording */
  stopRecording: () => void;
  /** Clear recording and return to ready state */
  clearRecording: () => void;
  /** Get analyser for waveform visualization */
  getAnalyser: () => AnalyserNode | null;
  /** Release microphone resources */
  releaseMicrophone: () => void;
}

const MAX_DURATION = 60; // 60 seconds max recording

/**
 * Custom hook for inline audio recording with pre-initialized microphone.
 *
 * Key features:
 * - Pre-initializes microphone on mount to eliminate startup delay
 * - Keeps stream ready for instant recording
 * - Provides waveform analyser for visualization
 */
export function useInlineRecorder(): UseInlineRecorder {
  const [state, setState] = useState<InlineRecorderState>({
    status: 'idle',
    duration: 0,
    audioBlob: null,
    error: null,
    audioUrl: null,
    permissionGranted: false,
  });

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<number | null>(null);
  const startTimeRef = useRef<number>(0);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);

  /**
   * Pre-initialize microphone to eliminate recording delay.
   * Call this when the conversation interface mounts.
   */
  const initMicrophone = useCallback(async (): Promise<boolean> => {
    console.log('[InlineRecorder] Pre-initializing microphone...');

    // Already initialized
    if (streamRef.current && state.permissionGranted) {
      console.log('[InlineRecorder] Microphone already initialized');
      return true;
    }

    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      streamRef.current = stream;

      // Create audio context and analyser for waveform
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 2048;
      analyserRef.current.smoothingTimeConstant = 0.8;

      sourceRef.current = audioContextRef.current.createMediaStreamSource(stream);
      sourceRef.current.connect(analyserRef.current);

      setState(prev => ({
        ...prev,
        status: 'ready',
        permissionGranted: true,
        error: null,
      }));

      console.log('[InlineRecorder] Microphone pre-initialized successfully');
      return true;
    } catch (error) {
      console.error('[InlineRecorder] Failed to initialize microphone:', error);

      let errorMessage = 'Failed to access microphone';
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
          errorMessage =
            'Microphone permission denied. Please allow access in your browser settings.';
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
          errorMessage = 'No microphone found. Please connect a microphone and try again.';
        } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
          errorMessage = 'Microphone is already in use by another application.';
        } else {
          errorMessage = `Microphone error: ${error.message}`;
        }
      }

      setState(prev => ({
        ...prev,
        status: 'error',
        error: errorMessage,
        permissionGranted: false,
      }));

      return false;
    }
  }, [state.permissionGranted]);

  /**
   * Start recording immediately (microphone should already be initialized)
   */
  const startRecording = useCallback(() => {
    console.log('[InlineRecorder] Starting recording...');

    if (!streamRef.current) {
      console.error('[InlineRecorder] No stream available - call initMicrophone first');
      setState(prev => ({
        ...prev,
        status: 'error',
        error: 'Microphone not initialized. Please try again.',
      }));
      return;
    }

    // Clear previous recording
    if (state.audioUrl) {
      URL.revokeObjectURL(state.audioUrl);
    }

    // Reset state for new recording
    setState(prev => ({
      ...prev,
      status: 'recording',
      duration: 0,
      audioBlob: null,
      audioUrl: null,
      error: null,
    }));

    // Create new media recorder
    const mimeType = MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4';
    const mediaRecorder = new MediaRecorder(streamRef.current, { mimeType });
    mediaRecorderRef.current = mediaRecorder;
    chunksRef.current = [];

    mediaRecorder.ondataavailable = event => {
      if (event.data.size > 0) {
        chunksRef.current.push(event.data);
      }
    };

    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(chunksRef.current, { type: mimeType });
      const audioUrl = URL.createObjectURL(audioBlob);

      console.log('[InlineRecorder] Recording stopped, blob size:', audioBlob.size, 'bytes');

      // Clear timer
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }

      setState(prev => ({
        ...prev,
        status: 'stopped',
        audioBlob,
        audioUrl,
      }));
    };

    // Start recording
    mediaRecorder.start(100);
    startTimeRef.current = Date.now();

    // Start duration timer
    timerRef.current = window.setInterval(() => {
      const elapsed = (Date.now() - startTimeRef.current) / 1000;

      setState(prev => ({
        ...prev,
        duration: elapsed,
      }));

      // Auto-stop at max duration
      if (elapsed >= MAX_DURATION) {
        console.log('[InlineRecorder] Max duration reached, auto-stopping');
        mediaRecorder.stop();
      }
    }, 100);

    console.log('[InlineRecorder] Recording started');
  }, [state.audioUrl]);

  /**
   * Stop recording
   */
  const stopRecording = useCallback(() => {
    console.log('[InlineRecorder] Stopping recording...');

    if (mediaRecorderRef.current && state.status === 'recording') {
      mediaRecorderRef.current.stop();
    }
  }, [state.status]);

  /**
   * Clear recording and return to ready state
   */
  const clearRecording = useCallback(() => {
    console.log('[InlineRecorder] Clearing recording');

    if (state.audioUrl) {
      URL.revokeObjectURL(state.audioUrl);
    }

    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    setState(prev => ({
      ...prev,
      status: prev.permissionGranted ? 'ready' : 'idle',
      duration: 0,
      audioBlob: null,
      audioUrl: null,
      error: null,
    }));
  }, [state.audioUrl]);

  /**
   * Release all microphone resources
   */
  const releaseMicrophone = useCallback(() => {
    console.log('[InlineRecorder] Releasing microphone resources');

    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    sourceRef.current = null;
    analyserRef.current = null;

    if (state.audioUrl) {
      URL.revokeObjectURL(state.audioUrl);
    }

    setState({
      status: 'idle',
      duration: 0,
      audioBlob: null,
      error: null,
      audioUrl: null,
      permissionGranted: false,
    });
  }, [state.audioUrl]);

  /**
   * Get analyser for waveform visualization
   */
  const getAnalyser = useCallback(() => analyserRef.current, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close();
      }
    };
  }, []);

  return {
    state,
    initMicrophone,
    startRecording,
    stopRecording,
    clearRecording,
    getAnalyser,
    releaseMicrophone,
  };
}
