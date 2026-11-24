# เอกสารส่งต่องาน: video-joiner (ปลั๊กอิน + โน้ต)

เอกสารนี้ให้คนหรือ AI ตัวอื่น (เช่น ChatGPT) อ่านแล้วทำงานต่อได้ ไม่มี API key หรือข้อมูลส่วนตัว

## 1. โครงปลั๊กอิน
```
66luqrjh/                      # repo, branch ccr-f019ece8-ba7cf4
├── .claude-plugin/marketplace.json   # รายการปลั๊กอินของ repo
└── video-joiner/                     # รากของปลั๊กอิน
    ├── .claude-plugin/plugin.json    # ชื่อ/เวอร์ชัน/คำอธิบาย
    ├── skills/join-videos/SKILL.md   # สกิลที่สอน Claude ว่าเรียกอะไร
    ├── videojoiner/
    │   ├── joiner.py    # ตัวต่อคลิป (ffmpeg): probe, build_command, join_videos
    │   ├── __main__.py  # CLI
    │   ├── web.py       # หน้าเว็บ ลากสลับ/ความคืบหน้า (เฉพาะเครื่องตัวเอง)
    │   └── gemini.py    # โครง: ซับไตเติล (STT) + เสียงพากย์ (TTS)
    ├── tests/           # unittest 10 ข้อ
    ├── README.md  AI_STUDIO_PROMPT.md  HANDOFF.md
```
ติดตั้ง (Claude Code 2.1.275+): `/plugin install video-joiner --marketplace wayu1689w-dev/66luqrjh`

## 2. โน้ตสำคัญ
- ต้องมี ffmpeg >= 5.1 (ใช้ `amix normalize=0`) และ Python 3.9+
- เสียงไม่หาย: ปรับทุกคลิปเป็น 48kHz สเตอริโอ, คลิปไร้เสียงได้เสียงเงียบยาวเท่าคลิป, ตรวจว่าผลลัพธ์มีแทร็กเสียง
- crossfade: คลิปต้องยาว >= 2 เท่าของเวลา crossfade
- `--voiceover` ใช้พร้อม `--music` ไม่ได้ (ยังไม่รองรับ)
- เว็บไม่มีล็อกอิน ใช้เฉพาะเครื่องตัวเอง
- ชื่อโมเดล Gemini ใน gemini.py เป็นค่าเดา ตั้งทับด้วย `GEMINI_STT_MODEL` / `GEMINI_TTS_MODEL`; key อยู่ใน `GEMINI_API_KEY` เท่านั้น ห้ามใส่ในโค้ดหรือแชท

## 3. สถานะ
| ส่วน | สถานะ |
|---|---|
| ต่อคลิป/crossfade/เพลง/ความคืบหน้า/ลากสลับ | ทดสอบแล้ว (กับคลิปสังเคราะห์) |
| โครงปลั๊กอิน | `claude plugin validate` ผ่าน ยังไม่ได้ลองติดตั้งแล้วสั่งงานจริง |
| Gemini STT/TTS | ทดสอบกับคำตอบจำลองเท่านั้น ยังไม่เคยเรียก API จริง |
| ทดสอบกับคลิปจริงของผู้ใช้ | ยังไม่ได้ทำ |

## 4. งานที่ค้าง
- [ ] ทดสอบ Gemini กับ API จริงและยืนยันชื่อโมเดล
- [ ] ฝังซับลงบนภาพ (ต้องมี libass)
- [ ] ต่อ Gemini เข้าหน้าเว็บ
- [ ] ใส่ผู้เขียนใน plugin.json (ถามเจ้าของก่อน)

## 5. พรอมต์สำหรับ ChatGPT
> อ่านเอกสารนี้และโค้ดใน `video-joiner/` แล้วทำงานในข้อ 4 ทีละข้อ
> ห้ามขอหรือเก็บ API key ในแชท ห้ามอ้างว่าทดสอบกับ API จริงถ้ายังไม่ได้รัน
> รายงานผลเทสต์จริงทุกครั้ง (`python -m unittest discover tests`)
