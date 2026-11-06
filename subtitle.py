import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent



def timestamp(seconds):
    minutes, millis = divmod(round(seconds * 1000), 60000)
    hours, minutes = divmod(minutes, 60)
    seconds, millis = divmod(millis, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"


def transcribe(source):
    from faster_whisper import WhisperModel
    from opencc import OpenCC

    model = WhisperModel(str(ROOT / "model"), device="cpu", compute_type="int8", local_files_only=True)
    segments, _ = model.transcribe(str(source), language="zh", vad_filter=True)
    to_taiwan = OpenCC("s2twp.json")
    subtitles = []
    for segment in segments:
        line = " ".join(segment.text.split())
        if line:
            subtitles.append(
                f"{len(subtitles) + 1}\n{timestamp(segment.start)} --> {timestamp(segment.end)}\n"
                f"{to_taiwan.convert(line)}\n"
            )
    if not subtitles:
        raise ValueError("No speech was detected.")

    return "\n".join(subtitles)


def convert(source, output_dir, edited_srt):
    import av

    source = source.resolve(strict=True)
    if not source.is_file():
        raise ValueError("Input must be a media file.")
    with av.open(str(source)) as media:
        has_audio = bool(media.streams.audio)
        video = next(
            (s.index for s in media.streams.video if not s.disposition.attached_pic & s.disposition),
            None,
        )
    if edited_srt is not None and video is None:
        raise ValueError("--srt requires a video input.")
    if edited_srt is None and not has_audio:
        raise ValueError("Input has no audio stream.")

    destination = (output_dir or source.parent).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    srt_output = destination / (source.stem + ".zh-TW.srt")
    video_suffix = ".zh-TW.edited.mp4" if edited_srt is not None else ".zh-TW.mp4"
    video_output = destination / (source.stem + video_suffix)
    targets = []
    if edited_srt is None:
        targets.append(("captions.srt", srt_output))
    if video is not None:
        targets.append(("result.mp4", video_output))
    for _, target in targets:
        if target.exists():
            raise FileExistsError(f"Output already exists: {target}")

    captions = (
        edited_srt.read_text(encoding="utf-8-sig")
        if edited_srt is not None else transcribe(source)
    )
    if not captions.strip():
        raise ValueError("The SRT file is empty.")

    with TemporaryDirectory(prefix=".subtitle-", dir=destination) as temporary:
        scratch = Path(temporary)
        (scratch / "captions.srt").write_text(captions, encoding="utf-8")
        if video is not None:
            from imageio_ffmpeg import get_ffmpeg_exe

            subprocess.run(
                [
                    get_ffmpeg_exe(), "-nostdin", "-hide_banner", "-loglevel", "error",
                    "-i", str(source), "-map", f"0:{video}", "-map", "0:a:0?",
                    "-vf", "subtitles=captions.srt:force_style='FontName=Microsoft JhengHei'",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart",
                    str(scratch / "result.mp4"),
                ],
                cwd=scratch,
                check=True,
            )
        published = []
        try:
            for name, target in targets:
                os.rename(scratch / name, target)
                published.append(target)
        except OSError:
            for target in published:
                target.unlink()
            raise

    result = {
        "output": str(srt_output if video is None else video_output),
        "type": "srt" if video is None else "mp4",
    }
    if video is not None and edited_srt is None:
        result["srt"] = str(srt_output)
    return result



def main():
    parser = argparse.ArgumentParser(description="Convert Mandarin media to Taiwan Traditional Chinese subtitles.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--srt", type=Path, help="Burn an existing UTF-8 SRT into the original video.")
    args = parser.parse_args()
    try:
        print(json.dumps(convert(args.input, args.output_dir, args.srt), ensure_ascii=False))
    except Exception as error:
        print(f"Subtitle conversion failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())


