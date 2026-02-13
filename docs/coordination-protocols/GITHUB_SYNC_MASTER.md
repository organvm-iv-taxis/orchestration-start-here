# OMNI-DROMENON-MACHINA: GITHUB ↔ LOCAL SYNCHRONIZATION

**Status:** GitHub org `omni-dromenon-machina` is LIVE with 12 repos
**Local State:** `/Users/4jp/Desktop/omni-dromenon-machina/` (11 repos + 2 .github drafts + 5 handoff docs)
**Action:** Synchronize GitHub state with local + consolidate .github drafts + rename directory

---

## GITHUB ORG STATE (LIVE)

**URL:** https://github.com/orgs/omni-dromenon-machina/repositories

**12 Repos:**
1. ✅ academic-publication
2. ✅ artist-toolkits-templates
3. ✅ example-theatre-dialogue
4. ✅ example-choreographic-interface
5. ✅ example-generative-visual
6. ✅ example-generative-music
7. ✅ docs
8. ✅ audio-synthesis-bridge
9. ✅ performance-sdk
10. ✅ client-sdk ← **NOT IN LOCAL**
11. ✅ core-engine
12. ✅ .github ← **GitHub special repo**

---

## LOCAL STATE

**Path:** `/Users/4jp/Desktop/omni-dromenon-machina/`
**Structure:**
```
omni-dromenon-machina/
├── .github/                          ← Current scaffolded version
├── .github-v1.zip                    ← Draft 1 (TO RECONCILE)
├── .github-v2.zip                    ← Draft 2 (TO RECONCILE)
├── core-engine/
├── performance-sdk/
├── audio-synthesis-bridge/
├── docs/
├── academic-publication/
├── artist-toolkit-and-templates/
├── example-generative-music/
├── example-generative-visual/
├── example-choreographic-interface/
├── example-theatre-dialogue/
│
└── [HANDOFF DOCS]
    ├── HANDOFF_MASTER.md
    ├── AI_ORCHESTRATION_TIMELINE.md
    ├── PER_REPO_KEYS.md
    ├── AI_BRIEFING_TEMPLATES.md
    ├── FINAL_SUMMARY.md
    └── README.md
```

**Status:**
- ✅ 11 repos scaffolded locally
- ❌ client-sdk NOT present locally
- ❌ .github has 2 draft versions to reconcile
- ✅ All 5 handoff docs saved

---

## RECONCILIATION TASKS

### TASK 1: CONSOLIDATE `.github` DRAFTS

**Current:** 3 versions exist
- `/Users/4jp/Desktop/omni-dromenon-machina/.github/` (current)
- `/Users/4jp/Desktop/omni-dromenon-machina/.github-v1.zip`
- `/Users/4jp/Desktop/omni-dromenon-machina/.github-v2.zip`

**Action:**
1. Extract both zips to compare:
   ```bash
   unzip .github-v1.zip -d _v1_contents/
   unzip .github-v2.zip -d _v2_contents/
   ```

2. Compare files in each version (workflows, templates, etc.)

3. Decide on master version:
   - [ ] Use current `.github/` as base
   - [ ] Merge best parts from v1 + v2
   - [ ] Document decision in `.github/MERGE_DECISION.md`

4. Archive old versions:
   ```bash
   mkdir _archive/
   mv .github-v1.zip _archive/
   mv .github-v2.zip _archive/
   ```

5. Delete _v1_contents and _v2_contents folders (cleanup)

---

### TASK 2: CREATE MISSING `client-sdk` LOCALLY

**Status:** GitHub has `client-sdk`, local does not

**Action:**
```bash
cd /Users/4jp/Desktop/omni-dromenon-machina/
mkdir client-sdk
touch client-sdk/README.md
cat > client-sdk/README.md << 'EOF'
# Client SDK

WebSocket client library for connecting audience devices to the Omni-Dromenon-Engine.

**Status:** Scaffolding
**Purpose:** Lightweight JavaScript/TypeScript client for audience vote submission
**Dependencies:** core-engine types

See main docs for integration guide.
EOF
```

---

### TASK 3: RENAME DIRECTORY TO MATCH GITHUB ORG

**Current:** `/Users/4jp/Desktop/omni-dromenon-machina/`
**Target:** `/Users/4jp/Desktop/omni-dromenon-machina/`

**Action:**
```bash
cd ~/Desktop
mv omni-dromenon-machina omni-dromenon-machina
```

**Update all paths in documents:**
- HANDOFF_MASTER.md
- AI_ORCHESTRATION_TIMELINE.md
- PER_REPO_KEYS.md
- All other docs (replace `/omni-dromenon-machina/` → `/omni-dromenon-machina/`)

---

### TASK 4: ORGANIZE UNSORTED FILES

**Current loose files:**
- `.DS_Store` (remove)
- `README.md` (local readme, evaluate if needed)
- 5 handoff documents (keep, these are coordination docs)

**Action:**
```bash
# Remove macOS clutter
rm -f .DS_Store
rm -f .github/.DS_Store

# Move handoff docs to dedicated folder
mkdir -p _COORDINATION_DOCS/
mv HANDOFF_MASTER.md _COORDINATION_DOCS/
mv AI_ORCHESTRATION_TIMELINE.md _COORDINATION_DOCS/
mv PER_REPO_KEYS.md _COORDINATION_DOCS/
mv AI_BRIEFING_TEMPLATES.md _COORDINATION_DOCS/
mv FINAL_SUMMARY.md _COORDINATION_DOCS/

# Update README.md to point to coordination docs
cat > README.md << 'EOF'
# Omni-Dromenon-Machina

Real-time audience-participatory performance system.

## Quick Links

- **GitHub Org:** https://github.com/omni-dromenon-machina
- **Coordination:** See `_COORDINATION_DOCS/` for Phase A-D orchestration guides
- **Core Engine:** `core-engine/` (consensus algorithm + parameter bus)
- **Examples:** `example-generative-music/`, `example-visual/`, etc.

## Handoff Documentation

- `HANDOFF_MASTER.md` — Master orchestration plan
- `AI_ORCHESTRATION_TIMELINE.md` — Detailed phase breakdown
- `PER_REPO_KEYS.md` — Where each AI service starts
- `AI_BRIEFING_TEMPLATES.md` — Copy/paste prompts for Copilot, Gemini, Jules, ChatGPT
- `FINAL_SUMMARY.md` — Immediate action checklist

## Status

GitHub org: ✅ Live (12 repos)
Local scaffold: ✅ Complete (11 repos)
.github consolidation: ⏳ In progress
Phase A orchestration: ⏳ Ready to deploy (Dec 7-8)

EOF
```

---

## CONSOLIDATED FILE STRUCTURE (TARGET STATE)

```
/Users/4jp/Desktop/omni-dromenon-machina/
│
├── _COORDINATION_DOCS/                  ← Handoff infrastructure (Phase A-D)
│   ├── HANDOFF_MASTER.md
│   ├── AI_ORCHESTRATION_TIMELINE.md
│   ├── PER_REPO_KEYS.md
│   ├── AI_BRIEFING_TEMPLATES.md
│   └── FINAL_SUMMARY.md
│
├── _archive/                            ← Old .github drafts (for reference)
│   ├── .github-v1.zip
│   └── .github-v2.zip
│
├── .github/                             ← UNIFIED (merged from v1+v2+current)
│   ├── profile/
│   │   └── README.md
│   ├── workflows/                       ← CI/CD (from AI Phase A)
│   │   ├── test.yml
│   │   ├── deploy-docs.yml
│   │   └── release.yml
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE/
│   ├── CODE_OF_CONDUCT.md
│   ├── CONTRIBUTING.md
│   ├── MERGE_DECISION.md                ← Explains which .github version was chosen
│   └── [other org-level files]
│
├── core-engine/
├── performance-sdk/
├── client-sdk/                          ← **NEW** (matches GitHub)
├── audio-synthesis-bridge/
├── docs/
├── academic-publication/
├── artist-toolkit-and-templates/
├── example-generative-music/
├── example-generative-visual/
├── example-choreographic-interface/
├── example-theatre-dialogue/
│
└── README.md                            ← Updated (points to coordination docs)
```

---

## GITHUB ↔ LOCAL SYNC CHECKLIST

```bash
# 1. CONSOLIDATE .github DRAFTS
[ ] Extract .github-v1.zip to compare
[ ] Extract .github-v2.zip to compare
[ ] Merge/decide on final version
[ ] Archive old zips to _archive/
[ ] Clean up extraction folders

# 2. CREATE client-sdk LOCALLY
[ ] mkdir client-sdk
[ ] Create README.md with purpose
[ ] Git add + commit (or sync from GitHub if already there)

# 3. ORGANIZE FILES
[ ] Remove .DS_Store + other macOS clutter
[ ] Create _COORDINATION_DOCS/ folder
[ ] Move 5 handoff documents there
[ ] Update README.md

# 4. RENAME DIRECTORY
[ ] mv omni-dromenon-machina → omni-dromenon-machina
[ ] Update all file paths in coordination docs (sed replace)
[ ] Verify all links still work

# 5. VERIFY SYNC
[ ] 12 repos locally (11 existing + 1 new client-sdk)
[ ] .github is unified (no more v1, v2 zips)
[ ] All handoff docs in _COORDINATION_DOCS/
[ ] README.md updated + points to correct paths
[ ] No .DS_Store or other clutter

# 6. READY FOR PHASE A
[ ] AI services can access /Users/4jp/Desktop/omni-dromenon-machina/
[ ] All entry points from PER_REPO_KEYS.md are valid
[ ] Handoff templates use correct paths
```

---

## GITHUB SYNC AFTER LOCAL CLEANUP

**Once local is organized:**

```bash
cd ~/Desktop/omni-dromenon-machina/

# Option A: Pull GitHub state to local (if GitHub is more current)
git pull origin main --all

# Option B: Push local state to GitHub (if local is more current)
git add .
git commit -m "Consolidate .github drafts + add client-sdk + organize coordination docs"
git push origin main
```

**Recommended:** Pull from GitHub first to see what's already there. GitHub org is canonical.

---

## WHICH .github VERSION TO KEEP?

**Comparison strategy:**
1. Extract both zips
2. Check each for:
   - [ ] Workflow files (test.yml, deploy-docs.yml, release.yml)
   - [ ] Issue templates
   - [ ] PR templates
   - [ ] Profile/README.md
   - [ ] CoC, Contributing, License

3. Merge best parts:
   - If v1 has better workflows + v2 has better templates → combine both
   - Create `.github/MERGE_DECISION.md` explaining which version was chosen + why

4. Result: Single unified `.github/` directory with all necessary org-level files

---

## IMMEDIATE ACTION (NEXT 30 MINUTES)

```bash
# 1. Consolidate .github
cd /Users/4jp/Desktop/omni-dromenon-machina
unzip .github-v1.zip -d _v1_compare/
unzip .github-v2.zip -d _v2_compare/
# Compare files manually or with diff

# 2. Move handoff docs
mkdir _COORDINATION_DOCS/
mv HANDOFF_MASTER.md _COORDINATION_DOCS/
mv AI_ORCHESTRATION_TIMELINE.md _COORDINATION_DOCS/
mv PER_REPO_KEYS.md _COORDINATION_DOCS/
mv AI_BRIEFING_TEMPLATES.md _COORDINATION_DOCS/
mv FINAL_SUMMARY.md _COORDINATION_DOCS/

# 3. Create client-sdk
mkdir client-sdk && touch client-sdk/README.md

# 4. Clean up
rm -f .DS_Store .github/.DS_Store
mkdir _archive
mv .github-v1.zip .github-v2.zip _archive/

# 5. Rename directory
cd ~/Desktop
mv omni-dromenon-machina omni-dromenon-machina

# 6. Verify
find ~/Desktop/omni-dromenon-machina -name "README.md" | wc -l
# Expected: 14 (12 repos + .github + _COORDINATION_DOCS)
```

---

## AFTER LOCAL CLEANUP: UPDATE HANDOFF DOCS

**All 5 handoff docs must have paths updated:**

```bash
cd ~/Desktop/omni-dromenon-machina/_COORDINATION_DOCS/

# Replace old path with new path
sed -i '' 's|omni-dromenon-machina|omni-dromenon-machina|g' *.md

# Verify changes
grep -n "omni-dromenon-machina" HANDOFF_MASTER.md | head -5
```

---

## YOU'RE READY FOR PHASE A

**Once all above is complete:**
- ✅ GitHub org is canonical source (12 repos live)
- ✅ Local directory matches GitHub structure
- ✅ .github is unified (no more draft zips)
- ✅ client-sdk exists locally
- ✅ Coordination docs are organized + paths updated
- ✅ Ready to brief Jules, Gemini, Copilot with corrected paths

**Phase A timeline:** Dec 7-8 (unchanged)
**Phase B gate:** Dec 11 (unchanged)

---

**Timeline:** ~30 minutes to organize everything
**Complexity:** Low (mostly file shuffling + path updates)
**Risk:** None (all local; GitHub is unchanged until you push)

**Next step:** Run the cleanup commands above, then verify sync is complete.
