import { useState, useRef, useCallback, useEffect } from 'react';

/**
 * State of the audio recorder
 */
export interface AudioRecorderState {
  /** Current status of the recorder */
  status: 'idle' | 'recording' | 'stopped' | 'error';
  /** Recording duration in seconds */
  duration: number;
  /** Recorded audio blob (available when stopped) */
  audioBlob: Blob | null;
  /** Error message if status is 'error' */
  error: string | null;
  /** Audio URL for playback */
  audioUrl: string | null;
}

/**
 * Return type of useAudioRecorder hook
 */
export interface UseAudioRecorder {
  /** Current state of the recorder */
  state: AudioRecorderState;
  /** Start recording audio */
  startRecording: () => Promise<void>;
  /** Stop recording audio */
  stopRecording: () => void;
  /** Clear the current recording and reset state */
  clearRecording: () => void;
  /** Get audio analyser for waveform visualization */
  getAnalyser: () => AnalyserNode | null;
}

const MAX_DURATION = 60; // 60 seconds max recording

/**
 * Custom hook for audio recording using MediaRecorder API
 * 
 * Features:
 * - Records audio from user's microphone
 * - Tracks recording duration
 * - Auto-stops at maximum duration (60 seconds)
 * - Provides audio analyser for waveform visualization
 * - Handles errors and permissions
 * 
 * @returns {UseAudioRecorder} Audio recorder interface
 * 
 * @example
 * ```tsx
 * const { state, startRecording, stopRecording, clearRecording } = useAudioRecorder();
 * 
 * // Start recording
 * await startRecording();
 * 
 * // Stop recording
 * stopRecording();
 * 
 * // Access recorded audio
 * if (state.audioBlob) {
 *   // Send to server or play back
 * }
 * ```
 */
export function useAudioRecorder(): UseAudioRecorder {
  const [state, setState] = useState<AudioRecorderState>({
    status: 'idle',
    duration: 0,
    audioBlob: null,
    error: null,
    audioUrl: null,
  });

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<number | null>(null);
  const startTimeRef = useRef<number>(0);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);

  /**
   * Clean up resources (stream, timer, audio context)
   */
  const cleanup = useCallback(() => {
    // Stop all tracks in the media stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    // Clear timer
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    // Close audio context
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    analyserRef.current = null;
  }, []);

  /**
   * Start recording audio from the user's microphone
   */
  const startRecording = useCallback(async () => {
    console.log('[AudioRecorder] Starting audio recording');
    
    try {
      // Reset state
      setState((prev) => ({
        ...prev,
        status: 'recording',
        duration: 0,
        audioBlob: null,
        error: null,
        audioUrl: null,
      }));

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      });
      streamRef.current = stream;

      // Create audio context and analyser for waveform
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 2048;
      analyserRef.current.smoothingTimeConstant = 0.8;
      
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);

      // Initialize media recorder
      const mimeType = MediaRecorder.isTypeSupported('audio/webm')
        ? 'audio/webm'
        : 'audio/mp4';
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType,
      });
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      // Handle data available event
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      // Handle stop event
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(chunksRef.current, { type: mimeType });
        const audioUrl = URL.createObjectURL(audioBlob);
        
        console.log('[AudioRecorder] Recording stopped, blob size:', audioBlob.size, 'bytes');
        
        setState((prev) => ({
          ...prev,
          status: 'stopped',
          audioBlob,
          audioUrl,
        }));

        cleanup();
      };

      // Start recording
      mediaRecorder.start(100); // Collect data every 100ms
      startTimeRef.current = Date.now();

      // Start duration timer
      timerRef.current = window.setInterval(() => {
        const elapsed = (Date.now() - startTimeRef.current) / 1000;
        
        setState((prev) => ({
          ...prev,
          duration: elapsed,
        }));

        // Auto-stop at max duration
        if (elapsed >= MAX_DURATION) {
          console.log('[AudioRecorder] Max duration reached, auto-stopping recording');
          mediaRecorder.stop();
        }
      }, 100);

      console.log('[AudioRecorder] Recording started successfully');
    } catch (error) {
      console.error('[AudioRecorder] Failed to start recording:', error);
      
      let errorMessage = 'Failed to access microphone';
      
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
          errorMessage = 'Microphone permission denied. Please allow access in your browser settings.';
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
          errorMessage = 'No microphone found. Please connect a microphone and try again.';
        } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
          errorMessage = 'Microphone is already in use by another application.';
        } else {
          errorMessage = `Microphone error: ${error.message}`;
        }
      }

      setState((prev) => ({
        ...prev,
        status: 'error',
        error: errorMessage,
      }));

      cleanup();
    }
  }, [cleanup]);

  /**
   * Stop recording audio
   */
  const stopRecording = useCallback(() => {
    console.log('[AudioRecorder] Stopping audio recording');
    
    if (mediaRecorderRef.current && state.status === 'recording') {
      mediaRecorderRef.current.stop();
    }
  }, [state.status]);

  /**
   * Clear the current recording and reset to idle state
   */
  const clearRecording = useCallback(() => {
    console.log('[AudioRecorder] Clearing recording');
    
    // Revoke the object URL to free memory
    if (state.audioUrl) {
      URL.revokeObjectURL(state.audioUrl);
    }

    setState({
      status: 'idle',
      duration: 0,
      audioBlob: null,
      error: null,
      audioUrl: null,
    });

    cleanup();
  }, [state.audioUrl, cleanup]);

  /**
   * Get the analyser node for waveform visualization
   */
  const getAnalyser = useCallback(() => {
    return analyserRef.current;
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (state.audioUrl) {
        URL.revokeObjectURL(state.audioUrl);
      }
      cleanup();
    };
  }, [cleanup, state.audioUrl]);

  return {
    state,
    startRecording,
    stopRecording,
    clearRecording,
    getAnalyser,
  };
}
