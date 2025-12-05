from typing import List, Optional
from pydantic import BaseModel, Field

class DocumentInfo(BaseModel):
    submitted_date: Optional[str] = Field(description="Submitted date YYYY-MM-DD")
    disclosure_date: Optional[str] = Field(description="Disclosure date YYYY-MM-DD")

class Address(BaseModel):
    sub_district: Optional[str] = Field(description="Sub-district (Tambon)")
    district: Optional[str] = Field(description="District (Amphoe)")
    province: Optional[str] = Field(description="Province")
    post_code: Optional[str] = Field(description="Post code")

class SubmitterInfo(BaseModel):
    title: Optional[str] = Field(description="Title (e.g., นาย, นาง, นางสาว)")
    first_name: Optional[str] = Field(description="First name")
    last_name: Optional[str] = Field(description="Last name")
    age: Optional[int] = Field(description="Age")
    position: Optional[str] = Field(description="Current Position")
    agency: Optional[str] = Field(description="Agency or Organization")
    marital_status: Optional[str] = Field(description="Marital status")
    address: Optional[Address] = Field(description="Address details")

class OldName(BaseModel):
    old_first_name: Optional[str] = Field(description="Old first name")
    old_last_name: Optional[str] = Field(description="Old last name")
    changed_date: Optional[str] = Field(description="Date of change")

class PositionHistory(BaseModel):
    position: Optional[str] = Field(description="Position")
    agency: Optional[str] = Field(description="Agency")
    start_date: Optional[str] = Field(description="Start date")
    end_date: Optional[str] = Field(description="End date")

class SpouseInfo(BaseModel):
    title: Optional[str] = Field(description="Title")
    first_name: Optional[str] = Field(description="First name")
    last_name: Optional[str] = Field(description="Last name")
    age: Optional[int] = Field(description="Age")
    status: Optional[str] = Field(description="Status (e.g. จดทะเบียนสมรส)")
    status_date: Optional[str] = Field(description="Date of status change")

class ChildInfo(BaseModel):
    title: Optional[str] = Field(description="Title")
    first_name: Optional[str] = Field(description="First name")
    last_name: Optional[str] = Field(description="Last name")
    age: Optional[int] = Field(description="Age")

class RelativeInfo(BaseModel):
    relation: Optional[str] = Field(description="Relation (e.g. บิดา, มารดา)")
    title: Optional[str] = Field(description="Title")
    first_name: Optional[str] = Field(description="First name")
    last_name: Optional[str] = Field(description="Last name")
    age: Optional[int] = Field(description="Age")
    is_alive: Optional[bool] = Field(description="Is alive?")

class Asset(BaseModel):
    description: Optional[str] = Field(description="Description")
    value: Optional[float] = Field(description="Value")
    type: Optional[str] = Field(description="Type (เงินสด, เงินฝาก, ที่ดิน, โรงเรือน, ยานพาหนะ, สิทธิ, อื่นๆ)")
    owner: Optional[str] = Field(description="Owner (ผู้ยื่น, คู่สมรส, บุตร)")
    # Detailed fields for specific asset types
    location: Optional[str] = Field(description="Location (for Land/Building)")
    doc_number: Optional[str] = Field(description="Document number (e.g. Title deed, License plate)")
    province: Optional[str] = Field(description="Province (for Land/Building/Vehicle)")
    acquisition_date: Optional[str] = Field(description="Date acquired")

class Debt(BaseModel):
    description: Optional[str] = Field(description="Description")
    value: Optional[float] = Field(description="Value")
    owner: Optional[str] = Field(description="Owner")

class AssetDeclaration(BaseModel):
    doc_id: Optional[str] = Field(description="Document ID")
    document_info: Optional[DocumentInfo] = Field(description="Document metadata (dates)")
    submitter: Optional[SubmitterInfo] = Field(description="Submitter info")
    submitter_old_names: List[OldName] = Field(description="Submitter name changes")
    submitter_positions: List[PositionHistory] = Field(description="Submitter position history")
    spouse: Optional[SpouseInfo] = Field(description="Spouse info")
    spouse_old_names: List[OldName] = Field(description="Spouse name changes")
    spouse_positions: List[PositionHistory] = Field(description="Spouse position history")
    children: List[ChildInfo] = Field(description="Children")
    relatives: List[RelativeInfo] = Field(description="Relatives (Parents, etc.)")
    assets: List[Asset] = Field(description="Assets")
    debts: List[Debt] = Field(description="Debts")
    total_assets: Optional[float] = Field(description="Total assets")
    total_debts: Optional[float] = Field(description="Total debts")
