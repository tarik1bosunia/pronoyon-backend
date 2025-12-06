# Quick Start: Group Support Implementation

## Summary
Backend models have been updated to support optional groups (Science, Arts, Commerce) for classes like HSC and Admission, while keeping other classes group-free.

## Files Changed

### ✅ New Files Created:
1. **`apps/questions/models/group.py`** - New Group model
2. **`apps/questions/MIGRATION_GUIDE_GROUPS.md`** - Complete migration guide
3. **`apps/questions/MODEL_STRUCTURE.md`** - Detailed model documentation

### ✅ Files Modified:
1. **`apps/questions/models/class_model.py`**
   - Added `has_groups` boolean field
   - Updated docstring

2. **`apps/questions/models/subject.py`**
   - Added `group` ForeignKey field (optional)
   - Updated `unique_together` constraint
   - Updated `__str__` method to show group info
   - Added database index

3. **`apps/questions/models/__init__.py`**
   - Added Group import and export

## Quick Migration Steps

### 1. Create and Apply Migration
```bash
cd pronoyon-backend
python manage.py makemigrations questions
python manage.py migrate questions
```

### 2. Setup Initial Groups (Run in Django Shell)
```bash
python manage.py shell
```

```python
from apps.questions.models import Class, Group

# Find HSC class
hsc = Class.objects.filter(name__icontains='HSC').first()
if hsc:
    hsc.has_groups = True
    hsc.save()
    
    # Create groups
    groups = [
        {'name': 'Science', 'type': Group.SCIENCE, 'code': 'SCI', 'order': 1},
        {'name': 'Arts', 'type': Group.ARTS, 'code': 'ARTS', 'order': 2},
        {'name': 'Commerce', 'type': Group.COMMERCE, 'code': 'COM', 'order': 3},
    ]
    
    for g in groups:
        Group.objects.get_or_create(
            class_level=hsc,
            name=g['name'],
            defaults={'group_type': g['type'], 'code': g['code'], 'order': g['order']}
        )
    
    print(f"✅ Created {Group.objects.filter(class_level=hsc).count()} groups for HSC")

# Repeat for Admission
admission = Class.objects.filter(name__icontains='Admission').first()
if admission:
    admission.has_groups = True
    admission.save()
    
    for g in groups:
        Group.objects.get_or_create(
            class_level=admission,
            name=g['name'],
            defaults={'group_type': g['type'], 'code': g['code'], 'order': g['order']}
        )
    
    print(f"✅ Created {Group.objects.filter(class_level=admission).count()} groups for Admission")

print("\n✅ Migration complete!")
```

## Model Structure

```
Class (has_groups: Boolean)
  ├─→ Group (optional, only if has_groups=True)
  │     └─→ Subject (with group)
  │           └─→ Chapter → Topic → Question
  └─→ Subject (direct, if group not specified)
        └─→ Chapter → Topic → Question
```

## Example Usage

### Classes WITHOUT Groups (Class 6-10):
```python
class_6 = Class.objects.get(name='Class 6')
class_6.has_groups  # False

# Subjects directly under class
Subject.objects.create(
    class_level=class_6,
    name='Bangla',
    group=None  # No group
)
```

### Classes WITH Groups (HSC, Admission):
```python
hsc = Class.objects.get(name='HSC')
hsc.has_groups  # True

# Get groups
science = Group.objects.get(class_level=hsc, name='Science')
arts = Group.objects.get(class_level=hsc, name='Arts')

# Create subjects with groups
Subject.objects.create(
    class_level=hsc,
    group=science,
    name='Physics'
)

Subject.objects.create(
    class_level=hsc,
    group=arts,
    name='History'
)
```

## Query Examples

```python
# Get all subjects for HSC Science
Subject.objects.filter(class_level__name='HSC', group__name='Science')

# Get all subjects for Class 6 (no group)
Subject.objects.filter(class_level__name='Class 6', group__isnull=True)

# Get all groups for a class
Group.objects.filter(class_level__name='HSC')

# Check if class has groups
if my_class.has_groups:
    groups = my_class.groups.all()
```

## Next Steps

### Backend:
- [ ] Create and run migrations
- [ ] Setup initial groups for HSC and Admission
- [ ] Update serializers to include group field
- [ ] Update API views to filter by group
- [ ] Add group endpoints if needed
- [ ] Update tests

### Frontend:
- [ ] Add group selection dropdown (conditional on `has_groups`)
- [ ] Update subject filtering to include group
- [ ] Update UI flow: Class → [Group?] → Subject → Chapter
- [ ] Handle both grouped and non-grouped classes

## Testing

```python
# Test class without groups
class_6 = Class.objects.get(name='Class 6')
assert class_6.has_groups == False
assert class_6.groups.count() == 0

# Test class with groups
hsc = Class.objects.get(name='HSC')
assert hsc.has_groups == True
assert hsc.groups.count() == 3

# Test subject with group
physics = Subject.objects.get(name='Physics', class_level=hsc)
assert physics.group.name == 'Science'
assert str(physics) == 'HSC - Science - Physics'

# Test subject without group
bangla = Subject.objects.get(name='Bangla', class_level=class_6)
assert bangla.group is None
assert str(bangla) == 'Class 6 - Bangla'
```

## Documentation

- 📄 **MIGRATION_GUIDE_GROUPS.md** - Complete migration guide with API examples
- 📄 **MODEL_STRUCTURE.md** - Detailed model structure and relationships
- 📄 **README.md** - This quick start guide

## Support

If you encounter issues:
1. Check migration files in `apps/questions/migrations/`
2. Review `MIGRATION_GUIDE_GROUPS.md` for detailed steps
3. Verify database constraints and indexes
4. Test with sample data before production deployment
