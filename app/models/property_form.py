"""
Real estate property form data models.

This module defines the data structures for property search requirements,
including field validation, status tracking, and form completion logic.
"""
import enum
import logging
import re
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

LOG = logging.getLogger(__name__)


class FieldStatus(str, enum.Enum):
    """Possible states for a form field."""
    NOT_PROVIDED = 'not_provided'
    INVALID = 'invalid'
    VALID = 'valid'


class PropertyField(BaseModel):
    """Model for an individual property form field."""
    status: FieldStatus = FieldStatus.NOT_PROVIDED
    value: Optional[str] = None
    description: str
    examples: List[str]
    validation_pattern: Optional[str] = None

    def validate_value(self, value: str) -> Tuple[bool, Optional[str]]:
        """
        Validate the provided value for this field.

        Args:
            value: The value to validate

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if the value is valid, False otherwise
            - error_message: Descriptive error message if invalid, None if valid
        """
        # If there is a validation pattern, apply it
        if self.validation_pattern and value:
            pattern = re.compile(self.validation_pattern)
            if not pattern.match(value):
                return False, 'The value does not match the expected pattern for this field.'
        return True, None

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            'examples': [
                {
                    'status': 'valid',
                    'value': '20,000 USD',
                    'description': 'Budget for the property',
                    'examples': ['I have a budget of 20,000 USD']
                }
            ]
        }


class PropertyFormModel(BaseModel):
    """Complete real estate property form model."""
    budget: PropertyField = Field(
        default_factory=lambda: PropertyField(
            description='Budget for the property (e.g., 20,000 USD)',
            examples=['I have a budget of 20,000 USD', 'My budget is 50,000 dollars'],
        )
    )
    total_size: PropertyField = Field(
        default_factory=lambda: PropertyField(
            description='Total size requirement (e.g., 500m²)',
            examples=['I need 500m²', 'I\'m looking for 300 square meters'],
        )
    )
    real_estate_type: PropertyField = Field(
        default_factory=lambda: PropertyField(
            description='Type of real estate (e.g., office, retail, warehouse)',
            examples=['I am looking for an office space', 'I need a retail location'],
        )
    )
    city: PropertyField = Field(
        default_factory=lambda: PropertyField(
            description='City location (e.g., Mexico City)',
            examples=['I want a property in Mexico City', 'Looking in Barcelona'],
        )
    )

    additional_fields: Dict[str, PropertyField] = Field(default_factory=dict)
    form_complete: bool = False

    def is_complete(self) -> bool:
        """Check if all required fields are complete."""
        required_fields = [self.budget, self.total_size, self.real_estate_type, self.city]
        return all(field.status == FieldStatus.VALID for field in required_fields)

    def update_completion_status(self) -> bool:
        """Update the form completion status and return that status."""
        self.form_complete = self.is_complete()
        return self.form_complete

    def get_missing_fields(self) -> List[str]:
        """Return the names of required fields that are not yet complete."""
        missing = []
        fields_map = {
            'budget': self.budget,
            'total_size': self.total_size,
            'real_estate_type': self.real_estate_type,
            'city': self.city
        }

        for name, field in fields_map.items():
            if field.status != FieldStatus.VALID:
                missing.append(name)

        return missing

    def update_field(self, field_name: str, value: str) -> Tuple[bool, Optional[str]]:
        """
        Update a field with a new value and validate the result.

        Args:
            field_name: Name of the field to update
            value: New value for the field

        Returns:
            Tuple of (success, error_message)
            - success: True if updated successfully, False otherwise
            - error_message: Description of the error if any, None if successful
        """
        LOG.debug("Updating field '%s' with value '%s'", field_name, value)

        # Determine if it's a required or additional field
        if field_name in ['budget', 'total_size', 'real_estate_type', 'city']:
            field = getattr(self, field_name)

            is_valid, error_msg = field.validate_value(value)

            field.value = value
            field.status = FieldStatus.VALID if is_valid else FieldStatus.INVALID

            self.update_completion_status()

            if not is_valid:
                LOG.warning("Field '%s' validation failed: %s", field_name, error_msg)
            else:
                LOG.debug("Successfully updated required field '%s'", field_name)
            return is_valid, error_msg

        # Handle additional fields
        if field_name not in self.additional_fields:
            LOG.debug("Creating new additional field '%s'", field_name)
            self.additional_fields[field_name] = PropertyField(
                description=f'Additional field: {field_name}',
                examples=[value],
                value=value,
                status=FieldStatus.VALID  # We assume valid for additional fields
            )
        else:
            LOG.debug("Updating existing additional field '%s'", field_name)
            self.additional_fields[field_name].value = value
            self.additional_fields[field_name].status = FieldStatus.VALID

        return True, None

    def get_fields_summary(self) -> str:
        """
        Generate a readable summary of all form fields.

        Returns:
            A formatted string summarizing the status of all fields.
        """
        summary = []

        summary.append('### Required Fields')
        fields_map = {
            'Budget': self.budget,
            'Total Size': self.total_size,
            'Real Estate Type': self.real_estate_type,
            'City': self.city
        }

        for name, field in fields_map.items():
            if getattr(field, 'status') == FieldStatus.VALID:
                summary.append(f'✅ **{name}**: {getattr(field, "value")}')
            elif getattr(field, 'status') == FieldStatus.INVALID:
                summary.append(f'❌ **{name}**: {getattr(field, "value")} (Invalid)')
            else:
                summary.append(f'⬜ **{name}**: Not provided')

        if self.additional_fields:
            summary.append('\n### Additional Fields')
            # pylint: disable=E1101
            for name, field in self.additional_fields.items():
                display_name = name.replace('_', ' ').title()
                summary.append(f'📌 **{display_name}**: {field.value}')

        summary.append('\n### Form Status')
        if self.form_complete:
            summary.append('✅ All required fields are complete!')
        else:
            missing = self.get_missing_fields()
            missing_str = ', '.join([f'`{field}`' for field in missing])
            summary.append(f'⬜ Waiting for: {missing_str}')

        return '\n'.join(summary)
