"""Pydantic models for CAIP data schemas used by the demo agents.

These complement the JSON Schema files in spec/schemas/ and define the
typed structures that agents produce (estimate-v1, quote-v1).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# estimate-v1
# ---------------------------------------------------------------------------

class EstimateLineItem(BaseModel):
    bom_item_id: str = Field(alias="bomItemId")
    description: str
    quantity: float
    unit: str
    material_unit_cost: float = Field(alias="materialUnitCost")
    material_total: float = Field(alias="materialTotal")
    labor_hours: float = Field(alias="laborHours")
    labor_rate: float = Field(alias="laborRate")
    labor_total: float = Field(alias="laborTotal")
    equipment_cost: float = Field(0.0, alias="equipmentCost")
    subtotal: float

    model_config = {"populate_by_name": True}


class EstimateSummary(BaseModel):
    total_material: float = Field(alias="totalMaterial")
    total_labor: float = Field(alias="totalLabor")
    total_equipment: float = Field(alias="totalEquipment")
    subtotal: float
    overhead_percentage: float = Field(alias="overheadPercentage")
    overhead_amount: float = Field(alias="overheadAmount")
    profit_percentage: float = Field(alias="profitPercentage")
    profit_amount: float = Field(alias="profitAmount")
    grand_total: float = Field(alias="grandTotal")

    model_config = {"populate_by_name": True}


class EstimateMetadata(BaseModel):
    generated_by: str = Field(alias="generatedBy")
    generated_at: str = Field(alias="generatedAt")
    confidence: float
    pricing_region: str = Field("US-National", alias="pricingRegion")
    pricing_date: str = Field(alias="pricingDate")
    notes: list[str] = []

    model_config = {"populate_by_name": True}


class EstimateV1(BaseModel):
    project_id: str = Field(alias="projectId")
    trade: str
    csi_division: str = Field(alias="csiDivision")
    line_items: list[EstimateLineItem] = Field(alias="lineItems")
    summary: EstimateSummary
    metadata: EstimateMetadata

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# quote-v1
# ---------------------------------------------------------------------------

class QuoteLineItem(BaseModel):
    bom_item_id: str = Field(alias="bomItemId")
    description: str
    quantity: float
    unit: str
    unit_price: float = Field(alias="unitPrice")
    extended_price: float = Field(alias="extendedPrice")
    manufacturer: str
    part_number: str = Field(alias="partNumber")
    lead_time_days: int = Field(alias="leadTimeDays")
    availability: str  # "in-stock", "made-to-order", "backordered"
    notes: str | None = None

    model_config = {"populate_by_name": True}


class QuoteSummary(BaseModel):
    subtotal: float
    tax_rate: float = Field(alias="taxRate")
    tax_amount: float = Field(alias="taxAmount")
    freight: float
    total: float

    model_config = {"populate_by_name": True}


class QuoteTerms(BaseModel):
    payment_terms: str = Field(alias="paymentTerms")
    delivery_method: str = Field(alias="deliveryMethod")
    warranty: str
    return_policy: str = Field(alias="returnPolicy")

    model_config = {"populate_by_name": True}


class QuoteMetadata(BaseModel):
    generated_by: str = Field(alias="generatedBy")
    generated_at: str = Field(alias="generatedAt")
    confidence: float

    model_config = {"populate_by_name": True}


class QuoteV1(BaseModel):
    project_id: str = Field(alias="projectId")
    supplier_name: str = Field(alias="supplierName")
    quote_number: str = Field(alias="quoteNumber")
    valid_until: str = Field(alias="validUntil")
    line_items: list[QuoteLineItem] = Field(alias="lineItems")
    summary: QuoteSummary
    terms: QuoteTerms
    metadata: QuoteMetadata

    model_config = {"populate_by_name": True}
