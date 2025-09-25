"""
Database models for type hints and data validation
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Case:
    """Model for court case data"""
    case_name: str
    docket_number: str
    docket_url: Optional[str] = None
    town: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database insertion"""
        data = {
            'case_name': self.case_name,
            'docket_number': self.docket_number,
        }
        if self.docket_url:
            data['docket_url'] = self.docket_url
        if self.town:
            data['town'] = self.town
        return data

@dataclass
class Defendant:
    """Model for defendant data"""
    name: str
    docket_number: Optional[str] = None
    address: Optional[str] = None
    town: Optional[str] = None  # Changed from city to town
    state: Optional[str] = None
    zip: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database insertion"""
        data = {'name': self.name}
        if self.docket_number:
            data['docket_number'] = self.docket_number
        if self.address:
            data['address'] = self.address
        if self.town:
            data['town'] = self.town
        if self.state:
            data['state'] = self.state
        if self.zip:
            data['zip'] = self.zip
        return data

@dataclass
class SkipTrace:
    """Model for skip trace data"""
    docket_number: str
    phone_number: str
    phone_type: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database insertion"""
        data = {
            'docket_number': self.docket_number,
            'phone_number': self.phone_number
        }
        if self.phone_type:
            data['phone_type'] = self.phone_type
        return data

@dataclass
class SkipTraceCost:
    """Model for tracking skip trace costs"""
    docket_number: str
    lookup_count: int = 1
    cost_per_lookup: float = 0.07
    is_sandbox: bool = False
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    @property
    def total_cost(self) -> float:
        """Calculate total cost"""
        return self.lookup_count * self.cost_per_lookup

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database insertion"""
        return {
            'docket_number': self.docket_number,
            'lookup_count': self.lookup_count,
            'cost_per_lookup': self.cost_per_lookup,
            'is_sandbox': self.is_sandbox
        }

@dataclass
class ScrapedCase:
    """Model for scraped case data from web scraper"""
    case_name: str
    docket_number: str
    docket_url: str
    defendants: List[Dict[str, str]] = field(default_factory=list)

    def to_case_model(self, town: str = None) -> Case:
        """Convert to Case model"""
        return Case(
            case_name=self.case_name,
            docket_number=self.docket_number,
            docket_url=self.docket_url,
            town=town
        )

    def to_defendant_models(self, docket_number: str, town: str = None) -> List[Defendant]:
        """Convert defendants to Defendant models with docket_number and town"""
        defendant_models = []
        for def_data in self.defendants:
            defendant = Defendant(
                name=def_data.get('name', ''),
                docket_number=docket_number,
                address=def_data.get('address'),
                town=town or def_data.get('town'),  # Use provided town or from data
                state=def_data.get('state'),
                zip=def_data.get('zip')
            )
            defendant_models.append(defendant)
        return defendant_models