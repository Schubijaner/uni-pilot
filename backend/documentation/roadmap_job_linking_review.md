# Roadmap-to-Job Linking Review

## Current Implementation

Roadmaps are linked to jobs **indirectly** through `TopicField`:

1. **Data Model**: 
   - Jobs are `CareerTreeNode` objects with `is_leaf=True`
   - Jobs have an optional `topic_field_id` (nullable foreign key)
   - Roadmaps are stored with `topic_field_id` (NOT `job_id`)
   - The `Roadmap` model does not have a direct `job_id` field

2. **Linking Process** (in `roadmap_service.py:generate_roadmap_for_job()`):
   - Line 401: Gets `job.topic_field` (may be None)
   - Lines 402-409: If job has no `topic_field`, creates a new `TopicField` with name "Roadmap für {job.name}"
   - Line 413: Checks for existing roadmap using `topic_field.id`
   - Line 467: Creates roadmap with `topic_field_id=topic√√_field.id`

## Issues Found

### Issue 1: Job's topic_field_id Not Updated (FIXED ✅)
**Location**: `backend/api/services/roadmap_service.py:generate_roadmap_for_job()` lines 402-414

**Problem**: When a new `TopicField` is created for a job, the job's `topic_field_id` was NOT updated to reference it.

**Impact**: 
- First generation for a job without topic_field: Creates TopicField A, creates Roadmap linked to A
- Second generation for same job: Job still has `topic_field_id=NULL`, creates TopicField B, creates another Roadmap linked to B
- Result: Multiple topic_fields and roadmaps for the same job, wasting resources

**Fix Applied**: After creating the topic_field (line 409), the code now updates the job's topic_field_id:
```python
job.topic_field_id = topic_field.id
db.flush()
```
This ensures each job has a unique topic_field_id and prevents duplicate topic_fields for the same job.

### Issue 2: Potential Roadmap Sharing
**Problem**: If multiple jobs share the same `topic_field_id`, they will share the same roadmap.

**Impact**: 
- This may or may not be intentional
- If intentional, good for grouping similar jobs
- If not intentional, roadmaps won't be job-specific

**Status**: This appears intentional based on the design, but should be documented.

### Issue 3: Orphaned TopicFields
**Problem**: When topic_fields are created for jobs, they may accumulate over time if jobs are deleted or roadmaps are regenerated.

**Impact**: Database bloat with temporary topic_fields that may no longer be needed.

**Mitigation**: The deletion script should optionally clean up orphaned topic_fields that were created for jobs.

## Recommendations

1. **Fix Issue 1**: Update `job.topic_field_id` when creating a new topic_field for a job
2. **Add Direct Linking**: Consider adding `job_id` to the `Roadmap` model for direct linking (as noted in comment on line 412)
3. **Cleanup Script**: Create utility to find and optionally delete orphaned topic_fields

## Files Involved

- `backend/api/services/roadmap_service.py:generate_roadmap_for_job()` (lines 369-597)
- `backend/api/routers/roadmaps.py:generate_roadmap_for_job()` (lines 145-213)
- `backend/database/models.py`: `Roadmap` model (lines 213-232), `CareerTreeNode` model (lines 167-197)

