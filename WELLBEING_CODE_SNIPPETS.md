# Well-Being Page - Ready-to-Paste Code Snippets

## 📋 Use These Exact Files & Code

---

## PHASE 1: BACKEND (Copy-Paste Ready)

### File 1️⃣: `backend/app/schemas/readiness.py` (NEW)

```python
"""Pydantic models for well-being/readiness check-ins."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CheckinRequest(BaseModel):
    """Daily well-being check-in submission."""
    sleep: str = Field(..., description="Sleep quality: bad, okay, great")
    focus: str = Field(..., description="Focus level: low, medium, high")
    mood: str = Field(..., description="Mood: sad, neutral, happy")
    journal: Optional[str] = Field(None, description="Optional journal notes")
    date: Optional[datetime] = Field(None, description="Check-in date (defaults to today)")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "sleep": "great",
                "focus": "high",
                "mood": "happy",
                "journal": "Had a productive study session!"
            }]
        }
    }


class CheckinResponse(BaseModel):
    """Response after submitting a check-in."""
    id: str
    date: str
    sleep: str
    focus: str
    mood: str
    journal: Optional[str]
    created_at: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "date": "2026-04-19",
                "sleep": "great",
                "focus": "high",
                "mood": "happy",
                "journal": "Had a productive study session!",
                "created_at": "2026-04-19T14:30:00Z"
            }]
        }
    }


class WeeklySummary(BaseModel):
    """Weekly aggregated statistics."""
    happy_pct: int
    neutral_pct: int
    sad_pct: int
    avg_sleep: str
    avg_focus: str
    total_checkins: int


class ReadinessHistoryResponse(BaseModel):
    """Response for historical check-ins."""
    data: list[CheckinResponse]
    week_summary: WeeklySummary
```

---

### File 2️⃣: `backend/app/services/readiness_service.py` (NEW)

```python
"""Service layer for readiness/well-being check-ins."""

import uuid
from datetime import datetime
from collections import defaultdict
from typing import Optional

from backend.app.schemas.readiness import (
    CheckinRequest,
    CheckinResponse,
    ReadinessHistoryResponse,
    WeeklySummary,
)


# In-memory storage (will be replaced with database in Phase 2)
_checkins: dict[str, list[dict]] = defaultdict(list)


async def submit_checkin(user_id: str, req: CheckinRequest) -> CheckinResponse:
    """
    Submit a daily well-being check-in.

    Args:
        user_id: ID of the user submitting the check-in
        req: CheckinRequest with sleep, focus, mood, journal

    Returns:
        CheckinResponse with the stored check-in data
    """
    checkin = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "date": (req.date or datetime.utcnow()).strftime("%Y-%m-%d"),
        "sleep": req.sleep,
        "focus": req.focus,
        "mood": req.mood,
        "journal": req.journal,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    # Store in memory
    _checkins[user_id].append(checkin)

    return CheckinResponse(**checkin)


async def get_today_checkin(user_id: str) -> Optional[CheckinResponse]:
    """
    Get today's check-in if it exists.

    Args:
        user_id: ID of the user

    Returns:
        CheckinResponse if checked in today, None otherwise
    """
    today = datetime.utcnow().strftime("%Y-%m-%d")
    checkins = _checkins.get(user_id, [])

    for checkin in checkins:
        if checkin["date"] == today:
            return CheckinResponse(**checkin)

    return None


async def get_history(user_id: str, days: int = 7) -> ReadinessHistoryResponse:
    """
    Get historical check-ins and weekly summary.

    Args:
        user_id: ID of the user
        days: Number of days to retrieve (default 7)

    Returns:
        ReadinessHistoryResponse with checkins and week_summary
    """
    checkins = _checkins.get(user_id, [])

    # Get last N days
    recent = checkins[-days:] if len(checkins) > days else checkins

    # Compute weekly summary statistics
    mood_counts = {"happy": 0, "neutral": 0, "sad": 0}
    sleep_counts = {"great": 0, "okay": 0, "bad": 0}
    focus_counts = {"high": 0, "medium": 0, "low": 0}

    for checkin in recent:
        mood_counts[checkin.get("mood", "neutral")] += 1
        sleep_counts[checkin.get("sleep", "okay")] += 1
        focus_counts[checkin.get("focus", "medium")] += 1

    total = len(recent) or 1

    # Determine average mood/sleep/focus
    def get_average(counts: dict) -> str:
        """Return the most common value."""
        if not counts:
            return "neutral"
        return max(counts, key=counts.get)

    week_summary = WeeklySummary(
        happy_pct=round(mood_counts["happy"] / total * 100),
        neutral_pct=round(mood_counts["neutral"] / total * 100),
        sad_pct=round(mood_counts["sad"] / total * 100),
        avg_sleep=get_average(sleep_counts),
        avg_focus=get_average(focus_counts),
        total_checkins=len(recent),
    )

    return ReadinessHistoryResponse(
        data=[CheckinResponse(**c) for c in recent],
        week_summary=week_summary,
    )
```

---

### File 3️⃣: `backend/app/api/routes/readiness.py` (NEW)

```python
"""API routes for well-being/readiness check-ins."""

from typing import Optional
from fastapi import APIRouter, Query

from backend.app.schemas.readiness import (
    CheckinRequest,
    CheckinResponse,
    ReadinessHistoryResponse,
)
from backend.app.services import readiness_service


router = APIRouter(tags=["readiness"], prefix="/api/readiness")


@router.post("/checkin", response_model=CheckinResponse)
async def submit_checkin(req: CheckinRequest) -> CheckinResponse:
    """
    Submit a daily well-being check-in.

    Submit your sleep quality, focus level, mood, and optional journal notes.

    **Request Body:**
    - `sleep`: "bad", "okay", or "great"
    - `focus`: "low", "medium", or "high"
    - `mood`: "sad", "neutral", or "happy"
    - `journal`: (optional) Free-text notes

    **Response:** CheckinResponse with auto-generated ID and timestamp
    """
    # TODO: Get user_id from JWT token when auth is implemented
    user_id = "default_user"

    return await readiness_service.submit_checkin(user_id, req)


@router.get("/current", response_model=Optional[CheckinResponse])
async def get_today() -> Optional[CheckinResponse]:
    """
    Get today's check-in if already submitted.

    Returns the check-in for today, or None if not checked in yet.
    Useful for pre-filling the form on page load.
    """
    # TODO: Get user_id from JWT token when auth is implemented
    user_id = "default_user"

    return await readiness_service.get_today_checkin(user_id)


@router.get("/history", response_model=ReadinessHistoryResponse)
async def get_history(days: int = Query(7, ge=1, le=90)) -> ReadinessHistoryResponse:
    """
    Get historical check-ins with weekly summary.

    **Query Parameters:**
    - `days`: Number of days to retrieve (1-90, default 7)

    **Response:** ReadinessHistoryResponse with checkin list and aggregated stats
    """
    # TODO: Get user_id from JWT token when auth is implemented
    user_id = "default_user"

    return await readiness_service.get_history(user_id, days)
```

---

### Update File 4️⃣: `backend/app/main.py` (ADD THESE LINES)

**Find this section:**

```python
# Register routes
app.include_router(chat.router)
# ... other routers ...
```

**Add this line after the other routers:**

```python
# Import at the top
from backend.app.api.routes import readiness

# Add with other routers (around line ~70)
app.include_router(readiness.router)
```

**Complete example (check your actual main.py for exact location):**

```python
# === API Routes ===
app.include_router(chat.router)
app.include_router(corpus.router)
app.include_router(health.router)
app.include_router(session.router)
app.include_router(readiness.router)  # ADD THIS LINE
```

---

## PHASE 2: FRONTEND HOOKS

### File 5️⃣: `frontend/src/hooks/useReadiness.tsx` (NEW)

````typescript
import {
  useMutation,
  useQuery,
  useQueryClient,
  UseQueryResult,
  UseMutationResult,
} from '@tanstack/react-query';

/**
 * Types matching backend readiness.py schemas
 */

export interface Checkin {
  id: string;
  date: string;
  sleep: 'bad' | 'okay' | 'great';
  focus: 'low' | 'medium' | 'high';
  mood: 'sad' | 'neutral' | 'happy';
  journal?: string | null;
  created_at: string;
}

export interface WeeklySummary {
  happy_pct: number;
  neutral_pct: number;
  sad_pct: number;
  avg_sleep: string;
  avg_focus: string;
  total_checkins: number;
}

export interface ReadinessHistory {
  checkins: Checkin[];
  summary: WeeklySummary;
}

export interface CheckinSubmitData {
  sleep: string;
  focus: string;
  mood: string;
  journal?: string;
}

/**
 * Submit today's well-being check-in
 *
 * Usage:
 * ```
 * const { mutate, isPending } = useSubmitCheckin();
 * mutate({ sleep: "great", focus: "high", mood: "happy" });
 * ```
 */
export const useSubmitCheckin = (): UseMutationResult<
  Checkin,
  Error,
  CheckinSubmitData
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CheckinSubmitData) => {
      const response = await fetch('/api/readiness/checkin', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to submit check-in');
      }

      return response.json() as Promise<Checkin>;
    },
    onSuccess: () => {
      // Invalidate queries so they refetch with new data
      queryClient.invalidateQueries({ queryKey: ['readiness', 'today'] });
      queryClient.invalidateQueries({ queryKey: ['readiness', 'history'] });
    },
  });
};

/**
 * Get today's check-in if already submitted
 *
 * Usage:
 * ```
 * const { data: todayCheckin, isLoading } = useReadinessToday();
 * if (!todayCheckin) return <CheckinForm />;
 * ```
 */
export const useReadinessToday = (): UseQueryResult<Checkin | null> => {
  return useQuery({
    queryKey: ['readiness', 'today'],
    queryFn: async () => {
      const response = await fetch('/api/readiness/current');

      // 200 but null response means no check-in yet
      if (
        response.status === 204 ||
        response.headers.get('content-length') === '0'
      ) {
        return null;
      }

      if (!response.ok) {
        return null;
      }

      const data = await response.json();
      return data as Checkin | null;
    },
    // Refetch every 5 minutes to see if new check-in submitted
    staleTime: 5 * 60 * 1000,
  });
};

/**
 * Get historical check-ins and weekly summary
 *
 * Usage:
 * ```
 * const { data, isLoading } = useReadinessHistory(7);
 * data?.checkins.map(c => <CheckinCard key={c.id} checkin={c} />)
 * ```
 */
export const useReadinessHistory = (
  days: number = 7,
): UseQueryResult<ReadinessHistory> => {
  return useQuery({
    queryKey: ['readiness', 'history', days],
    queryFn: async () => {
      const response = await fetch(`/api/readiness/history?days=${days}`);

      if (!response.ok) {
        throw new Error('Failed to fetch readiness history');
      }

      const data = await response.json();

      return {
        checkins: data.data as Checkin[],
        summary: data.week_summary as WeeklySummary,
      };
    },
    // Keep cache for 10 minutes
    staleTime: 10 * 60 * 1000,
  });
};
````

---

## PHASE 3: UPDATE WELL-BEING PAGE

### File 6️⃣: `frontend/src/routes/wellbeing.tsx` (KEY CHANGES)

**Replace the entire component with this updated version:**

```typescript
import { useState, useMemo, useCallback } from "react";
import { PageHeader } from "@/components/PageHeader";
import { AvatarTip } from "@/components/AvatarTip";
import { useReadinessHistory, useReadinessToday, useSubmitCheckin } from "@/hooks/useReadiness";
// ... other imports ...

export function WellbeingPage() {
  // ========== Local Form State ==========
  const [sleep, setSleep] = useState<string | null>(null);
  const [focus, setFocus] = useState<string | null>(null);
  const [mood, setMood] = useState<string | null>(null);
  const [journal, setJournal] = useState("");

  // ========== Fetch Data from Backend ==========
  const { data: todayCheckin, isLoading: loadingToday } = useReadinessToday();
  const { data: historyData, isLoading: loadingHistory } = useReadinessHistory(7);
  const { mutate: submitCheckin, isPending: submitting } = useSubmitCheckin();

  // ========== Pre-fill if Already Checked In Today ==========
  useMemo(() => {
    if (todayCheckin) {
      setSleep(todayCheckin.sleep);
      setFocus(todayCheckin.focus);
      setMood(todayCheckin.mood);
      setJournal(todayCheckin.journal || "");
    }
  }, [todayCheckin]);

  // ========== Check if Form is Complete ==========
  const isComplete = sleep && focus && mood;

  // ========== Handle Form Submission ==========
  const handleSubmit = useCallback(() => {
    if (isComplete) {
      submitCheckin({
        sleep,
        focus,
        mood,
        journal: journal || undefined,
      });
    }
  }, [sleep, focus, mood, journal, isComplete, submitCheckin]);

  // ========== Compute Real Chart Data ==========

  // Weekly mood data (mapped to numeric: happy=3, neutral=2, sad=1)
  const moodWeek = useMemo(() => {
    if (!historyData?.checkins) return [2, 3, 2, 2, 3, 3, 3];
    const moodMap = { happy: 3, neutral: 2, sad: 1 };
    return historyData.checkins
      .map((c) => moodMap[c.mood as keyof typeof moodMap] || 2)
      .concat(Array(7).fill(2))
      .slice(-7);
  }, [historyData?.checkins]);

  // Emotion distribution (percentages)
  const emotionDist = useMemo(() => {
    if (!historyData?.summary) {
      return { happy: 40, neutral: 40, sad: 20 };
    }
    return {
      happy: historyData.summary.happy_pct,
      neutral: historyData.summary.neutral_pct,
      sad: historyData.summary.sad_pct,
    };
  }, [historyData?.summary]);

  // Sleep vs Focus weekly data
  const sleepWeek = useMemo(() => {
    if (!historyData?.checkins) return [6, 7, 5, 6, 8, 7, 6];
    const sleepMap = { bad: 4, okay: 6, great: 8 };
    return historyData.checkins
      .map((c) => sleepMap[c.sleep as keyof typeof sleepMap] || 6)
      .concat(Array(7).fill(6))
      .slice(-7);
  }, [historyData?.checkins]);

  const focusWeek = useMemo(() => {
    if (!historyData?.checkins) return [6, 7, 5, 6, 8, 7, 6];
    const focusMap = { low: 4, medium: 6, high: 8 };
    return historyData.checkins
      .map((c) => focusMap[c.focus as keyof typeof focusMap] || 6)
      .concat(Array(7).fill(6))
      .slice(-7);
  }, [historyData?.checkins]);

  // ========== Compute Smart Insights ==========
  const insights = useMemo(() => {
    const msgs: string[] = [];

    if (!sleep || !focus || !mood) return msgs;

    if (focus === "high" && sleep === "bad") {
      msgs.push("🚨 You're pushing hard but not sleeping well. Consider resting.");
    } else if (focus === "high" && sleep === "great") {
      msgs.push("🌟 Perfect balance! High focus with great sleep.");
    }

    if (mood === "happy" && focus === "high") {
      msgs.push("😊 Happy and focused - great combo for learning!");
    } else if (mood === "sad") {
      msgs.push("💙 It's okay to take a break. Try a breathing exercise.");
    }

    if (focus === "low") {
      msgs.push("💡 Try the Pomodoro technique: 25 min focus + 5 min break");
    }

    if (sleep === "bad") {
      msgs.push("😴 Poor sleep affects focus. Prioritize rest tonight.");
    }

    return msgs.length > 0
      ? msgs
      : ["✨ You're doing great! Keep up the momentum."];
  }, [sleep, focus, mood]);

  // ========== Render ==========
  return (
    <div className="min-h-screen bg-background">
      <PageHeader
        title="Well-Being Dashboard"
        subtitle="Track your mood, sleep, and focus"
        icon="💙"
      />

      <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
        {/* ─── Daily Check-in Widget ─── */}
        <section className="rounded-3xl bg-card border border-border p-6 lg:p-8 shadow-card">
          <h2 className="text-2xl font-bold mb-6">Today's Check-in</h2>

          {loadingToday ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading...
            </div>
          ) : (
            <div className="space-y-6">
              {/* Sleep */}
              <div>
                <label className="block text-sm font-medium mb-3">
                  How did you sleep? 😴
                </label>
                <PillGroup
                  options={[
                    { label: "Bad 😴", value: "bad" },
                    { label: "Okay 😐", value: "okay" },
                    { label: "Great 😊", value: "great" },
                  ]}
                  selected={sleep}
                  onChange={setSleep}
                />
              </div>

              {/* Focus */}
              <div>
                <label className="block text-sm font-medium mb-3">
                  How's your focus? 🎯
                </label>
                <PillGroup
                  options={[
                    { label: "Low 🌊", value: "low" },
                    { label: "Medium ⚖️", value: "medium" },
                    { label: "High 🚀", value: "high" },
                  ]}
                  selected={focus}
                  onChange={setFocus}
                />
              </div>

              {/* Mood */}
              <div>
                <label className="block text-sm font-medium mb-3">
                  How's your mood? 😊
                </label>
                <PillGroup
                  options={[
                    { label: "Sad 😢", value: "sad" },
                    { label: "Neutral 😐", value: "neutral" },
                    { label: "Happy 😊", value: "happy" },
                  ]}
                  selected={mood}
                  onChange={setMood}
                />
              </div>

              {/* Journal */}
              <div>
                <label className="block text-sm font-medium mb-3">
                  Any notes? (optional)
                </label>
                <textarea
                  value={journal}
                  onChange={(e) => setJournal(e.target.value)}
                  placeholder="How are you feeling today?"
                  className="w-full px-4 py-3 rounded-xl border border-input bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 resize-none"
                  rows={3}
                />
              </div>

              {/* Submit Button */}
              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleSubmit}
                  disabled={!isComplete || submitting}
                  className={`flex-1 px-6 py-3 rounded-xl font-semibold transition-all ${
                    isComplete && !submitting
                      ? "gradient-primary text-primary-foreground hover:shadow-lg cursor-pointer"
                      : "bg-muted text-muted-foreground cursor-not-allowed opacity-50"
                  }`}
                >
                  {submitting ? "Saving..." : "Save Check-in"}
                </button>

                {todayCheckin && (
                  <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-success/10 text-success text-sm font-medium">
                    <span>✓</span>
                    <span>Saved today</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </section>

        {/* ─── Smart Insights ─── */}
        {(sleep || focus || mood) && (
          <section className="rounded-3xl bg-gradient-to-br from-primary/10 to-accent/10 border border-border p-6 lg:p-8">
            <div className="flex gap-4 items-start">
              <AvatarTip insights={insights} />
              <div className="flex-1 space-y-2">
                <h3 className="font-semibold text-lg">AI Insights</h3>
                {insights.map((insight, i) => (
                  <p key={i} className="text-sm text-foreground/80 leading-relaxed">
                    {insight}
                  </p>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* ─── Charts Section ─── */}
        {!loadingHistory && (
          <>
            {/* Weekly Mood */}
            <MoodLineChart data={moodWeek} />

            {/* Emotion Distribution */}
            <EmotionDonut
              happy={emotionDist.happy}
              neutral={emotionDist.neutral}
              sad={emotionDist.sad}
            />

            {/* Sleep vs Focus */}
            <DualLineChart sleepData={sleepWeek} focusData={focusWeek} />

            {/* Study Intensity */}
            <StudyIntensitySection />

            {/* Emotional Timeline */}
            <EmotionalTimeline />
          </>
        )}
      </div>
    </div>
  );
}

// ========== Helper Components (Already Exist) ==========

function PillGroup({
  options,
  selected,
  onChange,
}: {
  options: { label: string; value: string }[];
  selected: string | null;
  onChange: (value: string) => void;
}) {
  return (
    <div className="flex gap-3 flex-wrap">
      {options.map((opt) => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          className={`px-4 py-2 rounded-full font-medium transition-all ${
            selected === opt.value
              ? "gradient-primary text-primary-foreground shadow-lg"
              : "bg-muted text-muted-foreground hover:bg-muted/80"
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

// Note: MoodLineChart, EmotionDonut, DualLineChart, StudyIntensitySection,
// EmotionalTimeline components should already exist in your file.
// They'll now receive real data instead of mock data.
```

---

## 🧪 TESTING (Copy-Paste Commands)

### Test Backend

```bash
# Terminal 1: Start backend
cd "c:\Institue Isimm\Ing2_Info\GreenNovation\greenNovation"
uvicorn backend.app.main:app --reload --port 8001

# Then in browser, go to:
# http://127.0.0.1:8001/docs

# Try this in Swagger UI:
POST /api/readiness/checkin
{
  "sleep": "great",
  "focus": "high",
  "mood": "happy",
  "journal": "Excellent study session!"
}

# Should return 200 with CheckinResponse
```

### Test Frontend

```bash
# Terminal 2: Start frontend
cd "c:\Institue Isimm\Ing2_Info\GreenNovation\greenNovation\frontend"
npm run dev

# Go to: http://localhost:5173/wellbeing
# Fill form → Click Save → Check browser console
```

---

## ✅ Final Checklist

### Backend Files Created

- [ ] `backend/app/schemas/readiness.py` ✓
- [ ] `backend/app/services/readiness_service.py` ✓
- [ ] `backend/app/api/routes/readiness.py` ✓
- [ ] `backend/app/main.py` (added readiness router) ✓

### Frontend Files

- [ ] `frontend/src/hooks/useReadiness.tsx` ✓
- [ ] `frontend/src/routes/wellbeing.tsx` (updated) ✓

### Testing

- [ ] Backend starts without errors ✓
- [ ] Swagger UI shows /api/readiness/\* endpoints ✓
- [ ] POST /api/readiness/checkin works ✓
- [ ] Frontend loads without errors ✓
- [ ] Can submit check-in from UI ✓
- [ ] Can refresh and data persists ✓
- [ ] Charts show real data ✓

---

## 🚀 Ready?

**Start here:**

1. Create the 3 backend files (readiness.py x3)
2. Update main.py
3. Test in Swagger
4. Create frontend hook
5. Update wellbeing page
6. Test end-to-end

Good luck! 🎉
