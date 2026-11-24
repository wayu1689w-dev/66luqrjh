# 66luqrjh

[![CI](https://github.com/wayu1689w-dev/66luqrjh/actions/workflows/ci.yml/badge.svg)](https://github.com/wayu1689w-dev/66luqrjh/actions/workflows/ci.yml)

[Edit in StackBlitz next generation editor ⚡️](https://stackblitz.com/~/github.com/wayu1689w-dev/66luqrjh)

## มีอะไรในนี้
| ส่วน | ที่อยู่ | รันที่ไหนได้ |
|---|---|---|
| ปลั๊กอินต่อวิดีโอ (`video-joiner`) | `video-joiner/` | **เครื่องตัวเองเท่านั้น** ต้องมี Python + ffmpeg |
| โทเค็นสี (สว่าง/มืด, Tailwind v4) | `tokens.css` | StackBlitz หรือที่ไหนก็ได้ |
| ตัว build ทดลอง (rolldown) | `index.ts`, `rolldown.config.ts` | StackBlitz |

StackBlitz รันได้เฉพาะ Node ในเบราว์เซอร์ ไม่มี Python/ffmpeg จึงใช้รัน `video-joiner` ไม่ได้ ใช้แก้โค้ดและดูไฟล์ได้เท่านั้น

## ระบบอัตโนมัติ (GitHub Actions)
ทุกครั้งที่ push หรือเปิด PR ระบบรัน `.github/workflows/ci.yml`:
1. ติดตั้ง ffmpeg แล้วรัน unit test ของ `video-joiner`
2. ตรวจ `plugin.json` / `marketplace.json` ว่าถูกต้องและชื่อตรงกัน
3. ตรวจ `tokens.css` ว่าวงเล็บครบและทุก `var()` ชี้ไปตัวแปรที่มีจริง

ติดตั้งปลั๊กอิน: `/plugin install video-joiner --marketplace wayu1689w-dev/66luqrjh`
