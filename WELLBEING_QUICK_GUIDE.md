# Well-Being Page - Quick Visual Overview

## Current State vs. Target State

### 🔴 CURRENT (Mock Data Only)

```
┌─────────────────────────────────────┐
│    Well-Being Page (wellbeing.tsx)  │
├─────────────────────────────────────┤
│                                     │
│  ✓ Beautiful UI (100% complete)    │
│  ✓ Local state (useState)           │
│  ✓ Mock data (hardcoded)            │
│  ✗ No backend connection            │
│  ✗ No data persistence              │
│  ✗ No real user data                │
│                                     │
│  Charts show: FAKE DATA             │
│  Check-in doesn't save anywhere     │
│  Page refresh = data lost           │
│                                     │
└─────────────────────────────────────┘
```

### 🟢 TARGET (Connected & Persistent)

```
┌─────────────────────────────────────┐
│    Well-Being Page (wellbeing.tsx)  │
├─────────────────────────────────────┤
│                                     │
│  ✓ Beautiful UI (100%)              │
│  ✓ Real state (from API)            │
│  ✓ Real user data                   │
│  ✓ Backend connection               │
│  ✓ Data persisted in memory/DB      │
│  ✓ Multi-day history                │
│                                     │
│  Charts show: REAL DATA             │
│  Check-in automatically saves       │
│  Page refresh = data restored       │
│                                     │
│        ↓ Uses Hooks ↓               │
│  useSubmitCheckin()                 │
│  useReadinessToday()                │
│  useReadinessHistory()              │
│                                     │
│        ↓ Calls API ↓                │
│  POST   /api/readiness/checkin      │
│  GET    /api/readiness/current      │
│  GET    /api/readiness/history      │
│                                     │
└─────────────────────────────────────┘
          ↓
┌─────────────────────────────────────┐
│      Backend (backend.app)          │
├─────────────────────────────────────┤
│                                     │
│  readiness_service.py               │
│  ├─ submit_checkin()                │
│  ├─ get_today_checkin()             │
│  └─ get_history()                   │
│                                     │
│  ↓ Stores/Retrieves Data ↓          │
│                                     │
│  In-Memory (Phase 1)                │
│  └─ _checkins dict                  │
│                                     │
│  Database (Phase 2)                 │
│  └─ CheckinRecords table            │
│                                     │
└─────────────────────────────────────┘
```

---

## File Creation Order (Recommended)

### 🔵 PHASE 1: Backend (30-45 min)

```
backend/app/
├── schemas/
│   └── readiness.py ...................... NEW (CheckinRequest, CheckinResponse)
│
├── services/
│   └── readiness_service.py .............. NEW (submit, get_today, get_history)
│
├── api/routes/
│   ├── readiness.py ...................... NEW (@router.post, @router.get)
│   └── [+ register in main.py]
│
└── main.py ............................. EDIT (add readiness router)
```

**Result**: 3 POST/GET endpoints ready

### 🟠 PHASE 2: Frontend Hooks (15-20 min)

```
frontend/src/
└── hooks/
    └── useReadiness.tsx .................. NEW (3 hooks)
        ├─ useSubmitCheckin()
        ├─ useReadinessToday()
        └─ useReadinessHistory()
```

**Result**: Ready to fetch/submit data

### 🟡 PHASE 3: Connect Page (30-45 min)

```
frontend/src/routes/
└── wellbeing.tsx ....................... EDIT
    ├─ Import hooks
    ├─ Replace mock data with real
    ├─ Add submit button
    ├─ Add loading states
    └─ Add error handling
```

**Result**: Fully working well-being page

---

## User Journey (After Implementation)

```
User visits /wellbeing
       ↓
Page loads → useReadinessToday() fetches today's check-in
       ↓
─────────────────────────────────
If checked in today:
  → Pre-fill all 3 fields
  → Show "✓ Saved today" badge
─────────────────────────────────
       ↓
User fills out check-in (or updates existing)
  - Sleep: "Great" ✓
  - Focus: "High" ✓
  - Mood: "Happy" ✓
  - Journal: "Great study session!"
       ↓
Clicks "Save Check-in" button
       ↓
useSubmitCheckin() sends:
  POST /api/readiness/checkin
  {
    "sleep": "great",
    "focus": "high",
    "mood": "happy",
    "journal": "Great study session!"
  }
       ↓
Backend saves to memory (_checkins)
  → Returns CheckinResponse
       ↓
Frontend queries invalidate
  → useReadinessToday() refetches
  → useReadinessHistory() refetches
       ↓
Page re-renders with NEW data
  ✓ Charts update
  ✓ Insights recompute
  ✓ Success badge shows
```

---

## Backend Flow Diagram

```
POST /api/readiness/checkin
  ↓
readiness.py (route handler)
  ↓
readiness_service.py
  ├─ receive: CheckinRequest
  ├─ create: Checkin dict with:
  │  ├─ id (uuid)
  │  ├─ date (today)
  │  ├─ sleep/focus/mood/journal
  │  └─ created_at (now)
  │
  ├─ store in: _checkins[user_id].append()
  │
  └─ return: CheckinResponse
       ↓
readiness.py (sends back)
  ↓
Frontend receives JSON
  ↓
useSubmitCheckin() success
  ├─ Invalidate queries
  └─ Page re-renders
```

---

## Frontend Data Flow

```
wellbeing.tsx Component
  ├─ useState(sleep, focus, mood, journal)
  │
  ├─ useReadinessToday()
  │  └─ GET /api/readiness/current
  │     └─ Returns: todayCheckin or null
  │
  ├─ useReadinessHistory(7)
  │  └─ GET /api/readiness/history?days=7
  │     └─ Returns: { data: [...], week_summary: {...} }
  │
  └─ useSubmitCheckin()
     └─ POST /api/readiness/checkin
        └─ Returns: CheckinResponse
           └─ Invalidates above 2 queries

useEffect hooks:
  └─ If todayCheckin exists → pre-fill form

Render flow:
  ├─ Check-in widget
  │  └─ Saves on button click
  │
  ├─ Charts
  │  ├─ moodWeek = history.map(c => c.mood)
  │  ├─ emotionDist = computed from history
  │  └─ sleepWeek = derived from history
  │
  └─ Insights
     └─ Computed from current form values
```

---

## Key Integration Points

```
Well-Being Page
    ├─ Displays: mood, sleep, focus checks
    ├─ Stores: daily check-ins
    ├─ Analyzes: 7-day trends
    └─ Recommends: adaptive suggestions

↓↓↓ CONNECTS TO ↓↓↓

Dashboard (index.tsx)
    ├─ Uses: readiness scores
    ├─ Displays: readiness card
    └─ Shows: energy level

Learning Page (learning.tsx)
    ├─ Uses: student readiness
    ├─ Adjusts: difficulty
    └─ Tunes: response depth

Workspace (workspace.tsx)
    ├─ Uses: focus level
    ├─ Suggests: break timing
    └─ Adapts: session length
```

---

## Testing Checklist

### Backend Testing

- [ ] Run backend: `uvicorn backend.app.main:app --reload --port 8001`
- [ ] Go to: http://127.0.0.1:8001/docs
- [ ] Try POST /api/readiness/checkin:
  ```json
  {
    "sleep": "great",
    "focus": "high",
    "mood": "happy"
  }
  ```
- [ ] Should return: CheckinResponse with id, date, created_at
- [ ] Try GET /api/readiness/current → returns same data
- [ ] Try GET /api/readiness/history → returns list with summary

### Frontend Testing

- [ ] Run frontend: `cd frontend && npm run dev`
- [ ] Go to: http://localhost:5173/wellbeing
- [ ] Page loads (no errors in console)
- [ ] Fill check-in form
- [ ] Click "Save Check-in"
- [ ] Check Network tab → see POST to /api/readiness/checkin
- [ ] Page shows "✓ Saved today" badge
- [ ] Refresh page → form pre-fills with saved data
- [ ] Charts show consistent data

### Integration Testing

- [ ] Submit check-in from UI
- [ ] Verify in backend (check \_checkins dict)
- [ ] Submit multiple times
- [ ] Verify history grows
- [ ] Charts update with new data
- [ ] Insights change based on values

---

## Common Issues & Solutions

### Issue: "Module not found" in backend

```
❌ from backend.app.api.routes import readiness
✓ Actually: from backend.app.api.routes import readiness (in main.py)

Solution: Make sure __init__.py exists in each folder
```

### Issue: CORS error in frontend

```
❌ POST http://localhost:8001/api/readiness/checkin → CORS blocked

Solution: Backend CORS should already be configured in main.py
  - Check: app.add_middleware(CORSMiddleware, ...)
  - Verify: allow_origins includes http://localhost:5173
```

### Issue: "Cannot read property 'map' of undefined"

```
❌ moodWeek.map() fails

Solution: Add fallback in wellbeing.tsx:
  const moodWeek = history?.checkins?.map(...) || [2,3,2,2,3,3,3];
```

### Issue: Button doesn't submit

```
❌ Save button clicked but nothing happens

Solution: Check:
  1. checkedIn state is true (all 3 fields filled)
  2. isPending is false (not already submitting)
  3. submitCheckin is imported and working
  4. Backend is running on correct port
```

---

## Success Criteria ✅

After implementation, you should be able to:

1. ✅ Open well-being page
2. ✅ Fill out check-in (sleep, focus, mood, journal)
3. ✅ Click "Save Check-in"
4. ✅ See success message
5. ✅ Refresh page
6. ✅ Form still filled with same data
7. ✅ Submit multiple times
8. ✅ See history in charts
9. ✅ Charts update when data changes
10. ✅ No console errors

---

## Timeline Estimate

| Phase | Task                                  | Time | Total   |
| ----- | ------------------------------------- | ---- | ------- |
| 1     | Create `readiness.py` (schemas)       | 10m  | 10m     |
| 1     | Create `readiness_service.py` (logic) | 15m  | 25m     |
| 1     | Create `readiness.py` (routes)        | 10m  | 35m     |
| 1     | Update `main.py` (register)           | 5m   | 40m     |
| 1     | **TEST backend**                      | 10m  | 50m ⏱️  |
| 2     | Create `useReadiness.tsx` (hooks)     | 20m  | 70m     |
| 3     | Update `wellbeing.tsx` (page)         | 30m  | 100m    |
| 3     | Add submit button & handlers          | 10m  | 110m    |
| 3     | Connect charts to real data           | 15m  | 125m    |
| 3     | **TEST full integration**             | 15m  | 140m ⏱️ |

**Total: ~2.5 hours** (start to fully working) ✅

---

Ready to dive in? Start with **Phase 1: Backend** and let me know when you're ready for the next step!
