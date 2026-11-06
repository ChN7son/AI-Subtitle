# AI-Subtitle

在 Windows 上將中文語音轉成台灣繁體 SRT。輸入影片時，同時輸出字幕固定顯示在畫面上的 MP4。也能用校對後的 SRT 重新輸出影片，省去語音辨識。

## 安裝

1. 安裝 **Windows 64 位元版 Python 3.12**，並在安裝程式啟用 Python Launcher，以便使用 `py -3.12`。[Python 官方下載](https://www.python.org/downloads/windows/)
2. 將專案下載並解壓縮，或用 Git 複製專案。在含有 `subtitle.py` 的資料夾開啟 PowerShell，依序執行以下命令。

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -c "from huggingface_hub import snapshot_download; snapshot_download('Systran/faster-whisper-small', local_dir='model', allow_patterns=['config.json','model.bin','tokenizer.json','vocabulary.*','preprocessor_config.json'])"
```

套件和模型下載需要網路。模型約 484 MB。安裝後用 CPU 在本機處理，不需要 API 金鑰。FFmpeg 由 `imageio-ffmpeg` 提供。

## 拖放使用

1. 將一支原始影片拖到 `1-generate-subtitles.bat`。在專案的 `校對` 資料夾取得 `原始檔名.zh-TW.srt` 和 `原始檔名.zh-TW.mp4`。音檔只會產生 SRT。
2. 用記事本修改 SRT，保留檔名、字幕編號和時間碼，以 UTF-8 儲存。
3. 將同一支原始影片拖到 `2-apply-edited-subtitles.bat`。批次檔會從 `校對` 讀取同名 SRT，輸出 `原始檔名.zh-TW.edited.mp4`。

如果目的地已存在同名成品，請先移走或重新命名舊檔。兩個批次檔每次接收一個檔案。

## 命令列與 AI Agent

在專案資料夾執行以下命令，並換成自己的檔案路徑。省略 `--output-dir` 時，預設輸出到來源檔案所在的資料夾。

```powershell
.\subtitle.cmd "C:\影片\原始影片.mp4" --output-dir ".\校對"
.\subtitle.cmd "C:\影片\原始影片.mp4" --srt ".\校對\原始影片.zh-TW.srt" --output-dir ".\校對"
```

成功時，標準輸出回傳一行 JSON，包含 `output`（絕對路徑）與 `type`（`srt` 或 `mp4`）。自動辨識影片時也會回傳 `srt` 路徑。失敗時會回傳非零結束碼，錯誤寫到標準錯誤。

## 開源來源

- **faster-whisper** 用 CTranslate2 執行語音辨識。[faster-whisper](https://github.com/SYSTRAN/faster-whisper) · [OpenAI Whisper](https://github.com/openai/whisper) · [small 模型下載](https://huggingface.co/Systran/faster-whisper-small)
- **FFmpeg** 將字幕壓進 MP4，執行檔由 imageio-ffmpeg 套件提供。[FFmpeg](https://github.com/FFmpeg/FFmpeg) · [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg)
- **OpenCC** 以 `s2twp` 將辨識結果轉成台灣繁體字形與用詞。[OpenCC](https://github.com/BYVoid/OpenCC)
- **PyAV** 讀取影音串流資訊。[PyAV](https://github.com/PyAV-Org/PyAV)

本專案的整合程式和批次檔採用 MIT 授權，詳見 [LICENSE](LICENSE)。上游套件、FFmpeg 執行檔和模型各自適用其上游授權，並在安裝時下載。
