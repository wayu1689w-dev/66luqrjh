# Video Joiner

แอปต่อวิดีโอหลายคลิปเป็นไฟล์เดียว โดยไม่ให้เสียงหาย/เพี้ยน (ต้องมี `ffmpeg` ในเครื่อง)

    python -m videojoiner a.mp4 b.mov c.mp4 -o joined.mp4   # CLI
    python -m videojoiner.web                               # เว็บ http://localhost:8000
    python -m unittest discover tests                       # ทดสอบ

ตัวเลือก: `--size 1080x1920` (แนวตั้ง) `--fps 30` `--mute`

เสียงหายเพราะอะไร: คลิปบางอันไม่มีแทร็กเสียง / sample rate ต่างกัน
แก้โดยปรับทุกคลิปเป็น 48kHz สเตอริโอ และสร้างเสียงเงียบความยาวเท่าคลิปให้คลิปที่ไม่มีเสียง
แล้วต่อด้วย concat filter
