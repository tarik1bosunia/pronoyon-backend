# Updated Backend Models Structure with Group Support

## Model Overview

### 1. Class Model
**Location:** `apps/questions/models/class_model.py`

```python
class Class(models.Model):
    id = UUIDField (PK)
    name = CharField (unique, max_length=100)
    code = CharField (unique, optional)
    description = TextField (optional)
    has_groups = BooleanField (default=False)  # NEW FIELD
    order = PositiveIntegerField
    created_by = ForeignKey → User
    created_at = DateTimeField
    updated_at = DateTimeField
    is_active = BooleanField
```

**Examples:**
- Class 6, 7, 8, 9, 10: `has_groups = False`
- HSC, Admission: `has_groups = True`

---

### 2. Group Model (NEW)
**Location:** `apps/questions/models/group.py`

```python
class Group(models.Model):
    id = UUIDField (PK)
    class_level = ForeignKey → Class
    name = CharField (max_length=100)
    code = CharField (optional)
    group_type = CharField (choices: science, arts, commerce, general)
    description = TextField (optional)
    order = PositiveIntegerField
    created_by = ForeignKey → User
    created_at = DateTimeField
    updated_at = DateTimeField
    is_active = BooleanField
    
    unique_together = [['class_level', 'name']]
```

**Examples:**
- HSC - Science (বিজ্ঞান)
- HSC - Arts (মানবিক)
- HSC - Commerce (ব্যবসায় শিক্ষা)

---

### 3. Subject Model (UPDATED)
**Location:** `apps/questions/models/subject.py`

```python
class Subject(models.Model):
    id = UUIDField (PK)
    class_level = ForeignKey → Class
    group = ForeignKey → Group (optional, null=True)  # NEW FIELD
    name = CharField (max_length=200)
    code = CharField (optional)
    description = TextField (optional)
    order = PositiveIntegerField
    created_by = ForeignKey → User
    created_at = DateTimeField
    updated_at = DateTimeField
    is_active = BooleanField
    
    unique_together = [['class_level', 'group', 'name']]  # UPDATED
```

**Examples:**
- Class 6 - Bangla (group = null)
- HSC - Science - Physics (group = Science)
- HSC - Arts - History (group = Arts)

---

### 4. Chapter Model (UNCHANGED)
**Location:** `apps/questions/models/chapter.py`

```python
class Chapter(models.Model):
    id = UUIDField (PK)
    subject = ForeignKey → Subject
    name = CharField (max_length=200)
    description = TextField (optional)
    order = PositiveIntegerField
    created_by = ForeignKey → User
    created_at = DateTimeField
    updated_at = DateTimeField
    is_active = BooleanField
    
    unique_together = [['subject', 'name']]
```

---

### 5. Topic Model (UNCHANGED)
**Location:** `apps/questions/models/topic.py`

```python
class Topic(models.Model):
    id = UUIDField (PK)
    chapter = ForeignKey → Chapter
    name = CharField (max_length=200)
    description = TextField (optional)
    order = PositiveIntegerField
    created_by = ForeignKey → User
    created_at = DateTimeField
    updated_at = DateTimeField
    is_active = BooleanField
```

---

## Model Relationships

### Complete Hierarchy:

```
┌─────────────────────────────────────────────────────────────────┐
│                           Class                                 │
│  (has_groups: Boolean)                                          │
│  - Class 6, 7, 8, 9, 10 → has_groups = False                   │
│  - HSC, Admission → has_groups = True                          │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ├───────────────┐
                          ↓               ↓
         ┌─────────────────────┐    ┌──────────────────┐
         │   Group (optional)  │    │  Subject (direct)│
         │  - Science          │    │  (no group)      │
         │  - Arts             │    └──────────────────┘
         │  - Commerce         │            ↓
         └─────────────────────┘      ┌──────────┐
                   ↓                  │ Chapter  │
         ┌──────────────────┐         └──────────┘
         │     Subject      │              ↓
         │  (with group)    │         ┌──────────┐
         └──────────────────┘         │  Topic   │
                   ↓                  └──────────┘
            ┌──────────┐                   ↓
            │ Chapter  │           ┌──────────────┐
            └──────────┘           │   Question   │
                 ↓                 └──────────────┘
            ┌──────────┐
            │  Topic   │
            └──────────┘
                 ↓
         ┌──────────────┐
         │   Question   │
         └──────────────┘
```

### Scenario 1: Class WITHOUT Groups (e.g., Class 6)
```
Class 6 (has_groups=False)
  └─→ Subject: Bangla (group=null)
        └─→ Chapter: কবিতা
              └─→ Topic: ছন্দ
                    └─→ Question
```

### Scenario 2: Class WITH Groups (e.g., HSC)
```
HSC (has_groups=True)
  ├─→ Group: Science
  │     ├─→ Subject: Physics
  │     │     └─→ Chapter: Mechanics
  │     │           └─→ Topic: Newton's Laws
  │     │                 └─→ Question
  │     └─→ Subject: Chemistry
  │           └─→ Chapter: Organic Chemistry
  │
  ├─→ Group: Arts
  │     ├─→ Subject: History
  │     │     └─→ Chapter: Ancient History
  │     └─→ Subject: Civics
  │
  └─→ Group: Commerce
        ├─→ Subject: Accounting
        └─→ Subject: Business Studies
```

---

## Database Schema Diagram

```sql
┌──────────────────────┐
│       Class          │
│──────────────────────│
│ id (UUID, PK)        │
│ name (VARCHAR)       │
│ has_groups (BOOLEAN) │ ← NEW
│ order (INT)          │
│ ...                  │
└──────────────────────┘
         │ 1
         │
         │ *
┌──────────────────────┐
│       Group          │ ← NEW MODEL
│──────────────────────│
│ id (UUID, PK)        │
│ class_level_id (FK)  │
│ name (VARCHAR)       │
│ group_type (VARCHAR) │
│ order (INT)          │
│ ...                  │
└──────────────────────┘
         │ 1
         │
         │ *
┌──────────────────────┐       ┌──────────────────────┐
│      Subject         │       │       Class          │
│──────────────────────│       │──────────────────────│
│ id (UUID, PK)        │   *   │ id (UUID, PK)        │
│ class_level_id (FK)  ├───────┤ ...                  │
│ group_id (FK) NULL   │ ← NEW │                      │
│ name (VARCHAR)       │       └──────────────────────┘
│ order (INT)          │
│ ...                  │
└──────────────────────┘
         │ 1
         │
         │ *
┌──────────────────────┐
│      Chapter         │
│──────────────────────│
│ id (UUID, PK)        │
│ subject_id (FK)      │
│ name (VARCHAR)       │
│ ...                  │
└──────────────────────┘
         │ 1
         │
         │ *
┌──────────────────────┐
│       Topic          │
│──────────────────────│
│ id (UUID, PK)        │
│ chapter_id (FK)      │
│ name (VARCHAR)       │
│ ...                  │
└──────────────────────┘
         │ 1
         │
         │ *
┌──────────────────────┐
│      Question        │
│──────────────────────│
│ id (UUID, PK)        │
│ topic_id (FK)        │
│ type (VARCHAR)       │
│ question_text (TEXT) │
│ ...                  │
└──────────────────────┘
```

---

## Key Features

### 1. Flexibility
- ✅ Classes can have groups or not (controlled by `has_groups` flag)
- ✅ Subjects can belong to a group or directly to a class
- ✅ No breaking changes to existing data

### 2. Data Integrity
- ✅ Unique constraint: `[class_level, group, name]` on Subject
- ✅ Allows same subject name in different groups
- ✅ Foreign key cascades maintain referential integrity

### 3. Query Patterns

**Get all subjects for HSC Science:**
```python
Subject.objects.filter(
    class_level__name='HSC',
    group__name='Science'
)
```

**Get all subjects for Class 6 (no group):**
```python
Subject.objects.filter(
    class_level__name='Class 6',
    group__isnull=True
)
```

**Get all groups for HSC:**
```python
Group.objects.filter(class_level__name='HSC')
```

**Check if a class has groups:**
```python
if my_class.has_groups:
    groups = my_class.groups.all()
else:
    subjects = my_class.subjects.filter(group__isnull=True)
```

---

## Migration Summary

### New Files:
1. ✅ `apps/questions/models/group.py` - New Group model

### Modified Files:
1. ✅ `apps/questions/models/class_model.py` - Added `has_groups` field
2. ✅ `apps/questions/models/subject.py` - Added `group` field
3. ✅ `apps/questions/models/__init__.py` - Added Group import

### Documentation:
1. ✅ `apps/questions/MIGRATION_GUIDE_GROUPS.md` - Complete migration guide

---

## Next Steps

1. **Run Migrations:**
   ```bash
   python manage.py makemigrations questions
   python manage.py migrate questions
   ```

2. **Create Initial Data:**
   - Set `has_groups=True` for HSC and Admission classes
   - Create Science, Arts, Commerce groups for those classes

3. **Update Serializers:**
   - Add `group` field to SubjectSerializer
   - Add `has_groups` to ClassSerializer
   - Create GroupSerializer

4. **Update Views/APIs:**
   - Filter subjects by group when applicable
   - Add group list endpoint

5. **Update Frontend:**
   - Show group dropdown when `has_groups=True`
   - Filter subjects based on selected group

---

## Benefits

✅ **Proper Organization:** Science, Arts, Commerce streams properly organized
✅ **Flexible Design:** Works for both grouped and non-grouped classes
✅ **Scalable:** Easy to add new groups or classes
✅ **Backwards Compatible:** Existing data continues to work
✅ **User-Friendly:** Clear hierarchy matches educational structure
