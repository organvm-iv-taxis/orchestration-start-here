# Testament Formalization

Formal logic, algorithms, and mathematics for the thirteen articles.

---

## Foundational Definitions

### Domain

Let **D** be the domain of discourse:

```
T = {t₁, t₂, ..., tₙ}          — set of all text units (sentences)
P = {p₁, p₂, ..., pₘ}          — set of all paragraphs, where pᵢ ⊂ T
S = {s₁, s₂, ..., sₖ}          — set of all sections, where sⱼ ⊂ P
W = {w₁, w₂, ..., wᵥ}          — vocabulary (all available words)
R = {r₁, r₂, ..., rᵤ}          — set of all readers
C = {c₁, c₂, ..., cₗ}          — set of all citable sources
```

### Primitive Functions

```
κ : T → ℝ≥0                     — knowledge content of a text unit
χ : W → ℝ>0                     — charge (semantic weight) of a word
δ : T → ℝ>0                     — density: information per unit surface
ω : T → W                       — final word extractor (power position)
θ : P → {pathos, ethos, logos} → ℝ≥0  — rhetorical dimension measure
```

---

## Article I — The Knowledge Imperative

### Logic

```
Axiom I:
  ∀O ∈ Output: κ(O) > 0

Theorem I.1 (Agreement Extension):
  ∀ response R to input I:
    agree(R, I) → ∃ extension E: κ(E) > 0 ∧ E ⊂ R ∧ E ⊄ I

  Proof:
    1. Assume agree(R, I) ∧ ¬∃E          — suppose agreement with no extension
    2. Then R ⊆ restatement(I)           — R adds nothing beyond I
    3. Then κ(R \ I) = 0                 — no new knowledge
    4. Contradicts Axiom I               — ∎ QED by contradiction

Theorem I.2 (Disagreement Pivot):
  ∀ response R to input I:
    disagree(R, I) → ∃ pivot V: κ(V) > 0 ∧ V ⊂ R ∧ constructive(V)

Theorem I.3 (Fat Elimination):
  ∀ paragraph p ∈ P:
    removable(p) ↔ ∀ reader r: understanding(r, text) = understanding(r, text \ {p})
    removable(p) → ¬publish(p)
```

### Algorithm

```python
def validate_knowledge_imperative(output: list[Paragraph]) -> bool:
    """Every paragraph must carry non-zero knowledge content."""
    for p in output:
        if knowledge_content(p) == 0:
            return False
        if is_pure_agreement(p) and not has_extension(p):
            return False
        if is_pure_disagreement(p) and not has_pivot(p):
            return False
    return True

def knowledge_content(p: Paragraph) -> float:
    """κ(p) = information in p not derivable from prior context."""
    prior = p.preceding_context()
    novel = p.semantic_content() - prior.semantic_content()
    return magnitude(novel)
```

### Mathematics

```
κ: P → ℝ≥0 is the knowledge function.

Define the information gain of paragraph p given context C:

  κ(p | C) = H(p) - H(p | C)

where H is Shannon entropy over the semantic content space.

Axiom I requires: ∀p ∈ published(P): κ(p | C_p) > 0
where C_p is the context preceding p.

The fat metric:
  fat(p) = 1 - κ(p | C_p) / |p|

where |p| is word count. A paragraph with fat(p) > τ (threshold) should be cut or compressed.
```

---

## Article II — Cascading Causation

### Logic

```
Definition: Connector Types
  CONN = {BUT, THEREFORE, AND_THEN}

  BUT(a, b)       ≡ b complicates a     — introduces obstacle
  THEREFORE(a, b)  ≡ b follows from a    — causal consequence
  AND_THEN(a, b)   ≡ b merely follows a  — temporal succession only

Axiom II:
  ∀ adjacent beats (bᵢ, bᵢ₊₁) in text:
    connector(bᵢ, bᵢ₊₁) ∈ {BUT, THEREFORE}

Theorem II.1 (Causal Chain Validity):
  A text is structurally valid iff:
    ∀i ∈ [1, n-1]: connector(bᵢ, bᵢ₊₁) ≠ AND_THEN

  Proof:
    1. Let text = (b₁, b₂, ..., bₙ)
    2. Define valid(text) ≡ ∀i: connector(bᵢ, bᵢ₊₁) ∈ {BUT, THEREFORE}
    3. By Axiom II, AND_THEN is excluded
    4. Therefore valid(text) ↔ ¬∃i: connector(bᵢ, bᵢ₊₁) = AND_THEN  — ∎

Theorem II.2 (Cascade Property):
  ∀ adjacent paragraphs (pᵢ, pᵢ₊₁):
    conclusion(pᵢ) = premise(pᵢ₊₁)

  This is the waterfall property: each pool's overflow feeds the next.
```

### Algorithm

```python
def classify_connector(beat_a: Beat, beat_b: Beat) -> Connector:
    """Parker/Stone diagnostic."""
    if beat_b.is_consequence_of(beat_a):
        return THEREFORE
    elif beat_b.is_complication_of(beat_a):
        return BUT
    else:
        return AND_THEN  # STRUCTURAL FAILURE

def validate_cascade(paragraphs: list[Paragraph]) -> list[Failure]:
    """Test the entire text for AND_THEN violations."""
    failures = []
    for i in range(len(paragraphs) - 1):
        conn = classify_connector(paragraphs[i], paragraphs[i + 1])
        if conn == AND_THEN:
            failures.append(CascadeFailure(
                index=i,
                from_paragraph=paragraphs[i],
                to_paragraph=paragraphs[i + 1],
                diagnosis="temporal succession without causal force",
            ))
        # Waterfall test
        if conclusion(paragraphs[i]) != premise(paragraphs[i + 1]):
            failures.append(WaterfallBreak(index=i))
    return failures
```

### Mathematics

```
Define the causal graph G = (B, E) where:
  B = {b₁, ..., bₙ}  — beats (nodes)
  E ⊆ B × B × CONN   — edges labeled with connector type

The causation constraint is:
  ∀(bᵢ, bⱼ, c) ∈ E: c ∈ {BUT, THEREFORE}

Define causal strength:
  σ: E → ℝ>0 where
  σ(bᵢ, bⱼ, THEREFORE) = P(bⱼ | bᵢ)     — probability of consequence
  σ(bᵢ, bⱼ, BUT) = 1 - P(bⱼ | bᵢ)       — surprise of complication

Total cascade momentum:
  M(text) = Σᵢ σ(bᵢ, bᵢ₊₁, cᵢ)

A well-cascaded text maximizes M(text).
```

---

## Article III — The Triple Layer

### Logic

```
Definition: Rhetorical Dimensions
  Θ = {pathos, ethos, logos}

Axiom III:
  ∀p ∈ P: ∀d ∈ Θ: θ(p, d) > 0

  In words: every paragraph has non-zero pathos AND non-zero ethos AND non-zero logos.

Theorem III.1 (Dimensional Completeness):
  Let p be a paragraph. Define:
    textbook(p) ≡ θ(p, logos) > 0 ∧ θ(p, pathos) = 0 ∧ θ(p, ethos) = 0
    diary(p)    ≡ θ(p, pathos) > 0 ∧ θ(p, logos) = 0 ∧ θ(p, ethos) = 0
    resume(p)   ≡ θ(p, ethos) > 0 ∧ θ(p, logos) = 0 ∧ θ(p, pathos) = 0

  Axiom III → ¬textbook(p) ∧ ¬diary(p) ∧ ¬resume(p)  — ∎

Corollary III.1 (Waller-Bridge Minimum):
  |{d ∈ Θ : θ(p, d) > 0}| ≥ 3   — at least three things going on
```

### Algorithm

```python
def measure_triple_layer(paragraph: Paragraph) -> dict[str, float]:
    """Compute θ(p, d) for each rhetorical dimension."""
    return {
        "pathos": measure_pathos(paragraph),   # felt truth, honest questions
        "ethos":  measure_ethos(paragraph),     # embedded competence signals
        "logos":  measure_logos(paragraph),      # evidence, mechanism, causation
    }

def validate_triple_layer(paragraph: Paragraph) -> bool:
    scores = measure_triple_layer(paragraph)
    return all(v > 0 for v in scores.values())

def diagnose_imbalance(paragraph: Paragraph) -> str | None:
    scores = measure_triple_layer(paragraph)
    zero_dims = [k for k, v in scores.items() if v == 0]
    if not zero_dims:
        return None
    if zero_dims == ["pathos", "ethos"]:
        return "TEXTBOOK — add felt truth and demonstrated competence"
    if zero_dims == ["logos", "ethos"]:
        return "DIARY — add evidence and credential"
    if zero_dims == ["logos", "pathos"]:
        return "RESUME — add argument and honesty"
    return f"MISSING: {', '.join(zero_dims)}"
```

### Mathematics

```
The rhetorical space is ℝ³₊ with axes (pathos, ethos, logos).

Each paragraph p maps to a point:
  θ(p) = (θ_P(p), θ_E(p), θ_L(p)) ∈ ℝ³₊

Axiom III constrains all paragraphs to the open positive orthant:
  ∀p: θ(p) ∈ ℝ³₊₊ = {(x, y, z) : x > 0 ∧ y > 0 ∧ z > 0}

The balance metric (how evenly distributed the three dimensions are):
  β(p) = 1 - (max(θ(p)) - min(θ(p))) / max(θ(p))

β(p) = 1 means perfect balance. β(p) → 0 means one dimension dominates.

The rhetorical volume of a paragraph:
  V(p) = θ_P(p) · θ_E(p) · θ_L(p)

V(p) is maximized when all three dimensions are strong. If any dimension
is zero, V(p) = 0 (the paragraph collapses to a plane — flat, not spatial).
```

---

## Article IV — Non-Submersible Units

### Logic

```
Definition:
  standalone(s) ≡ ∀r ∈ R: comprehensible(r, s) without context(s \ {s})

Axiom IV:
  ∀s ∈ S: standalone(s)
  4 ≤ |S| ≤ 8

Theorem IV.1 (Dependency Elimination):
  ∀(sᵢ, sⱼ) ∈ S²:
    requires(sⱼ, sᵢ) → merge(sᵢ, sⱼ) ∨ make_self_sufficient(sⱼ)

  A section that depends on another section for comprehensibility
  must be either merged with its dependency or made self-sufficient.
```

### Algorithm

```python
def validate_submersibility(sections: list[Section]) -> list[Failure]:
    failures = []
    if not (4 <= len(sections) <= 8):
        failures.append(CountFailure(len(sections), expected="4-8"))
    for s in sections:
        if not is_comprehensible_in_isolation(s):
            deps = find_dependencies(s, sections)
            failures.append(DependencyFailure(
                section=s,
                depends_on=deps,
                remedy="merge or make self-sufficient",
            ))
    return failures
```

### Mathematics

```
Define the dependency matrix D ∈ {0,1}^(k×k) where:
  D[i,j] = 1 iff section sᵢ requires sⱼ for comprehension

Axiom IV requires D = 0 (the zero matrix) — no section depends on any other.

The submersibility score:
  Ψ(s) = 1 - |{j : D[i,j] = 1}| / (k - 1)

Ψ(s) = 1 means fully standalone. Ψ(s) = 0 means dependent on every other section.

Axiom IV: ∀i: Ψ(sᵢ) = 1
```

---

## Article V — Collision Geometry

### Logic

```
Definition:
  Thread = ordered sequence of beats with internal causal coherence
  BridgeElement = detail planted in thread Tᵢ that connects to Tⱼ
  CollisionPoint = beat where ≥2 threads intersect via bridge elements

Axiom V:
  ∃ B ⊂ BridgeElements, ∃ cp ∈ CollisionPoint:
    |threads_intersecting(cp)| ≥ 2 ∧
    ∀t ∈ threads_intersecting(cp): causal_via(t, cp, B)

Theorem V.1 (Inevitability-Surprise Duality):
  Let cp be a collision point. Define:
    P_foresight(cp) = P(reader predicts cp before it occurs)
    P_retrospect(cp) = P(reader sees cp as necessary after it occurs)

  Optimal collision: P_foresight(cp) is LOW ∧ P_retrospect(cp) is HIGH

  If P_foresight is high → setup too obvious.
  If P_retrospect is low → bridge elements too weak.
```

### Algorithm

```python
def validate_collision_geometry(threads: list[Thread]) -> CollisionAnalysis:
    """Verify Larry David architecture."""
    bridges = find_bridge_elements(threads)
    collisions = find_collision_points(threads, bridges)

    if not collisions:
        return CollisionAnalysis(valid=False, diagnosis="no convergence found")

    for cp in collisions:
        # Test inevitability
        if not all(is_causal(t, cp) for t in cp.threads):
            return CollisionAnalysis(
                valid=False,
                diagnosis=f"collision at {cp} is coincidental, not causal",
            )
        # Test surprise
        if bridge_is_obvious(cp.bridge_element):
            return CollisionAnalysis(
                valid=False,
                diagnosis="bridge element too conspicuous at planting",
            )

    return CollisionAnalysis(valid=True, collision_points=collisions)
```

### Mathematics

```
Let T = {T₁, ..., Tₙ} be n threads, each Tᵢ a sequence of beats.
Let B = {b₁, ..., bₘ} be bridge elements.

Define the connection function:
  γ: B → 𝒫(T)   mapping each bridge to the set of threads it connects

A collision point cp exists iff:
  ∃b ∈ B: |γ(b)| ≥ 2

The collision strength:
  Γ(cp) = |γ(b_cp)| × Π_{T∈γ(b_cp)} causal_strength(T, cp)

The surprise-inevitability score:
  S(cp) = P_retrospect(cp) × (1 - P_foresight(cp))

  S ∈ [0, 1]. Optimal when both factors are high.
```

---

## Article VI — Recognition Pleasure

### Logic

```
Definition:
  K(r) = knowledge level of reader r (domain: [0, 1])
  pleasure: R × Text → ℝ≥0

Axiom VI:
  ∀r ∈ R: pleasure(r, text) > 0
  ∀r₁, r₂: K(r₁) > K(r₂) → pleasure(r₁, text) ≥ pleasure(r₂, text)

  In words: everyone gets something, and more knowledge yields more pleasure.

Theorem VI.1 (Non-Exclusion):
  ¬∃ text: pleasure(r, text) = 0 for K(r) = 0

  Even the reader with no domain knowledge experiences craft pleasure.

Theorem VI.2 (Non-Explanation):
  Let E(text) be a version of text with deeper layers explained explicitly.
  Then: ∀r with K(r) > 0: pleasure(r, E(text)) < pleasure(r, text)

  Explaining the deeper reference destroys the recognition pleasure.
```

### Algorithm

```python
def validate_recognition_layers(text: Text) -> LayerAnalysis:
    """Verify multiple recognition levels exist."""
    surface = extract_surface_meaning(text)        # accessible to all
    craft = extract_craft_signals(text)             # style, structure, rhythm
    reference = extract_embedded_references(text)   # domain-specific allusions

    if not surface:
        return LayerAnalysis(valid=False, diagnosis="no surface meaning")
    if not craft:
        return LayerAnalysis(valid=False, diagnosis="no craft layer")

    # Check that references are implicit, not explained
    for ref in reference:
        if is_explicitly_explained(ref, text):
            return LayerAnalysis(
                valid=False,
                diagnosis=f"reference '{ref.source}' is explained — destroys recognition",
            )

    return LayerAnalysis(valid=True, layers=len(reference) + 2)
```

### Mathematics

```
Define the pleasure function as a sum over recognition layers:

  pleasure(r, text) = Σᵢ αᵢ · recognize(r, layerᵢ)

where:
  recognize(r, layerᵢ) = 1 if K(r) ≥ threshold(layerᵢ), else 0
  αᵢ > 0 for all layers (each recognized layer adds pleasure)
  layer₀ = surface meaning, threshold(layer₀) = 0  (everyone recognizes)
  layer₁ = craft, threshold(layer₁) = ε (near-zero — most people sense craft)
  layerₙ = deep reference, threshold(layerₙ) = high

The monotonicity property:
  K(r₁) > K(r₂) → pleasure(r₁) ≥ pleasure(r₂)

follows directly from the threshold structure.

The non-exclusion floor:
  pleasure(r, text) ≥ α₀ > 0 for all r

because layer₀ is always recognized.
```

---

## Article VII — Citation Discipline

### Logic

```
Definition:
  Citation = (runway_in, source_material, runway_out)
  Mode = {DIRECT_QUOTE, PARAPHRASE, SUMMARY}

Axiom VII.1 (Default Paraphrase):
  ∀c ∈ Citations: mode(c) = PARAPHRASE unless language_relevance(c.source) > τ

Axiom VII.2 (Sandwich Completeness):
  ∀c ∈ Citations:
    runway_in(c) ≠ ∅ ∧ source_material(c) ≠ ∅ ∧ runway_out(c) ≠ ∅

Axiom VII.3 (Endnote Format):
  ∀c ∈ Citations: format(c) = ENDNOTE, format(c) ≠ INLINE_PARENTHETICAL

Theorem VII.1 (Direct Quote Justification):
  mode(c) = DIRECT_QUOTE →
    language_relevance(c.source) > τ ∧
    meaning(c.source) ≠ meaning(paraphrase(c.source))

  Direct quotation is justified iff the original language carries
  rhetorical weight that paraphrase would lose.
```

### Algorithm

```python
def validate_citation(citation: Citation) -> list[Failure]:
    failures = []

    # Sandwich completeness
    if not citation.runway_in:
        failures.append("missing runway in — source appears without introduction")
    if not citation.runway_out:
        failures.append("missing runway out — source departs without consequence")

    # Mode justification
    if citation.mode == DIRECT_QUOTE:
        if not language_carries_weight(citation.source_text):
            failures.append("direct quote unjustified — paraphrase would serve")

    # Format
    if citation.format == INLINE_PARENTHETICAL:
        failures.append("inline parenthetical — convert to endnote")

    # Primary before secondary
    if citation.type == SECONDARY and not exists_primary_for_same_topic(citation):
        failures.append("secondary source without primary — cite the repo docs first")

    return failures
```

---

## Article VIII — Dual Purpose

### Logic

```
Axiom VIII:
  ∀ action A: genuine(A) ∧ strategic(A)
  ¬∃ A: genuine(A) ⊕ strategic(A)     — never XOR, always AND

Theorem VIII.1 (Compounding):
  value(A) = Σ_{organ ∈ Organs} return(A, organ)

  Each action produces returns across multiple organs simultaneously.
  The total value is the sum, not the maximum.

Theorem VIII.2 (Quality Invariance):
  Let A₁, A₂ be actions differing only in target selection.
  quality(A₁) = quality(A₂)

  The quality of contribution is held constant.
  Only the targeting is optimized for conversion potential.
```

### Mathematics

```
Define the return vector for action A:
  R(A) = (r_I, r_II, r_III, r_V, r_VI, r_VII) ∈ ℝ⁶₊

where each component is the return to a specific organ.

Total value: V(A) = w · R(A) = Σᵢ wᵢ · rᵢ
where w is the income-weighting vector.

The dual-purpose constraint:
  ∀A: genuine_quality(A) ≥ Q_min

  Subject to: maximize V(A) = w · R(A)

This is a constrained optimization: maximize strategic return
subject to a quality floor. Not a trade-off — a constraint.
```

---

## Article IX — Verification Before Assertion

### Logic

```
Axiom IX:
  assert(P) → ∃ evidence(E): verified(E) ∧ supports(E, P) ∧ precedes(E, assert(P))

  In temporal logic: □(assert(P) → ◇⁻¹ verified(evidence(P)))
  "Always, if P is asserted, then in the past, evidence for P was verified."

Theorem IX.1 (Gap Honesty):
  ∀ system S: report(S) = exists(S) ∪ missing(S)
  |exists(S)| and |missing(S)| stated with equal specificity.
```

### Algorithm

```python
def verify_before_assert(claim: str, system: System) -> VerificationResult:
    """Article IX: evidence before assertion."""
    evidence = gather_evidence(system, claim)

    if not evidence:
        return VerificationResult(
            verified=False,
            diagnosis="claim has no supporting evidence",
        )

    for e in evidence:
        if not e.is_current():
            return VerificationResult(
                verified=False,
                diagnosis=f"evidence '{e}' is stale — reverify",
            )

    return VerificationResult(verified=True, evidence=evidence)
```

---

## Article X — Opening Architecture

### Logic

```
Definition:
  Piece = (Title, Subtitle, Precis, Frontmatter, Body, Notes)

Axiom X.1:
  ∀ piece: Title ≠ ∅ ∧ Subtitle ≠ ∅ ∧ Precis ≠ ∅

Axiom X.2:
  ∀ piece: Frontmatter ≠ ∅ ∧ machine_readable(Frontmatter)

Axiom X.3 (Hook Strength):
  continuation_desire(reader, Precis) > continuation_threshold

  The precis alone must make the reader want the full text.
```

### Algorithm

```python
def validate_opening(piece: Piece) -> list[Failure]:
    failures = []

    if not piece.title or len(piece.title.split()) > 12:
        failures.append("title missing or too long — compress to sharpest edge")

    if not piece.subtitle:
        failures.append("subtitle missing — scope undefined")

    if not piece.precis or len(piece.precis.split()) > 60:
        failures.append("precis missing or too long — 2-3 sentences maximum")

    if not stands_alone(piece.precis):
        failures.append("precis doesn't stand alone as miniature of piece")

    if not piece.frontmatter:
        failures.append("frontmatter missing — piece has no address in the system")

    # Hook test: does the precis create a gap?
    if not creates_information_gap(piece.precis):
        failures.append("precis doesn't hook — no tension to resolve")

    return failures
```

---

## Article XI — Paragraph Discipline

### Logic

```
Definition:
  ideas(p) = set of distinct ideas contained in paragraph p
  connects_backward(pᵢ, pᵢ₋₁) ≡ opening(pᵢ) references conclusion(pᵢ₋₁)
  connects_forward(pᵢ, pᵢ₊₁) ≡ conclusion(pᵢ) opens premise(pᵢ₊₁)

Axiom XI.1:
  ∀p ∈ P: |ideas(p)| = 1

Axiom XI.2:
  ∀ consecutive (pᵢ, pᵢ₊₁):
    connects_backward(pᵢ₊₁, pᵢ) ∧ connects_forward(pᵢ, pᵢ₊₁)

Axiom XI.3 (Subheading Spine):
  Let H = (h₁, h₂, ..., hₖ) be the subheadings in order.
  poetic(H) ∧ reveals_thesis_structure(H)

  Formally: H is publishable as standalone text.
```

### Algorithm

```python
def validate_paragraph_discipline(paragraphs: list[Paragraph]) -> list[Failure]:
    failures = []

    for i, p in enumerate(paragraphs):
        # One idea test
        ideas = extract_ideas(p)
        if len(ideas) > 1:
            failures.append(f"p[{i}] has {len(ideas)} ideas — split")
        if len(ideas) == 0:
            failures.append(f"p[{i}] has no idea — cut")

        # Reach-backward test
        if i > 0 and not connects_backward(p, paragraphs[i - 1]):
            failures.append(f"p[{i}] doesn't reach backward — no causal bridge")

        # Reach-forward test
        if i < len(paragraphs) - 1 and not connects_forward(p, paragraphs[i + 1]):
            failures.append(f"p[{i}] doesn't reach forward — dead end")

    return failures

def validate_subheading_spine(subheadings: list[str]) -> SpineAnalysis:
    """Extract subheadings and test if they read as poetry."""
    spine = "\n".join(subheadings)
    return SpineAnalysis(
        spine=spine,
        reveals_thesis=has_argumentative_arc(subheadings),
        reads_as_poetry=has_rhythm_and_compression(subheadings),
        publishable_standalone=is_compelling_without_body(spine),
    )
```

### Mathematics

```
Define the paragraph graph G_P = (P, E_P) where:
  E_P = {(pᵢ, pᵢ₊₁) : i ∈ [1, m-1]}

Each edge carries two functions:
  backward(pᵢ₊₁) → conclusion(pᵢ)    — the backward reach
  forward(pᵢ) → premise(pᵢ₊₁)        — the forward reach

Axiom XI.2 requires both functions to be non-null for every edge.

The connectivity measure:
  Λ(text) = |{(pᵢ,pᵢ₊₁) : backward ≠ ∅ ∧ forward ≠ ∅}| / |E_P|

Axiom XI.2: Λ(text) = 1 (every transition is bidirectionally connected).
```

---

## Article XII — Charged Language

### Logic

```
Definition:
  none_word(w) ≡ χ(w) ≈ 0 — word carries negligible semantic charge
  pandering(t) ≡ t instructs the reader what to think or feel

  NONE_WORDS = {"very", "really", "quite", "somewhat", "in order to",
                "it is important to note that", "it should be mentioned",
                "as a matter of fact", "interestingly", "it's worth noting"}

Axiom XII.1:
  ∀w ∈ published_text: w ∉ NONE_WORDS

Axiom XII.2 (Density):
  ∀t ∈ T: δ(t) = κ(t) / |t| > δ_min

  Information content per word must exceed a minimum threshold.

Axiom XII.3 (Heaviness):
  Given synonyms w₁, w₂ with meaning(w₁) ≈ meaning(w₂):
    choose argmax(χ(w)) — the heavier word

Axiom XII.4 (No Pandering):
  ∀t ∈ T: ¬pandering(t)
```

### Algorithm

```python
NONE_WORDS = {
    "very", "really", "quite", "somewhat", "in order to",
    "it is important to note that", "it should be mentioned",
    "as a matter of fact", "interestingly", "it's worth noting",
    "as well", "also", "additionally", "furthermore", "moreover",
}

PANDERING_PATTERNS = [
    r"this is exciting because",
    r"interestingly,?\s",
    r"it's worth noting",
    r"importantly,?\s",
    r"needless to say",
    r"it goes without saying",
]

def validate_charged_language(text: str) -> list[Failure]:
    failures = []
    words = tokenize(text)

    # None-word scan
    for w in words:
        if w.lower() in NONE_WORDS:
            failures.append(f"none-word: '{w}' — cut it")

    # Density check
    sentences = split_sentences(text)
    for s in sentences:
        d = information_content(s) / word_count(s)
        if d < DENSITY_THRESHOLD:
            failures.append(f"low density sentence: '{s[:50]}...'")

    # Pandering check
    for pattern in PANDERING_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            failures.append(f"pandering: matches '{pattern}'")

    # Heaviness optimization (advisory)
    for w in words:
        heavier = find_heavier_synonym(w)
        if heavier and charge(heavier) > charge(w) * 1.5:
            failures.append(f"weight upgrade: '{w}' → '{heavier}'")

    return failures
```

### Mathematics

```
The charge function χ: W → ℝ>0 orders the vocabulary by semantic weight.

For a sentence t = (w₁, ..., wₙ):

  Density: δ(t) = κ(t) / n

  Charge density: Χ(t) = (1/n) Σᵢ χ(wᵢ)

  Fat ratio: φ(t) = |{wᵢ : χ(wᵢ) < ε}| / n

  Article XII requires: φ(t) = 0 (no none-words)
  Article XII optimizes: Χ(t) → max (heaviest available words)
  Article XII constrains: δ(t) > δ_min (information per word above threshold)
```

---

## Article XIII — Enjambment and Power Position

### Logic

```
Definition:
  ω(p) = last word of paragraph p (power position)
  heartbeat(text) = (ω(p₁), ω(p₂), ..., ω(pₘ))

Axiom XIII.1 (Power Position):
  ∀p ∈ P: χ(ω(p)) = max{χ(w) : w ∈ p is a candidate for final position}

  The last word of every paragraph is the heaviest available word
  that can grammatically occupy that position.

Axiom XIII.2 (Enjambment):
  ∃ breaks in text where semantic content spans the break:
    meaning(before_break) is incomplete without meaning(after_break)

  The reader's cognitive momentum carries them across the boundary.

Axiom XIII.3 (Heartbeat Arc):
  heartbeat(text) exhibits tonal progression.
  ∃ arc function A: [1,m] → Tone such that:
    A is non-constant ∧ A has recognizable shape (rise, fall, transformation)
```

### Algorithm

```python
def extract_heartbeat(paragraphs: list[Paragraph]) -> list[str]:
    """Extract the power-word sequence — the tonal spine."""
    return [last_word(p) for p in paragraphs]

def validate_power_positions(paragraphs: list[Paragraph]) -> list[Failure]:
    failures = []

    WEAK_ENDINGS = {"well", "also", "too", "done", "things", "etc",
                    "way", "stuff", "it", "them", "this", "that"}

    for i, p in enumerate(paragraphs):
        pw = last_word(p)
        if pw.lower() in WEAK_ENDINGS:
            failures.append(f"p[{i}] ends on weak word '{pw}' — restructure")

        # Check if a heavier word exists that could occupy final position
        candidates = get_final_position_candidates(p)
        heaviest = max(candidates, key=lambda w: charge(w))
        if charge(heaviest) > charge(pw) * 1.3:
            failures.append(f"p[{i}] could end on '{heaviest}' instead of '{pw}'")

    return failures

def validate_heartbeat_arc(paragraphs: list[Paragraph]) -> ArcAnalysis:
    """Test that the power-word sequence has tonal progression."""
    heartbeat = extract_heartbeat(paragraphs)
    charges = [charge(w) for w in heartbeat]

    # Check for flat heartbeat (no progression)
    if max(charges) - min(charges) < FLATLINE_THRESHOLD:
        return ArcAnalysis(valid=False, diagnosis="flatline — no tonal progression")

    # Check for recognizable arc shape
    arc_shape = classify_arc(charges)  # rise, fall, rise-fall, transformation

    return ArcAnalysis(
        valid=arc_shape != "flat",
        heartbeat=heartbeat,
        arc=arc_shape,
        charge_sequence=charges,
    )

def dual_spine_report(text: Text) -> str:
    """The two spines: subheadings (thesis) and power words (tone)."""
    thesis_spine = extract_subheadings(text)
    tonal_spine = extract_heartbeat(text.paragraphs)

    report = "THESIS SPINE (subheadings):\n"
    report += "\n".join(f"  {h}" for h in thesis_spine)
    report += "\n\nTONAL SPINE (power words):\n"
    report += " → ".join(tonal_spine)

    return report
```

### Mathematics

```
The heartbeat function:
  H: [1,m] → ℝ>0 where H(i) = χ(ω(pᵢ))

The tonal arc is the shape of H over the paragraph sequence.

Define arc energy:
  E(H) = Σᵢ |H(i+1) - H(i)|

E(H) = 0 means flatline (no tonal movement). High E means dynamic progression.

Define arc direction:
  D(H) = sign(H(m) - H(1))

D > 0: rising arc (uncertainty → authority)
D < 0: falling arc (confidence → doubt)
D = 0: circular (return to origin)

The dual spine correlation:
  Let S = thesis spine (subheading charge sequence)
  Let H = tonal spine (power word charge sequence)

  ρ(S, H) = correlation between the two spines

  High ρ: thesis and tone move together (reinforcing).
  Low ρ: thesis and tone move independently (contrapuntal — can be powerful).
  Negative ρ: thesis and tone oppose (ironic — intentional subversion).

All three are valid. The key constraint is that neither spine is flat.
```

---

## Composite Validation

The complete validation of a text against all thirteen articles:

```python
def validate_testament(text: Text) -> TestamentReport:
    """Run all thirteen articles against a text."""
    report = TestamentReport()

    # I. Knowledge Imperative
    report.add(validate_knowledge_imperative(text.paragraphs))

    # II. Cascading Causation
    report.add(validate_cascade(text.paragraphs))

    # III. Triple Layer
    for p in text.paragraphs:
        report.add(validate_triple_layer(p))

    # IV. Non-Submersible Units
    report.add(validate_submersibility(text.sections))

    # V. Collision Geometry
    report.add(validate_collision_geometry(text.threads))

    # VI. Recognition Pleasure
    report.add(validate_recognition_layers(text))

    # VII. Citation Discipline
    for c in text.citations:
        report.add(validate_citation(c))

    # VIII. Dual Purpose (structural — not automatically testable)

    # IX. Verification Before Assertion
    for claim in text.claims:
        report.add(verify_before_assert(claim, text.system))

    # X. Opening Architecture
    report.add(validate_opening(text))

    # XI. Paragraph Discipline
    report.add(validate_paragraph_discipline(text.paragraphs))
    report.add(validate_subheading_spine(text.subheadings))

    # XII. Charged Language
    report.add(validate_charged_language(text.raw))

    # XIII. Enjambment & Power Position
    report.add(validate_power_positions(text.paragraphs))
    report.add(validate_heartbeat_arc(text.paragraphs))

    # Dual spine
    report.dual_spine = dual_spine_report(text)

    return report
```
