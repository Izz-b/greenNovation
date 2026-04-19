# Well-Being Page - Analysis & Implementation Guide

## 📊 Current Status

### ✅ What's Already Done

- **Beautiful UI Components**: Fully designed with:
  - Daily check-in widget (mood, sleep, focus)
  - Smart insights panel (AI-like recommendations)
  - Multiple chart types (line, donut, dual-axis)
  - Emotional timeline
  - Adaptive suggestions
  - Avatar tips
  - Responsive grid layout

- **Mock Data Structure**:
  - Weekly mood/sleep/focus/study data
  - Emotional timeline with timestamps
  - Smart insights logic based on check-in values
  - Realistic patterns and calculations

### ❌ What's Missing

- **Backend API Endpoints**: No readiness endpoints exposed
- **Frontend Hooks**: No API client hooks for fetching/posting data
- **Data Persistence**: Check-ins not saved to database
- **Real-time Sync**: No connection between frontend state and backend
- **User-specific Data**: All data is mock/session-scoped

---

## 🏗️ Architecture Overview

```
Well-Being Page (wellbeing.tsx)
    ├─ Local State (4 inputs)
    │  ├─ sleep: "bad" | "okay" | "great"
    │  ├─ focus: "low" | "medium" | "high"
    │  ├─ mood: "sad" | "neutral" | "happy"
    │  └─ journal: string (optional notes)
    │
    ├─ Computed Insights (client-side)
    │  └─ Smart recommendations based on check-in
    │
    └─ Mock Chart Data (hardcoded)
       ├─ moodWeek, sleepWeek, focusWeek, studyWeek
       └─ TIMELINE emotional moments

API Hooks (to be created)
    ├─ useReadinessTodaySubmit() → POST /readiness/checkin
    ├─ useReadinessHistory() → GET /readiness/history
    ├─ useReadinessCurrent() → GET /readiness/current
    └─ useReadinessInsights() → GET /readiness/insights

Backend Routes (to be created)
    ├─ POST /api/readiness/checkin
    ├─ GET /api/readiness/current
    ├─ GET /api/readiness/history
    └─ GET /api/readiness/insights

Database (to store)
    └─ CheckinRecords
       ├─ user_id
       ├─ date
       ├─ sleep, focus, mood, journal
       └─ timestamp
```

---

## 🎯 Implementation Steps

### Phase 1: Create Backend API Endpoints (2-3 hours)

#### 1.1 Create Readiness Schema Models

**File**: `backend/app/schemas/readiness.py`

```python
from pydantic import BaseModel
from datetime import datetime

class CheckinRequest(BaseModel):
    sleep: str  # "bad" | "okay" | "great"
    focus: str  # "low" | "medium" | "high"
    mood: str   # "sad" | "neutral" | "happy"
    journal: str | None = None
    date: datetime | None = None  # defaults to today

class CheckinResponse(BaseModel):
    id: str
    date: str
    sleep: str
    focus: str
    mood: str
    journal: str | None
    created_at: datetime

class ReadinessHistoryResponse(BaseModel):
    data: list[CheckinResponse]
    week_summary: dict  # aggregated stats
```

#### 1.2 Create Readiness Service

**File**: `backend/app/services/readiness_service.py`

```python
from datetime import datetime, timedelta
from collections import defaultdict

# In-memory for now (will migrate to DB later)
_checkins: dict[str, list[dict]] = defaultdict(list)

async def submit_checkin(user_id: str, req: CheckinRequest) -> CheckinResponse:
    """Store daily check-in"""
    checkin = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "date": (req.date or datetime.utcnow()).isoformat(),
        "sleep": req.sleep,
        "focus": req.focus,
        "mood": req.mood,
        "journal": req.journal,
        "created_at": datetime.utcnow()
    }
    _checkins[user_id].append(checkin)
    return CheckinResponse(**checkin)

async def get_history(user_id: str, days: int = 7) -> ReadinessHistoryResponse:
    """Get last N days of check-ins"""
    checkins = _checkins.get(user_id, [])
    recent = checkins[-days:] if len(checkins) > days else checkins

    # Compute weekly summary
    mood_counts = {"happy": 0, "neutral": 0, "sad": 0}
    for c in recent:
        mood_counts[c["mood"]] += 1

    total = len(recent) or 1
    week_summary = {
        "happy_pct": round(mood_counts["happy"] / total * 100),
        "neutral_pct": round(mood_counts["neutral"] / total * 100),
        "sad_pct": round(mood_counts["sad"] / total * 100),
        "avg_sleep": "good",  # compute from data
        "avg_focus": "medium"  # compute from data
    }

    return ReadinessHistoryResponse(
        data=[CheckinResponse(**c) for c in recent],
        week_summary=week_summary
    )

async def get_today_checkin(user_id: str) -> CheckinResponse | None:
    """Get today's check-in (if exists)"""
    today = datetime.utcnow().date()
    checkins = _checkins.get(user_id, [])
    for c in checkins:
        if c["date"].startswith(today.isoformat()):
            return CheckinResponse(**c)
    return None
```

#### 1.3 Create Readiness Routes

**File**: `backend/app/api/routes/readiness.py`

```python
from fastapi import APIRouter, Query, HTTPException
from backend.app.schemas.readiness import CheckinRequest, CheckinResponse, ReadinessHistoryResponse
from backend.app.services import readiness_service

router = APIRouter(tags=["readiness"], prefix="/api/readiness")

@router.post("/checkin", response_model=CheckinResponse)
async def submit_checkin(req: CheckinRequest) -> CheckinResponse:
    """Submit daily well-being check-in"""
    # TODO: get user_id from auth token
    user_id = "default_user"
    return await readiness_service.submit_checkin(user_id, req)

@router.get("/current", response_model=CheckinResponse | None)
async def get_today() -> CheckinResponse | None:
    """Get today's check-in (if already submitted)"""
    user_id = "default_user"
    return await readiness_service.get_today_checkin(user_id)

@router.get("/history", response_model=ReadinessHistoryResponse)
async def get_history(days: int = Query(7, ge=1, le=90)) -> ReadinessHistoryResponse:
    """Get historical check-ins"""
    user_id = "default_user"
    return await readiness_service.get_history(user_id, days)
```

#### 1.4 Register Routes in Main App

**File**: `backend/app/main.py` (add import)

```python
from backend.app.api.routes import readiness
# ... in app setup:
app.include_router(readiness.router)
```

---

### Phase 2: Create Frontend Hooks (1-2 hours)

#### 2.1 Create useReadiness Hook

**File**: `frontend/src/hooks/useReadiness.tsx`

```typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

interface Checkin {
  id: string;
  date: string;
  sleep: 'bad' | 'okay' | 'great';
  focus: 'low' | 'medium' | 'high';
  mood: 'sad' | 'neutral' | 'happy';
  journal?: string;
  created_at: string;
}

interface WeeklySummary {
  happy_pct: number;
  neutral_pct: number;
  sad_pct: number;
  avg_sleep: string;
  avg_focus: string;
}

// ─── Submit Today's Check-in ───
export const useSubmitCheckin = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      sleep: string;
      focus: string;
      mood: string;
      journal?: string;
    }) => {
      const res = await fetch('/api/readiness/checkin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error('Failed to submit check-in');
      return res.json() as Promise<Checkin>;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['readiness', 'today'] });
      queryClient.invalidateQueries({ queryKey: ['readiness', 'history'] });
    },
  });
};

// ─── Get Today's Check-in ───
export const useReadinessToday = () => {
  return useQuery({
    queryKey: ['readiness', 'today'],
    queryFn: async () => {
      const res = await fetch('/api/readiness/current');
      if (!res.ok) return null;
      return res.json() as Promise<Checkin | null>;
    },
  });
};

// ─── Get Weekly History ───
export const useReadinessHistory = (days: number = 7) => {
  return useQuery({
    queryKey: ['readiness', 'history', days],
    queryFn: async () => {
      const res = await fetch(`/api/readiness/history?days=${days}`);
      if (!res.ok) throw new Error('Failed to fetch history');
      return res.json();
    },
    select: (data) => ({
      checkins: data.data as Checkin[],
      summary: data.week_summary as WeeklySummary,
    }),
  });
};
```

---

### Phase 3: Connect Well-Being Page (2-3 hours)

#### 3.1 Update Well-Being Page Component

**File**: `frontend/src/routes/wellbeing.tsx`

Key changes:

1. Import the hooks
2. Replace local state with server state
3. Update mock data with real data
4. Add loading/error states
5. Add submit handlers

```typescript
// At top, add imports:
import { useSubmitCheckin, useReadinessToday, useReadinessHistory } from "@/hooks/useReadiness";
import { useEffect } from "react";

// In WellbeingPage():
export function WellbeingPage() {
  const [sleep, setSleep] = useState<string | null>(null);
  const [focus, setFocus] = useState<string | null>(null);
  const [mood, setMood] = useState<string | null>(null);
  const [journal, setJournal] = useState("");

  // NEW: Fetch existing data
  const { data: todayCheckin, isLoading: loadingToday } = useReadinessToday();
  const { data: history } = useReadinessHistory(7);
  const { mutate: submitCheckin, isPending } = useSubmitCheckin();

  // NEW: Pre-fill if already checked in today
  useEffect(() => {
    if (todayCheckin) {
      setSleep(todayCheckin.sleep);
      setFocus(todayCheckin.focus);
      setMood(todayCheckin.mood);
      setJournal(todayCheckin.journal || "");
    }
  }, [todayCheckin]);

  const checkedIn = sleep && focus && mood;

  // NEW: Handle submit
  const handleSubmitCheckin = () => {
    if (checkedIn) {
      submitCheckin({
        sleep,
        focus,
        mood,
        journal: journal || undefined,
      });
    }
  };

  // NEW: Use real data instead of mock
  const moodWeek = history?.checkins
    .map((c) => c.mood === "happy" ? 3 : c.mood === "neutral" ? 2 : 1)
    .concat(Array(7).fill(2))
    .slice(-7) || [2, 3, 2, 2, 3, 3, 3];

  const emotionDist = useMemo(() => {
    if (!history) {
      return { happy: 40, neutral: 40, sad: 20 };
    }
    const total = history.checkins.length || 1;
    const happy = history.checkins.filter((c) => c.mood === "happy").length;
    const neutral = history.checkins.filter((c) => c.mood === "neutral").length;
    const sad = history.checkins.filter((c) => c.mood === "sad").length;

    return {
      happy: Math.round((happy / total) * 100),
      neutral: Math.round((neutral / total) * 100),
      sad: Math.round((sad / total) * 100),
    };
  }, [history]);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* ... header ... */}

      {/* Daily Check-in - ADD SUBMIT BUTTON */}
      <section className="rounded-3xl bg-card border border-border p-6 lg:p-8 shadow-card">
        {/* ... existing check-in UI ... */}
        <div className="mt-6 flex gap-2">
          <button
            onClick={handleSubmitCheckin}
            disabled={!checkedIn || isPending}
            className="flex-1 rounded-xl gradient-primary text-primary-foreground px-4 py-2.5 font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isPending ? "Saving..." : "Save Check-in"}
          </button>
          {todayCheckin && (
            <span className="text-xs text-success flex items-center gap-1">
              ✓ Saved today
            </span>
          )}
        </div>
      </section>

      {/* Use real emotion distribution */}
      <EmotionDonut
        happy={emotionDist.happy}
        neutral={emotionDist.neutral}
        sad={emotionDist.sad}
      />

      {/* ... rest of page ... */}
    </div>
  );
}
```

---

## 📋 Detailed Component Breakdown

### Check-in Widget

```
Input Fields (3 columns):
├─ Sleep Quality (bad/okay/great)
├─ Focus Level (low/medium/high)
└─ Mood (sad/neutral/happy)

Journal Note (optional):
└─ Text input for context

Save Button:
└─ Submits all to backend
```

### Smart Insights Panel

Logic already implemented:

- ✅ Focus high + sleep low → warning
- ✅ Mood improved → positive
- ✅ Mood sad → supportive
- ✅ Sleep great + focus good → celebrate
- ✅ Focus low → suggest Pomodoro

### Charts & Visualizations

**Weekly Mood (Line Chart)**

- Data: moodWeek (mapped to numeric: happy=3, neutral=2, sad=1)
- Shows trend over 7 days
- Color coded

**Emotion Mix (Donut Chart)**

- Breakdown: happy %, neutral %, sad %
- Computed from week's check-ins

**Sleep vs Focus (Dual-axis Chart)**

- Left Y: Sleep hours
- Right Y: Focus level
- Shows correlation

**Study Intensity (Bar Chart)**

- Hours studied per day
- Shows consistency/workload

**Emotional Timeline**

- Hourly snapshots with emoji + note
- Shows mood shifts throughout day

---

## 🔗 Data Flow

```
1. User fills check-in (sleep, focus, mood, journal)
   ↓
2. Click "Save Check-in"
   ↓
3. Frontend: useSubmitCheckin() → POST /api/readiness/checkin
   ↓
4. Backend: readiness_service.submit_checkin()
   ├─ Save to in-memory dict (or DB later)
   └─ Return CheckinResponse
   ↓
5. Frontend: Query invalidates
   ├─ useReadinessToday() refetches
   └─ useReadinessHistory() refetches
   ↓
6. Page re-renders with real data
   ├─ Charts update
   ├─ Insights recompute
   └─ "✓ Saved today" badge shows
```

---

## 🎨 UI Components to Update

### 1. Daily Check-in Section

- [ ] Pre-fill from today's data (if exists)
- [ ] Add "Save Check-in" button
- [ ] Show loading state while saving
- [ ] Show success badge after save
- [ ] Disable until all 3 fields filled

### 2. Smart Insights Section

- [ ] Already works! Just needs real data

### 3. Charts

- [ ] Weekly Mood: Use real checkins
- [ ] Emotion Mix: Use real counts
- [ ] Sleep vs Focus: Derive from checkins (estimate focus from data)
- [ ] Study Intensity: Use session data (integration task)

### 4. Emotional Timeline

- [ ] Fetch actual daily timeline events
- [ ] Currently hardcoded for demo

### 5. Avatar Tip

- [ ] Already works! Generates contextual tips

---

## 📊 Data Model

### Checkin Record

```json
{
  "id": "uuid",
  "user_id": "user123",
  "date": "2026-04-19",
  "sleep": "great",
  "focus": "high",
  "mood": "happy",
  "journal": "Had a great study session!",
  "created_at": "2026-04-19T14:30:00Z"
}
```

### Weekly Summary

```json
{
  "happy_pct": 60,
  "neutral_pct": 30,
  "sad_pct": 10,
  "avg_sleep": "great",
  "avg_focus": "medium",
  "total_study_hours": 28.5,
  "consistency_streak": 5
}
```

---

## 🔧 Environment Setup

### Backend

1. Create files in `backend/app/`
2. Add routes to `backend/app/main.py`
3. Start: `uvicorn backend.app.main:app --reload --port 8001`

### Frontend

1. Create hook in `frontend/src/hooks/`
2. Update `frontend/src/routes/wellbeing.tsx`
3. Start: `cd frontend && npm run dev`

### Test

- Navigate to http://localhost:5173/wellbeing
- Fill check-in
- Click Save
- Check browser DevTools Network tab for `/api/readiness/checkin` POST

---

## 🚀 Implementation Checklist

### Backend

- [ ] Create `backend/app/schemas/readiness.py`
- [ ] Create `backend/app/services/readiness_service.py`
- [ ] Create `backend/app/api/routes/readiness.py`
- [ ] Add router to `backend/app/main.py`
- [ ] Test endpoints with Swagger UI

### Frontend

- [ ] Create `frontend/src/hooks/useReadiness.tsx`
- [ ] Update `frontend/src/routes/wellbeing.tsx`
- [ ] Add submit button and handlers
- [ ] Connect charts to real data
- [ ] Add loading/error states
- [ ] Test form submission

### Testing

- [ ] Submit check-in from UI
- [ ] Verify saved in backend
- [ ] Page refreshes → pre-fills
- [ ] Charts show real data
- [ ] Try different days

---

## 💾 Future Enhancements

### Phase 2 (Database)

- Migrate from in-memory to persistent storage
- Add user authentication
- Multi-user support
- Historical data queries

### Phase 3 (Analytics)

- AI insights from patterns
- Recommendations based on correlations
- Alerts for concerning patterns
- Export data

### Phase 4 (Integration)

- Pull session data for study intensity
- Link readiness to learning page
- Show alerts on dashboard
- Notifications for check-in reminders

---

## 📚 File Summary

| File                                        | Purpose         | Status     |
| ------------------------------------------- | --------------- | ---------- |
| `backend/app/schemas/readiness.py`          | Data models     | **TODO**   |
| `backend/app/services/readiness_service.py` | Business logic  | **TODO**   |
| `backend/app/api/routes/readiness.py`       | API endpoints   | **TODO**   |
| `backend/app/main.py`                       | Register routes | **UPDATE** |
| `frontend/src/hooks/useReadiness.tsx`       | React hooks     | **TODO**   |
| `frontend/src/routes/wellbeing.tsx`         | Page component  | **UPDATE** |

---

## 🎯 Quick Start (TL;DR)

**Step 1: Create Backend** (30 min)

```bash
# Create 3 files as shown above
# Run backend: uvicorn backend.app.main:app --reload --port 8001
# Test: http://127.0.0.1:8001/docs → POST /api/readiness/checkin
```

**Step 2: Create Frontend Hook** (15 min)

```bash
# Create frontend/src/hooks/useReadiness.tsx
# Add 3 hooks: useSubmitCheckin, useReadinessToday, useReadinessHistory
```

**Step 3: Update Well-Being Page** (30 min)

```bash
# Import hooks in wellbeing.tsx
# Replace mock data with real data
# Add submit button and handlers
```

**Step 4: Test** (10 min)

```bash
# Go to http://localhost:5173/wellbeing
# Fill check-in → Save
# Refresh page → data persists
# Charts show real data
```

---

**Ready to start? Pick a phase and let me guide you through each file!** 🚀
