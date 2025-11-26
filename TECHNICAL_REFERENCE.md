# เครื่องมือและทรัพยากร (Tools & Resources)

เอกสารนี้ระบุรายการเครื่องมือ เทคโนโลยี และทรัพยากรที่ใช้ในการพัฒนาโปรเจคนี้

## 1. เครื่องมือและไลบรารีหลัก (Core Tools & Libraries)

| เครื่องมือ / ไลบรารี | หน้าที่หลัก |
|-------------------|-------------|
| **Python** | ภาษาโปรแกรมหลักที่ใช้ในการพัฒนา |
| **Streamlit** | Framework สำหรับสร้าง Web Application UI อย่างรวดเร็ว |
| **Google Gemini API** | AI Model (Gemini 1.5 Flash/Pro) สำหรับอ่านและสกัดข้อมูลจากเอกสาร PDF |
| **pdf2image** | แปลงไฟล์ PDF เป็นรูปภาพเพื่อส่งให้ AI ประมวลผล (ต้องใช้ Poppler) |
| **Pandas** | จัดการและประมวลผลข้อมูลในรูปแบบตาราง (DataFrame) และส่งออกเป็น CSV |
| **Pydantic** | (Optional) ใช้สำหรับกำหนดโครงสร้างข้อมูล (Data Validation) |

## 2. ทรัพยากรภายนอก (External Resources)

- **Poppler**: โปรแกรมเบื้องหลังสำหรับจัดการไฟล์ PDF
  - แหล่งดาวน์โหลด: [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/)
- **Hugging Face Spaces**: แพลตฟอร์มสำหรับ Deploy Application (Cloud Hosting)
- **Google AI Studio**: แหล่งสำหรับขอ API Key และทดสอบ Prompt

## 3. โครงสร้างข้อมูลผลลัพธ์ (Output Data Structure)

ระบบจะสร้างไฟล์ CSV ตามมาตรฐานที่กำหนด ดังนี้:
1. **Train_summary.csv**: ข้อมูลสรุปภาพรวมของผู้ยื่นบัญชีทรัพย์สิน
2. **Test_doc_info.csv**: ข้อมูลอ้างอิงเอกสารและ ID
3. **Test_nacc_detail.csv**: รายละเอียดการยื่นบัญชีต่อ ป.ป.ช.
4. **Test_submitter_info.csv**: ข้อมูลส่วนตัวละเอียดของผู้ยื่น
