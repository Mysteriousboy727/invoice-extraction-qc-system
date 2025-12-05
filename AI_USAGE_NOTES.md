# AI Usage Notes

## Tools Used

I used **Cursor AI (Claude Sonnet)** and **GitHub Copilot** throughout the development process.

## Parts Where AI Was Used

### 1. **Project Scaffolding & Structure**
- **AI Help**: Generated initial folder structure and boilerplate code
- **What I Changed**: Reorganized to follow clean architecture principles, adjusted module structure

### 2. **Regex Pattern Development**
- **AI Help**: Suggested initial regex patterns for extracting invoice fields
- **What I Changed**: 
  - AI suggested overly complex patterns that didn't work well with real PDF text
  - Simplified to more robust patterns that handle variations in formatting
  - Added multiple fallback patterns for each field type

### 3. **Pydantic Schema Design**
- **AI Help**: Generated initial Pydantic model structure
- **What I Changed**: 
  - AI used Pydantic v1 syntax initially
  - Updated to Pydantic v2 with `model_validator` and `ConfigDict`
  - Added custom validators for business rules

### 4. **FastAPI Endpoint Structure**
- **AI Help**: Generated basic FastAPI app structure
- **What I Changed**:
  - AI forgot to include `python-multipart` dependency for file uploads
  - Added proper error handling and CORS configuration
  - Enhanced response formats to match requirements

### 5. **React Frontend Components**
- **AI Help**: Generated initial React component structure
- **What I Changed**:
  - AI's initial design was too basic
  - Enhanced with proper Tailwind styling, loading states, error handling
  - Added currency formatting and better UX

## Example of Incorrect AI Suggestion

### Issue: Date Parsing Logic

**AI Suggested:**
```python
def parse_date(date_str: str) -> Optional[date]:
    # AI suggested using datetime.strptime with hardcoded formats
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None
```

**Problem**: This approach is too rigid and doesn't handle variations in date formats found in real PDFs (e.g., "Jan 15, 2024", "15-01-2024", etc.)

**What I Did Instead:**
```python
def parse_date(date_str: str) -> Optional[str]:
    if not date_str:
        return None
    try:
        # Use python-dateutil for flexible parsing
        date_obj = date_parser.parse(date_str, dayfirst=True, fuzzy=True)
        return date_obj.date().isoformat()
    except (ValueError, TypeError):
        return None
```

**Why Better**: `python-dateutil` handles many date format variations automatically and is more robust for real-world PDF extraction.

## Other AI Corrections

1. **CLI Error Handling**: AI's initial CLI didn't have proper exception handling - I added comprehensive try/except blocks
2. **Validation Error Messages**: AI's error messages were too technical - I made them more user-friendly while keeping technical details
3. **Frontend API Integration**: AI forgot to handle loading states properly - I added proper async/await handling with loading indicators

## Overall Assessment

AI was very helpful for:
- Generating boilerplate code
- Suggesting library choices
- Creating initial structure

AI needed correction for:
- Handling edge cases in real-world data
- Understanding specific library version differences (Pydantic v1 vs v2)
- Missing dependencies
- UX considerations

## Learning Points

1. Always verify AI suggestions against actual library documentation
2. Test with real data, not just examples
3. Consider edge cases that AI might miss
4. Review dependencies carefully
5. Think about user experience, not just functionality

