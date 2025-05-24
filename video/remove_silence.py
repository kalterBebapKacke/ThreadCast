import numpy as np
import librosa
import soundfile as sf


def detect_silence(audio, sr, threshold_db=-20, min_silence_duration=0.2):
    """
    Detects silent regions in audio based on threshold and minimum duration.

    Parameters:
    -----------
    audio : numpy.ndarray
        Audio signal
    sr : int
        Sample rate
    threshold_db : float
        Threshold in dB below which audio is considered silent
    min_silence_duration : float
        Minimum duration in seconds for a region to be considered silent

    Returns:
    --------
    list of tuples
        List of (start_sample, end_sample) for silent regions
    """
    # Convert threshold from dB to amplitude
    threshold_amp = 10 ** (threshold_db / 20)

    # Get amplitude envelope
    amplitude = np.abs(audio)

    # Find silent regions (below threshold)
    is_silent = amplitude < threshold_amp

    # Find boundaries of silent regions
    silent_regions = []
    silent_start = None

    min_samples = int(min_silence_duration * sr)

    for i, silent in enumerate(is_silent):
        if silent and silent_start is None:
            silent_start = i
        elif not silent and silent_start is not None:
            duration = i - silent_start
            if duration >= min_samples:
                silent_regions.append((silent_start, i))
            silent_start = None

    # Check for silence at the end of the file
    if silent_start is not None:
        duration = len(audio) - silent_start
        if duration >= min_samples:
            silent_regions.append((silent_start, len(audio)))

    return silent_regions


def apply_crossfade(audio, fade_duration_samples):
    """
    Apply a simple linear fade in at the beginning and fade out at the end.

    Parameters:
    -----------
    audio : numpy.ndarray
        Audio segment
    fade_duration_samples : int
        Number of samples for the fade

    Returns:
    --------
    numpy.ndarray
        Audio with fades applied
    """
    length = len(audio)
    if length <= 2 * fade_duration_samples:
        # If segment is shorter than twice the fade duration, adjust fade length
        fade_duration_samples = length // 4

    if fade_duration_samples <= 0:
        return audio

    # Create a copy to avoid modifying the original
    result = np.copy(audio)

    # Create fade-in window
    fade_in = np.linspace(0, 1, fade_duration_samples)

    # Create fade-out window
    fade_out = np.linspace(1, 0, fade_duration_samples)

    # Apply fade-in
    result[:fade_duration_samples] *= fade_in

    # Apply fade-out
    result[-fade_duration_samples:] *= fade_out

    return result


def trim_silence(audio, sr, threshold_db=-20, min_silence_duration=0.2,
                 target_silence_duration=0.2, fade_duration=0.01, padding_duration=0.05):
    """
    Trims silent regions to a target duration with crossfades and padding.

    Parameters:
    -----------
    audio : numpy.ndarray
        Audio signal
    sr : int
        Sample rate
    threshold_db : float
        Threshold in dB below which audio is considered silent
    min_silence_duration : float
        Minimum duration in seconds for a region to be considered silent
    target_silence_duration : float
        Duration in seconds to trim silent regions to
    fade_duration : float
        Duration in seconds for crossfades
    padding_duration : float
        Duration in seconds of additional audio to keep around silence boundaries

    Returns:
    --------
    numpy.ndarray
        Audio with trimmed silence
    """
    # Detect silent regions
    silent_regions = detect_silence(audio, sr, threshold_db, min_silence_duration)

    # If no silent regions, return the original audio
    if not silent_regions:
        return audio

    # Convert durations to samples
    target_silence_samples = int(target_silence_duration * sr)
    fade_samples = int(fade_duration * sr)
    padding_samples = int(padding_duration * sr)

    # Build new audio by concatenating non-silent parts and shortened silence
    result = []
    last_end = 0

    for start, end in silent_regions:
        # Apply padding to the cut points
        cut_start = max(0, start + padding_samples)
        cut_end = min(len(audio), end - padding_samples)

        # Skip if the silent region becomes too short after padding
        if cut_start >= cut_end:
            continue

        # Add audio before silence (up to the padding point)
        result.append(audio[last_end:cut_start])

        # Calculate the center of the silence for trimming
        silence_center = (cut_start + cut_end) // 2
        silence_half_length = target_silence_samples // 2

        # Get the trimmed silence segment, centered in the original silence
        silence_start = max(0, silence_center - silence_half_length)
        silence_end = min(len(audio), silence_center + silence_half_length)
        silence_segment = audio[silence_start:silence_end]

        # Apply crossfade to the silence segment
        silence_segment = apply_crossfade(silence_segment, fade_samples)

        # Add the trimmed silence with crossfades
        result.append(silence_segment)

        last_end = cut_end

    # Add remaining audio after the last silent region
    if last_end < len(audio):
        result.append(audio[last_end:])

    # Concatenate all audio segments
    return np.concatenate(result)


def main(input_file, output_file, ):
    threshold = -20
<<<<<<< HEAD
    min_silence = 0.25
    target_silence = 0.25
=======
    min_silence = 0.2
    target_silence = 0.2
>>>>>>> afc76aa78a748f8a5ba187558dbdec3afb4be4d8
    fade = 0.01
    padding = 0.05

    # Load audio file
    audio, sr = librosa.load(input_file, sr=None)

    processed_audio = trim_silence(
        audio,
        sr,
        threshold_db=threshold,
        min_silence_duration=min_silence,
        target_silence_duration=target_silence,
        fade_duration=fade,
        padding_duration=padding
    )

    # Save processed audio
    sf.write(output_file, processed_audio, sr)


if __name__ == "__main__":
    main('audio_59.mp3', 'test_audio.mp3')