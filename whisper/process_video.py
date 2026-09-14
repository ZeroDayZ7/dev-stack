import json
import sys
from pathlib import Path


def format_timestamp(seconds: float) -> str:
    """Konwertuje sekundy do formatu SRT: HH:MM:SS,mmm."""
    milliseconds = round(seconds * 1000)

    hours = milliseconds // 3_600_000
    milliseconds %= 3_600_000

    minutes = milliseconds // 60_000
    milliseconds %= 60_000

    secs = milliseconds // 1_000
    milliseconds %= 1_000

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def convert_json_to_srt(json_path: Path, srt_path: Path) -> None:
    with json_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    segments = data.get("segments")

    if not isinstance(segments, list):
        raise ValueError("JSON nie zawiera poprawnej tablicy 'segments'.")

    if not segments:
        raise ValueError("Whisper nie zwrócił żadnych segmentów.")

    with srt_path.open("w", encoding="utf-8-sig") as file:
        subtitle_index = 1

        for segment in segments:
            start = segment.get("start")
            end = segment.get("end")
            text = segment.get("text", "").strip()

            if start is None or end is None:
                continue

            if not text:
                continue

            file.write(f"{subtitle_index}\n")
            file.write(
                f"{format_timestamp(start)} --> {format_timestamp(end)}\n"
            )
            file.write(f"{text}\n")
            file.write("\n")

            subtitle_index += 1

    if subtitle_index == 1:
        raise ValueError("Nie znaleziono poprawnych segmentów do zapisania.")


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "Uzycie: python process_video.py <input.json> <output.srt>",
            file=sys.stderr,
        )
        return 1

    json_path = Path(sys.argv[1])
    srt_path = Path(sys.argv[2])

    if not json_path.exists():
        print(f"[ERROR] Nie znaleziono pliku JSON: {json_path}", file=sys.stderr)
        return 1

    try:
        convert_json_to_srt(json_path, srt_path)
    except json.JSONDecodeError as error:
        print(f"[ERROR] Niepoprawny JSON: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"[ERROR] Nie udalo sie wygenerowac SRT: {error}", file=sys.stderr)
        return 1

    print(f"[OK] SRT wygenerowany: {srt_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())