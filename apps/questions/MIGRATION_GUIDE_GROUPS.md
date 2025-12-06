# Database Migration Guide: Adding Group Support to Question Bank

## Overview
This migration adds support for optional groups (Science, Arts, Commerce) to the Question Bank system. Classes like HSC and Admission can have groups, while other classes remain group-free.

## Changes Made

### 1. New Model: `Group`
**File:** `apps/questions/models/group.py`

A new model to represent groups/streams within classes:
- Science (বিজ্ঞান)
- Arts/Humanities (মানবিক)
- Commerce/Business Studies (ব্যবসায় শিক্ষা)
- General

**Key Fields:**
- `class_level`: ForeignKey to Class
- `name`: Group name
- `group_type`: Predefined choices for common groups
- `has_groups`: Boolean flag on Class model

### 2. Updated Model: `Class`
**File:** `apps/questions/models/class_model.py`

Added field:
- `has_groups`: Boolean field (default=False) to indicate if the class supports groups

**Usage Examples:**
- HSC: `has_groups=True` → Can have Science, Arts, Commerce groups
- Admission: `has_groups=True` → Can have Science, Arts, Commerce groups
- Class 6-10: `has_groups=False` → No groups needed

### 3. Updated Model: `Subject`
**File:** `apps/questions/models/subject.py`

Added field:
- `group`: Optional ForeignKey to Group (null=True, blank=True)

Updated constraints:
- `unique_together`: Changed from `['class_level', 'name']` to `['class_level', 'group', 'name']`
- This allows same subject name in different groups (e.g., "Physics" in both Science and Arts if needed)

Updated `__str__` method to show group information when present.

## Migration Steps

### Step 1: Create Migrations
```bash
cd pronoyon-backend
python manage.py makemigrations questions
```

This will create migrations for:
1. Adding `Group` model
2. Adding `has_groups` field to `Class` model
3. Adding `group` field to `Subject` model
4. Updating unique constraints on `Subject` model

### Step 2: Review Migration Files
Check the generated migration files in `apps/questions/migrations/`

### Step 3: Apply Migrations
```bash
python manage.py migrate questions
```

### Step 4: Create Initial Groups for HSC and Admission Classes

Run this in Django shell or create a data migration:

```python
python manage.py shell
```

```python
from apps.questions.models import Class, Group

# Update existing classes to set has_groups flag
hsc = Class.objects.filter(name__icontains='HSC').first()
if hsc:
    hsc.has_groups = True
    hsc.save()
    
    # Create groups for HSC
    Group.objects.get_or_create(
        class_level=hsc,
        name='Science',
        defaults={
            'group_type': Group.SCIENCE,
            'code': 'SCI',
            'order': 1
        }
    )
    
    Group.objects.get_or_create(
        class_level=hsc,
        name='Arts',
        defaults={
            'group_type': Group.ARTS,
            'code': 'ARTS',
            'order': 2
        }
    )
    
    Group.objects.get_or_create(
        class_level=hsc,
        name='Commerce',
        defaults={
            'group_type': Group.COMMERCE,
            'code': 'COM',
            'order': 3
        }
    )

# Similarly for Admission class
admission = Class.objects.filter(name__icontains='Admission').first()
if admission:
    admission.has_groups = True
    admission.save()
    
    # Create groups for Admission
    Group.objects.get_or_create(
        class_level=admission,
        name='Science',
        defaults={
            'group_type': Group.SCIENCE,
            'code': 'SCI',
            'order': 1
        }
    )
    
    Group.objects.get_or_create(
        class_level=admission,
        name='Arts',
        defaults={
            'group_type': Group.ARTS,
            'code': 'ARTS',
            'order': 2
        }
    )
    
    Group.objects.get_or_create(
        class_level=admission,
        name='Commerce',
        defaults={
            'group_type': Group.COMMERCE,
            'code': 'COM',
            'order': 3
        }
    )
```

## Data Model Structure

### Before:
```
Class → Subject → Chapter → Topic → Question
```

### After:
```
Class (has_groups: bool)
  ├─→ Group (optional, only if has_groups=True)
  │     └─→ Subject
  │           └─→ Chapter → Topic → Question
  └─→ Subject (direct, if has_groups=False or group not specified)
        └─→ Chapter → Topic → Question
```

## API Impact

### Endpoints to Update:

1. **Subject List/Create:**
   - Add `group` field to serializer (optional)
   - Filter subjects by group when querying

2. **Class Details:**
   - Include `has_groups` field
   - Include related groups in response when `has_groups=True`

3. **New Group Endpoints (if needed):**
   - `GET /api/classes/{class_id}/groups/` - List groups for a class
   - `GET /api/groups/{group_id}/subjects/` - List subjects in a group

### Example API Responses:

**Class without Groups (e.g., Class 6):**
```json
{
  "id": "uuid",
  "name": "Class 6",
  "has_groups": false,
  "subjects": [
    {"id": "uuid", "name": "Bangla", "group": null},
    {"id": "uuid", "name": "English", "group": null}
  ]
}
```

**Class with Groups (e.g., HSC):**
```json
{
  "id": "uuid",
  "name": "HSC",
  "has_groups": true,
  "groups": [
    {
      "id": "uuid",
      "name": "Science",
      "group_type": "science",
      "subjects": [
        {"id": "uuid", "name": "Physics"},
        {"id": "uuid", "name": "Chemistry"}
      ]
    },
    {
      "id": "uuid",
      "name": "Arts",
      "group_type": "arts",
      "subjects": [
        {"id": "uuid", "name": "History"},
        {"id": "uuid", "name": "Civics"}
      ]
    }
  ]
}
```

## Frontend Updates Required

1. **Class Selection:**
   - Check `has_groups` field
   - If true, show group selection dropdown after class selection
   - If false, skip to subject selection

2. **Subject Filtering:**
   - Filter subjects by both class AND group (when group is selected)
   - Show all subjects for a class if no group is selected

3. **UI Flow:**
   ```
   Select Class → [If has_groups] Select Group → Select Subject → Select Chapter
   ```

## Backwards Compatibility

- ✅ Existing classes without groups continue to work (group field is optional)
- ✅ Existing subjects remain valid (group=null is allowed)
- ✅ No breaking changes to existing data
- ✅ New features are additive only

## Testing Checklist

- [ ] Create a class with `has_groups=True` and add groups
- [ ] Create subjects with and without groups
- [ ] Verify unique constraints work correctly
- [ ] Test subject filtering by class and group
- [ ] Ensure existing data (classes without groups) still works
- [ ] Test frontend dropdown logic for group selection
- [ ] Verify API responses include group information

## Rollback Plan

If issues occur:

```bash
python manage.py migrate questions <previous_migration_number>
```

This will revert the changes. Note: You may need to manually clean up any Group records created.

## Notes

- Groups are only required for classes where `has_groups=True`
- Most classes (6-10) won't have groups
- HSC and Admission classes typically have groups
- The system remains flexible for future group additions
- Group information is displayed in Subject's `__str__` method for better admin clarity
