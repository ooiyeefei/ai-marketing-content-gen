# BrandMind AI - Development Principles

## Purpose
This document defines the mandatory development principles for BrandMind AI to meet the hackathon requirements for **truly autonomous, self-improving AI agents**.

---

## 1. Test-Driven Development (TDD)

### Workflow
1. **Write test FIRST** - Define the expected autonomous behavior
2. **Test must FAIL** - Proves test is actually testing something
3. **Write minimal code** - Just enough to pass the test
4. **Refactor** - Improve code quality while keeping tests green

### Example
```python
# test_master_agent.py
def test_agent_regenerates_low_quality_content():
    """Agent should autonomously regenerate content with quality < 75"""
    agent = MasterAgent()

    # Mock evaluation to return low quality first, then high quality
    with mock_quality_scores([45, 88]):
        result = await agent.run(goal="Generate caption")

    # Assert: Agent attempted generation twice
    assert result.generation_attempts == 2
    assert result.final_quality_score >= 75
```

---

## 2. Spec-Driven Development

### Hackathon Requirements (Non-Negotiable)
All features must trace directly to these requirements:

> "Build autonomous, self-improving AI agents that can tap into real-time data sources, make sense of what they find, and take meaningful action without human intervention. Your challenge is to design agents that are not just reactive, but continuously learn and improve as they operate—creating solutions that feel alive, adaptive, and built for real-world impact."

### Translation to Implementation

| Requirement | Implementation | Verification |
|-------------|----------------|--------------|
| **"autonomous"** | Agent makes decisions (not hardcoded steps) | Master agent uses ReAct loop to decide next action |
| **"self-improving"** | Quality improves over time | Test: Campaign N+1 > Campaign N |
| **"tap into real-time data"** | No mocks, actual API calls | Agent decides which data sources to query |
| **"make sense of what they find"** | Agent interprets and evaluates | Quality scoring determines if data sufficient |
| **"meaningful action without human intervention"** | Agent triggers actions based on evaluation | Auto-regeneration, dynamic tool selection |
| **"continuously learn and improve"** | Learning storage and retrieval | Past learnings influence future decisions |
| **"not just reactive"** | Proactive decision-making | Agent seeks additional data if needed |

---

## 3. No Mocks or Dummy Data

### Principles
- ❌ **NEVER use mock data for demo**
- ❌ **NEVER fallback to dummy generation**
- ✅ **Use real APIs** (Lightpanda, Claude, Vertex, Redis)
- ✅ **Catch and handle real errors**
- ✅ **Agent must adapt when APIs fail**

### Error Handling Strategy
```python
# BAD: Fallback to mock
try:
    data = await lightpanda.scrape(url)
except Exception:
    data = MOCK_DATA  # ❌ This defeats the purpose

# GOOD: Agent adapts
try:
    data = await lightpanda.scrape(url)
except Exception as e:
    # Agent decides alternative approach
    thought = await agent.reason(
        context="Scraping failed, what should I do?"
    )
    if thought.action == "try_grounded_generation":
        data = await vertex.grounded_generation(url)
    elif thought.action == "skip_and_continue":
        data = None
```

### Testing with Real APIs
- Unit tests: Mock external APIs (acceptable)
- Integration tests: Use real APIs with test accounts
- Demo: 100% real API calls

---

## 4. Truly Autonomous Agents (Not Rule-Based)

### What Makes an Agent "Autonomous"?

#### ❌ **NOT Autonomous (Rule-Based Sequential Workflow)**
```python
# This is just a script disguised as agents
async def orchestrate():
    research = await agent1.research()  # Always step 1
    strategy = await agent2.strategy()  # Always step 2
    creative = await agent3.creative()  # Always step 3
    return result
```

#### ✅ **Autonomous (ReAct Pattern)**
```python
# Agent decides what to do next based on reasoning
async def orchestrate(goal: str):
    scratchpad = []  # History of thoughts/actions

    while not goal_achieved:
        # REASON: Agent thinks about what to do next
        thought = await claude.reason(
            goal=goal,
            history=scratchpad,
            available_tools=TOOL_REGISTRY.keys()
        )

        # ACT: Execute chosen action
        action = thought.chosen_action
        result = await TOOL_REGISTRY[action.tool](**action.params)

        # OBSERVE: Evaluate result
        observation = await evaluate_quality(result)

        # LEARN: Update understanding
        scratchpad.append({
            "thought": thought,
            "action": action,
            "observation": observation
        })

        # Check if goal achieved
        if observation.goal_achieved:
            break

    return result
```

### Key Differences

| Rule-Based | Autonomous |
|------------|------------|
| Fixed sequence 1→2→3→4 | Dynamic planning based on context |
| Orchestrator coordinates steps | Agent reasons about goals |
| No evaluation of quality | Agent judges its own work |
| Same execution every time | Adapts based on feedback |
| No learning between runs | Learns from past experiences |

### ReAct Pattern Components

**1. REASON**
- Agent uses Claude to think: "What should I do next given current state?"
- Considers goal, history, available tools
- Outputs: thought (reasoning) + action (tool call)

**2. ACT**
- Execute the chosen tool with specified parameters
- Tools are capabilities agent can use (research, generate, evaluate)
- Result becomes part of observation

**3. OBSERVE**
- Evaluate quality/completeness of result
- Determine if goal achieved or more work needed
- Add to scratchpad for next reasoning step

**4. LEARN**
- Store successful patterns for future use
- Extract insights after campaign completion
- Retrieve learnings at start of new campaigns

---

## 5. Continuously Learning (Self-Improvement)

### Requirements
- Every campaign MUST improve over previous campaigns
- Learning is MEASURABLE (quality scores increase)
- Agent EXPLAINS how it learned and adapted

### Implementation Pattern

#### Phase 1: Learning Extraction (After Campaign)
```python
async def extract_learnings(campaign_id: str):
    """
    Agent analyzes what worked and stores actionable insights
    """
    campaign = await redis.get(f"campaign:{campaign_id}")

    # Agent analyzes performance
    learnings = await claude.messages.create(
        model="claude-sonnet-4.5",
        messages=[{
            "role": "user",
            "content": f"""
            Analyze this completed campaign and extract learnings:

            Campaign: {campaign}

            Provide specific, actionable insights:
            1. Which content themes drove highest engagement?
            2. What caption styles resonated most?
            3. Which visual styles performed best?
            4. What should future campaigns do differently?

            Format: Bullet list of specific learnings.
            """
        }]
    )

    # Store in simple file (MVP) or Redis vectors (production)
    with open("learnings.txt", "a") as f:
        f.write(f"\n\n=== Campaign {campaign_id} ===\n")
        f.write(learnings.content[0].text)
```

#### Phase 2: Learning Retrieval (Before Campaign)
```python
async def retrieve_learnings() -> str:
    """
    Load past learnings to influence new campaign
    """
    try:
        with open("learnings.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "No past learnings yet."
```

#### Phase 3: Learning Application (During Campaign)
```python
# Inject learnings into reasoning prompt
reasoning_prompt = f"""
You are creating a marketing campaign.

**Past Learnings:**
{await retrieve_learnings()}

**Current Goal:**
Create strategy for {business_name}

Use the learnings above to make better decisions than past campaigns.
"""
```

### Verification
```python
def test_campaigns_improve_over_time():
    """Second campaign should have higher quality than first"""
    # First campaign (no learnings)
    campaign1 = await orchestrator.run(business_url="example.com")
    score1 = campaign1.average_quality_score

    # Extract learnings
    await learning_service.extract_learnings(campaign1.id)

    # Second campaign (with learnings)
    campaign2 = await orchestrator.run(business_url="example.com")
    score2 = campaign2.average_quality_score

    # Assert improvement
    assert score2 > score1, "Agent did not improve from learnings"
```

---

## 6. Reasoning Prompt Template

### Master Orchestrator Reasoning Prompt
```text
You are a Master Marketing Orchestrator. Your goal is to create a complete, high-quality marketing campaign.

**User Request:**
{user_request}

**Available Tools:**
You have access to these tools ONLY:
{tool_definitions}

**Past Learnings:**
{learnings_from_past_campaigns}

**Instructions:**
1. Think step-by-step to achieve the goal
2. Output JSON: {"thought": "...", "action": {"tool": "...", "params": {...}}}
3. After acting, you'll receive an "observation"
4. Use evaluate_quality tool to check your work
5. If quality < 75, regenerate with different approach
6. When campaign is complete and high-quality, use finish_campaign tool

**Previous Steps:**
{scratchpad_history}

**Your Next Thought:**
```

---

## 7. Prohibited Patterns

### ❌ Hardcoded Sequences
```python
# DON'T DO THIS
async def run():
    step1 = await research()
    step2 = await strategy()
    step3 = await creative()
    return step3
```

### ❌ Mock Data Fallbacks
```python
# DON'T DO THIS
try:
    data = await api.fetch()
except:
    data = MOCK_DATA  # ❌
```

### ❌ Static Planning
```python
# DON'T DO THIS
PLAN = ["research", "strategy", "creative", "publish"]
for step in PLAN:
    await execute(step)
```

### ❌ No Quality Evaluation
```python
# DON'T DO THIS
content = await generate()
return content  # No quality check!
```

---

## 8. Required Testing Patterns

### Test 1: Autonomous Decision Making
```python
def test_agent_makes_dynamic_decisions():
    """Agent should choose different tools based on context"""
    agent = MasterAgent()

    # Scenario 1: Website has sufficient data
    result1 = await agent.run(context="rich_website")
    assert "scrape_social_media" not in result1.tools_used

    # Scenario 2: Website has minimal data
    result2 = await agent.run(context="minimal_website")
    assert "scrape_social_media" in result2.tools_used
```

### Test 2: Quality-Driven Regeneration
```python
def test_agent_regenerates_poor_quality():
    """Agent should retry when quality is low"""
    agent = MasterAgent()
    result = await agent.run()

    # Check that agent evaluated quality
    assert "evaluate_quality" in result.tools_used

    # If quality was initially low, should see multiple generation attempts
    if result.first_quality_score < 75:
        assert result.generation_attempts > 1
```

### Test 3: Learning Application
```python
def test_agent_applies_learnings():
    """Agent should use past learnings in new campaigns"""
    # Create first campaign with learning
    await orchestrator.run(business="coffee_shop_1")
    await learning_service.extract("coffee_shop_1")

    # Second campaign should reference learnings
    result = await orchestrator.run(business="coffee_shop_2")

    # Check that learnings were retrieved
    assert result.learnings_retrieved == True
```

---

## 9. Success Criteria

### Demo Must Show
1. ✅ Agent makes at least 3 autonomous decisions
2. ✅ Agent evaluates quality and regenerates at least once
3. ✅ Second campaign measurably better than first (quality score +10%)
4. ✅ No mock data used in demo
5. ✅ Agent explains its reasoning in logs

### Judges Will Look For
1. **Autonomy**: Is agent deciding or just executing steps?
2. **Learning**: Does quality improve between campaigns?
3. **Adaptation**: Does agent change behavior based on feedback?
4. **Real-time data**: Are APIs actually being called?
5. **No human intervention**: Does agent recover from failures?

---

## 10. Implementation Checklist

- [ ] Master agent uses ReAct loop (reason → act → observe)
- [ ] Tools registered as Python functions with docstrings
- [ ] Quality evaluation triggers regeneration
- [ ] Learning extraction after each campaign
- [ ] Learning retrieval before each campaign
- [ ] Reasoning prompt includes learnings
- [ ] Scratchpad maintains thought/action/observation history
- [ ] Max iterations limit prevents infinite loops
- [ ] finish_campaign tool signals completion
- [ ] All tests pass (TDD)
- [ ] No mock data in demo flow
- [ ] Error handling via agent adaptation (not fallbacks)

---

## Summary

**Sequential Workflow = Hackathon Fail**
**Autonomous Agent = Hackathon Win**

This document is your north star. Every line of code must serve one of these principles. When in doubt, ask: "Is the agent deciding, or am I deciding for it?"

If you're deciding, you're building it wrong.

**The agent must be the brain. Not you.**
