from typing import List, Optional
from pydantic import BaseModel, Field

class SubmitterInfo(BaseModel):
    title: Optional[str] = Field(None, description="Title (e.g., นาย, นาง, นางสาว)")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    position: Optional[str] = Field(None, description="Position held")
    agency: Optional[str] = Field(None, description="Agency or Organization")
    submitted_date: Optional[str] = Field(None, description="Date of submission (DD/MM/YYYY)")

class SpouseInfo(BaseModel):
    title: Optional[str] = Field(None, description="Title")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")

class ChildInfo(BaseModel):
    title: Optional[str] = Field(None, description="Title")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    age: Optional[int] = Field(None, description="Age")

class Asset(BaseModel):
    description: Optional[str] = Field(None, description="Description of the asset")
    value: Optional[float] = Field(None, description="Value of the asset")
    type: Optional[str] = Field(None, description="Type of asset (e.g., เงินสด, เงินฝาก, ที่ดิน)")
    owner: Optional[str] = Field(None, description="Owner (ผู้ยื่น, คู่สมรส, บุตร)")

class Debt(BaseModel):
    description: Optional[str] = Field(None, description="Description of the debt")
    value: Optional[float] = Field(None, description="Value of the debt")
    owner: Optional[str] = Field(None, description="Owner (ผู้ยื่น, คู่สมรส, บุตร)")

class AssetDeclaration(BaseModel):
    doc_id: Optional[str] = Field(None, description="Document ID if available")
    submitter: SubmitterInfo = Field(..., description="Information about the submitter")
    spouse: Optional[SpouseInfo] = Field(None, description="Information about the spouse")
    children: List[ChildInfo] = Field(default_factory=list, description="List of children")
    assets: List[Asset] = Field(default_factory=list, description="List of assets")
    debts: List[Debt] = Field(default_factory=list, description="List of debts")
    total_assets: Optional[float] = Field(None, description="Total assets value")
    total_debts: Optional[float] = Field(None, description="Total debts value")
