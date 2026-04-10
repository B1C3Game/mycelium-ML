# Evolution Is How Brains Learn (And Why Mycelium Works)

## The Question

You built a simulation where simple agents find food and survive. Some do better than others. Over generations, the population adapts.

Is that learning? Is that intelligence?

Yes. It's the same algorithm your brain uses.

## Part 1: What Learning Actually Is (Physiologically)

Your brain doesn't think by logic. It thinks by trying things and keeping what works.

The mechanism:

1. You encounter a problem (reach for a cup of coffee).
2. Your brain generates random variations (slightly different hand angles, forces, timings).
3. Most fail or barely work (you spill, you miss, you knock it over).
4. A few succeed (smooth reach, perfect grip).
5. Your brain keeps the successful version and discards the rest.
6. Next time, the variations cluster around what worked.

That's not logic. That's selection pressure on random variation.

Your cerebellum (the part that coordinates movement) runs this algorithm 10,000 times per second. It's not conscious. It's not reasoning. It's just: try, fail, keep what works, repeat.

## Part 2: The Brain's Learning Algorithm (Formally)

Here's what's actually happening in your neurons:

- State: "I'm trying to reach for coffee"
- Action: "Move arm to angle X with force Y"
- Reward: "Did the cup move toward my mouth?" (Yes = +1, No = -1)
- Update: "Increase probability of angle X and force Y slightly. Decrease others."

Run this 1000 times. By the end, your brain has learned: "these parameters work for this task."

Now scale it up.

Instead of one agent (your arm) making one decision:

1. Imagine 100 arms trying different angles.
2. Each one gets a reward (reach success).
3. The successful arms reproduce (copy their angle to the next generation).
4. The failed arms die.
5. Generation 2: population is now skewed toward successful angles.
6. Repeat for 500 generations.

By the end: the population has collectively "learned" the optimal angle without any central intelligence.

That's evolution. That's how your cerebellum works. That's what mycelium-ml does.

## Part 3: Naming the Algorithm (So You Know What You Built)

The algorithm is called: Evolutionary Algorithm (EA) or Genetic Algorithm (GA).

Here's what happens in each step.

Generation N:

1. Population: 100 agents, each with a "protocol" (`sensing_range`, `growth_angle`, `energy_efficiency`).
2. Evaluation: Run each agent for one step.

	- Agent senses resources (input)
	- Agent moves toward them (action)
	- Agent consumes energy (reward signal)
	- Alive? -> score = final_energy. Dead? -> score = 0

3. Selection: "Keep the winners"

	- Agents with high energy have higher probability of replicating
	- Agents with low energy die
	- This is the fitness pressure

4. Mutation: "Introduce variation"

	- Surviving agents reproduce
	- Each child has protocol similar to parent, but with small random changes
	- `sensing_range`: 5 -> 5.2
	- `growth_angle`: 45 -> 47
	- `energy_efficiency`: 1.0 -> 0.98

5. Population N+1: The new generation is now slightly shifted toward "what worked"

Run this for 500 generations:

- Gen 0: random population, all protocols different
- Gen 100: population converging, `sensing_range` clustering around some value
- Gen 500: narrow distribution, most agents have similar (successful) protocol

That convergence is learning. The population has collectively discovered: "`sensing_range=7` is better than 3 or 12."

## Part 4: Why This Mirrors Neuroscience

Your brain learns the same way, just in different hardware.

| Brain (Neuroscience) | Mycelium-ML (Evolution) |
|---|---|
| Synaptic connections are the weights | Protocol parameters are the weights |
| Trial and error (you reach for coffee 1000 times) | Mutation and selection (agents try different strategies 500 generations) |
| Reward signal (coffee reaches mouth = dopamine hit) | Fitness score (energy gained = agent survives) |
| Learning = synapses that fired together wire together | Evolution = agents that survived reproduce, passing on their "winning" parameters |
| Forgot what you learned? Reset the connections | Population crashed? Start over with random initial conditions |

The algorithm is the same. The substrate is different (neurons vs software agents). The timescale is different (milliseconds vs generations). But the logic is identical.

## Part 5: The Key Insight (Why This Matters)

Intelligence is not computation. Intelligence is selection pressure on variation.

A brain doesn't "think" in the sense of logic or reasoning. It:

1. Generates random variations (via neural noise, exploration).
2. Evaluates them against reality (reward signals, sensory feedback).
3. Keeps what works.
4. Discards what doesn't.

Your mycelium agents do the exact same thing:

1. Generate random protocol variations (mutation).
2. Evaluate them against the environment (energy, survival).
3. Keep what works (replication of successful agents).
4. Discard what doesn't (death of failed agents).

There is no ghost in the machine. No "intelligent planner" deciding the best strategy. Just mechanical rule: try, evaluate, keep winners, repeat.

And yet, intelligence emerges.

## Part 6: How Mycelium-ML Proves This

### Phase 1 (Current): Agents with fixed protocol

- Like a brain with frozen synapses
- Agents follow the same strategy every time
- Population survives, but doesn't improve
- Proof: static metrics, same agent behavior every generation

### Phase 2 (Next): Agents with mutation + replication

- Like a brain learning from experience
- Agents vary their strategy (mutation)
- Successful strategies spread (replication)
- Population improves over time
- Proof: protocol convergence, fitness increase, diversity changes

The comparison (Phase 1 vs Phase 2):

- Phase 1 = brain with frozen weights
- Phase 2 = brain that can learn
- Difference in performance = proof that learning works

## Part 7: Where Mycelium-ML Sits in ML (The Taxonomy)

Mycelium-ML = Embodied Genetic Algorithm + Behavioral Evolution + Swarm Intelligence.

Most ML algorithms are either:

- Fast but opaque: Neural networks + gradient descent (you get answers but can't read the logic)
- Slow but simple: Random search, brute force (interpretable but inefficient)

Mycelium-ml is different:

- Medium-speed + interpretable: You can read what agents "learned" (`sensing_range=7`, `growth_angle=48`)
- Embodied + realistic: Agents in real 3D environment consuming resources (not optimizing abstract math)
- Relational identity: Tests whether behavior persists through relation alone (minimal spore hypothesis)

How it differs from other algorithms:

| Algorithm | Population? | Evolution? | Gradient? | Embodied? | Interpretable? |
|---|---|---|---|---|---|
| Standard GA | Yes | Yes | No | No | Yes |
| NEAT (neuroevolution) | Yes | Yes | No | Yes | No (blackbox networks) |
| RL (Q-learning, policy gradient) | No | No | Yes | No | No |
| PSO (particle swarm) | Yes | No | No | No | Yes |
| Mycelium-ML | Yes | Yes | No | Yes | Yes |

Closest existing thing: embodied evolutionary robotics, but with ultra-simple controllers (protocols, not neural networks).

Why it matters: You don't need neural networks or calculus to get adaptive behavior. Simple rules + selection pressure + mutation = learning.

TL;DR: the algorithm is universal, the substrate doesn't matter.

## Part 8: The Recursion (Identity Through Relation)

Remember your insight about identity?

Identity isn't a fixed thing. Identity is the coherence of strategy over time.

In mycelium-ml:

1. Agent A has protocol (`sensing_range=5`, `angle=45`)
2. Agent A survives and reproduces
3. Agent B (child of A) has protocol (`sensing_range=5.2`, `angle=45.1`)
4. Agent B survives and reproduces
5. Agent C (child of B) has protocol (`sensing_range=5.1`, `angle=44.9`)

What is the identity of this lineage?

- Not the exact parameters (they change every generation)
- Not the individual agents (they die)
- It's the coherence: "this lineage tends toward `sensing_range ≈ 5` and `angle ≈ 45`"

Identity emerges from the relation between protocol and environment over time. The spore (the child) carries the protocol rule, which, when placed in an environment, expresses as behavior similar to the parent.

That's why minimal spores work. You don't need to store the exact parameters. You just need the rule (`protocol + lineage`). The environment will express it correctly.

## Part 9: What Comes Next

Deploy Phase 1 to overnight sweep.

Why? Because you need the data to write the rest of the story convincingly.

Tomorrow morning, you'll have:

1. Overnight sweep results (8 runs, different parameters)
2. Decision table (pass/fail breakdown)
3. Evidence that Phase 1 is stable across conditions

Then comes Phase 2: mutation + replication.

The full story:

- Phase 1: "Here's a population with fixed strategies. They survive, but they don't adapt."
- Phase 2: "Same conditions. Add mutation + selection. Watch what happens."
- The comparison: "The population learned. Not because they're smart. But because simple rules + selection pressure + variation = adaptation."

That's proof. That's the blog post with evidence.

## The Physiology Anchor (Why This Works)

You asked for every concept rooted in cognition/physiology. Here's the root:

Your brain's job is survival. Not thinking, not reasoning, survival.

Survival requires: sensing (input), action (behavior), evaluation (did I survive?).

Your brain runs this loop millions of times. It doesn't know calculus. It doesn't build models. It just:

1. Tries something (based on past success)
2. Sees what happens
3. Adjusts slightly toward what worked

That's the algorithm. Neurons are just the hardware it runs on.

Mycelium-ml is the same algorithm on a different substrate (agents on a grid). Same logic. Same outcome: adaptation without intention.

## Why This Matters (The Real Insight)

You don't need to be intelligent to learn. You don't need to think to adapt. You just need:

1. A way to vary your behavior (mutation)
2. A way to measure success (selection pressure)
3. A way to pass on what works (replication)

Everything else is details.

Your brain does this. Evolution does this. Mycelium-ml does this.

The algorithm is universal. The substrate doesn't matter.

## Next: Deploy and Gather Evidence

The blog post makes a claim. Phase 1 overnight sweep will provide the first evidence.

Tomorrow morning: decision table. If clean -> Phase 2. If fragile -> one bounded hardening cycle.

Then you'll have the data to write: "Here's what we learned from letting simple rules run unsupervised overnight."

That's when the story becomes proof.