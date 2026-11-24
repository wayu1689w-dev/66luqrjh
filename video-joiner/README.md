# Video Joiner

แอปต่อวิดีโอหลายคลิปเป็นไฟล์เดียว โดยเสียงไม่หาย (ต้องมี `ffmpeg` ≥ 5.1 และ Python 3.9+)

    python -m videojoiner.web          # เว็บ http://localhost:8000
    python -m videojoiner a.mp4 b.mov -o joined.mp4 [ตัวเลือก]
    python -m unittest discover tests

## ฟีเจอร์
- ลากสลับลำดับคลิปในหน้าเว็บ (ลบคลิปได้)
- Crossfade ภาพ+เสียงระหว่างคลิป: `--crossfade 0.5`
- เพลงพื้นหลังผสมใต้เสียงเดิม วนซ้ำถ้าสั้น เฟดท้ายให้เอง: `--music bg.mp3 --music-volume 0.25`
- แถบความคืบหน้า (เว็บ: อัปโหลด + เข้ารหัส / CLI: เปอร์เซ็นต์)
- ตัวเลือกอื่น: `--size 1080x1920` `--fps 30` `--mute`

## เสียงไม่หายได้อย่างไร
- คลิปที่ไม่มีเสียง → สร้างเสียงเงียบยาวเท่าคลิป เสียงคลิปอื่นไม่เลื่อน
- ปรับทุกคลิปเป็น 48kHz สเตอริโอก่อนต่อ
- ตรวจไฟล์ผลลัพธ์ว่ามีแทร็กเสียง ถ้าไม่มีจะ error

## ข้อจำกัด
- เข้ารหัสใหม่ทุกครั้ง (ช้ากว่าการ copy stream)
- คลิปต้องยาวอย่างน้อย 2 เท่าของเวลา crossfade
- เว็บลบไฟล์ที่อัปโหลดทันทีหลังต่อเสร็จ และลบผลลัพธ์เมื่อเกิน 1 ชั่วโมง (ตอนมีงานใหม่เข้า)

## Gemini (โครง — ยังไม่ได้ทดสอบกับ API จริง)
ตั้ง `GEMINI_API_KEY` (จาก Google AI Studio) แล้ว:

    python -m videojoiner.gemini subs joined.mp4 -o subs.srt --lang th   # ซับไตเติล
    python -m videojoiner.gemini speak script.txt -o voice.wav           # เสียงพากย์
    python -m videojoiner a.mp4 b.mp4 --voiceover voice.wav -o out.mp4   # ใส่เสียงพากย์ (เล่นครั้งเดียว)

ชื่อโมเดลตั้งผ่าน `GEMINI_STT_MODEL` / `GEMINI_TTS_MODEL` / `GEMINI_VOICE` — ค่าเริ่มต้นเป็นเพียงค่าเดา ต้องตรวจกับเอกสารปัจจุบัน
ตอนนี้ยังไม่ได้ฝังซับลงภาพและไม่ได้เชื่อมกับหน้าเว็บ

## ติดตั้งเป็นปลั๊กอิน Claude Code
    /plugin install video-joiner --marketplace wayu1689w-dev/66luqrjh   # Claude Code 2.1.275+

จากนั้นสั่ง Claude ว่า "ต่อวิดีโอเหล่านี้" สกิล `join-videos` จะทำงานให้ (ต้องมี ffmpeg)
ถ้าจะใช้ Gemini ให้ตั้ง `GEMINI_API_KEY` จาก Google AI Studio ใน environment
