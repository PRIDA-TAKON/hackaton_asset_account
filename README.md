---
title: Hackathon Asset Declaration
emoji: 💰
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.31.0
app_file: app.py
pinned: false
license: mit
---

# Hackathon ข้อมูลบัญชีทรัพย์สิน 💰

Web Application สำหรับแปลงไฟล์ PDF บัญชีทรัพย์สินและหนี้สินเป็นข้อมูล Digital (CSV) ด้วย AI (Gemini).

## Features
- 📂 **Upload PDF**: อัปโหลดไฟล์ PDF ได้ทีละหลายไฟล์
- ☁️ **Google Drive**: รองรับการดาวน์โหลดจาก Google Drive Folder Link
- 🤖 **AI Powered**: ใช้ Google Gemini ในการดึงข้อมูลอย่างแม่นยำ
- 📊 **CSV Export**: ส่งออกข้อมูลเป็น CSV พร้อมใช้งาน

## Setup Locally
1. Clone repo
2. Install dependencies: `pip install -r requirements.txt`
3. Install Poppler
4. Run: `streamlit run app.py`

## Environment Variables
- `api_gemini`: Google Gemini API Key
