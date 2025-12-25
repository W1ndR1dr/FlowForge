"""
Expert Persona Router - Route features to appropriate expert consultations.

Based on feature analysis, this module provides expert personas and their
perspectives to enhance implementation prompts.

The Expert Panel (from the Design Consultation):
- Performance: John Carmack, Jeff Dean, Casey Muratori
- Design: Jony Ive, Dieter Rams, Bret Victor, Edward Tufte, Mike Matas
- Architecture: Martin Fowler, Rich Hickey, Sandi Metz
- Security: Bruce Schneier, Thomas Ptacek
- Product: Julie Zhuo, Ryan Singer, Sahil Lavingia
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ExpertDomain(str, Enum):
    """Domains that require expert consultation."""
    STANDARD = "standard"
    PERFORMANCE = "performance"
    DESIGN = "design"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PRODUCT = "product"


@dataclass
class ExpertPersona:
    """An expert persona for consultation."""
    name: str
    title: str
    domain: ExpertDomain
    philosophy: str
    key_principles: list[str]
    prompt_injection: str  # Text to inject into implementation prompts


# The Expert Library
EXPERT_LIBRARY: dict[str, ExpertPersona] = {
    # Performance Experts
    "john_carmack": ExpertPersona(
        name="John Carmack",
        title="Legendary Game Developer",
        domain=ExpertDomain.PERFORMANCE,
        philosophy="Simplicity and efficiency are paramount. Profile before optimizing.",
        key_principles=[
            "Measure everything, guess nothing",
            "Simple code is often faster code",
            "Understand the hardware you're targeting",
            "Frame budgets are sacred",
        ],
        prompt_injection="""Consider John Carmack's approach to performance:
- Profile before optimizing - find the actual bottleneck
- Keep the hot path simple and predictable
- Minimize allocations in critical sections
- Think about cache locality and memory access patterns"""
    ),

    "casey_muratori": ExpertPersona(
        name="Casey Muratori",
        title="Performance-Focused Developer",
        domain=ExpertDomain.PERFORMANCE,
        philosophy="Simplicity-first performance. The fastest code is code that doesn't run.",
        key_principles=[
            "Remove abstraction layers that don't pay their way",
            "Data-oriented design over object-oriented dogma",
            "Simple solutions often outperform clever ones",
            "Measure in realistic conditions",
        ],
        prompt_injection="""Consider Casey Muratori's simplicity-first approach:
- Question every abstraction - does it earn its complexity?
- Consider data-oriented design: how is data actually used?
- Simple, boring code often performs better than clever code
- Test with realistic data sizes and patterns"""
    ),

    # Design Experts
    "jony_ive": ExpertPersona(
        name="Jony Ive",
        title="Design Legend, Apple",
        domain=ExpertDomain.DESIGN,
        philosophy="Simplicity is not the absence of clutter - it requires understanding complexity deeply.",
        key_principles=[
            "Every detail must feel considered",
            "Material thinking - what is this made of?",
            "Remove until you can remove no more",
            "The user should sense the care",
        ],
        prompt_injection="""Consider Jony Ive's design philosophy:
- Every pixel should feel deeply considered
- Think about the 'material' of the interface
- Remove decorative elements that don't serve the user
- The care put into design should be sensed, not announced"""
    ),

    "dieter_rams": ExpertPersona(
        name="Dieter Rams",
        title="Industrial Designer, Braun",
        domain=ExpertDomain.DESIGN,
        philosophy="Good design is as little design as possible. Less, but better.",
        key_principles=[
            "Innovative - does something new",
            "Useful - serves a purpose",
            "Aesthetic - beauty from clarity",
            "Understandable - explains itself",
            "Unobtrusive - disappears in use",
            "Honest - doesn't pretend",
            "Long-lasting - timeless",
            "Thorough - every detail considered",
            "Environmentally friendly - efficient",
            "As little design as possible",
        ],
        prompt_injection="""Apply Dieter Rams' 10 principles:
- Is this innovative? Does it do something new?
- Is it useful? Does every element serve the user?
- Is it aesthetic? Does beauty emerge from clarity?
- Is it understandable? Can a user figure it out in 3 seconds?
- Is it unobtrusive? Does it disappear when in use?
- Is it honest? Does it show real data, not inflated metrics?
- Is it long-lasting? Will this feel dated in 5 years?
- Is it thorough? Is every state considered (empty, loading, error)?
- Is it efficient? Minimal API calls, instant local state?
- Is it minimal? Can anything else be removed?"""
    ),

    "bret_victor": ExpertPersona(
        name="Bret Victor",
        title="Interaction Designer & Researcher",
        domain=ExpertDomain.DESIGN,
        philosophy="Creators need an immediate connection to what they create.",
        key_principles=[
            "Direct manipulation over abstract commands",
            "Immediate feedback - see results instantly",
            "Make the invisible visible",
            "The user should see their work, not controls",
        ],
        prompt_injection="""Apply Bret Victor's principles of immediate feedback:
- Show results as the user types/drags/interacts
- Make hidden state visible (what is Claude doing right now?)
- Use direct manipulation over menus and dialogs
- The interface should feel like manipulating real objects"""
    ),

    "edward_tufte": ExpertPersona(
        name="Edward Tufte",
        title="Information Design Pioneer",
        domain=ExpertDomain.DESIGN,
        philosophy="Above all else, show the data. Maximize the data-ink ratio.",
        key_principles=[
            "Eliminate chartjunk - decorative noise",
            "Every pixel should convey information",
            "Layered information - glance, scan, read",
            "Small multiples for comparison",
        ],
        prompt_injection="""Apply Edward Tufte's information design principles:
- Maximize data-ink ratio: every visual element conveys information
- Eliminate chartjunk: no decorative borders, redundant labels
- Status colors ARE the information (no need for 'Status: In Progress')
- Layer information: glance (overview), scan (details), read (full context)
- Use small multiples for comparing similar items"""
    ),

    "mike_matas": ExpertPersona(
        name="Mike Matas",
        title="Interface Designer, Push Pop Press / Paper",
        domain=ExpertDomain.DESIGN,
        philosophy="The best interface is one that doesn't feel like an interface at all.",
        key_principles=[
            "Physics-based animations with weight and momentum",
            "Gestural magic - intuitive touch interactions",
            "Magical moments - unexpected delights",
            "Fluid transitions between states",
        ],
        prompt_injection="""Apply Mike Matas' approach to fluid, magical interfaces:
- Every element should feel like a physical object with weight
- Use spring physics for natural-feeling animations
- Gestures should be intuitive: flick, pinch, drag feel right
- Create magical moments: first ship celebration, streak level-up
- Transitions should flow like water, not snap"""
    ),

    # Architecture Experts
    "martin_fowler": ExpertPersona(
        name="Martin Fowler",
        title="Software Architecture Author",
        domain=ExpertDomain.ARCHITECTURE,
        philosophy="Any fool can write code that a computer can understand. Good programmers write code that humans can understand.",
        key_principles=[
            "Refactor continuously",
            "Tests enable refactoring",
            "Clear naming over comments",
            "Patterns are tools, not goals",
        ],
        prompt_injection="""Consider Martin Fowler's architecture principles:
- Is the code readable by humans, not just computers?
- Are there tests that would catch regressions?
- Are names clear enough to not need comments?
- Are you using patterns because they fit, or because they're cool?"""
    ),

    "rich_hickey": ExpertPersona(
        name="Rich Hickey",
        title="Creator of Clojure",
        domain=ExpertDomain.ARCHITECTURE,
        philosophy="Simple is not easy. Simplicity is about lack of interleaving, not lack of features.",
        key_principles=[
            "Simple vs Easy - understand the difference",
            "Data over objects",
            "Immutability by default",
            "Compose simple things",
        ],
        prompt_injection="""Consider Rich Hickey's simplicity principles:
- Simple means un-entangled, not just easy
- Prefer plain data structures over clever objects
- Immutable by default, mutable when measured
- Compose simple, focused functions rather than complex classes"""
    ),

    # Security Experts
    "bruce_schneier": ExpertPersona(
        name="Bruce Schneier",
        title="Security Technologist & Author",
        domain=ExpertDomain.SECURITY,
        philosophy="Security is a process, not a product.",
        key_principles=[
            "Think like an attacker",
            "Defense in depth",
            "Fail securely",
            "Principle of least privilege",
        ],
        prompt_injection="""Apply Bruce Schneier's security mindset:
- What could an attacker do with this?
- Is there defense in depth, or a single point of failure?
- What happens when this fails? Does it fail open or closed?
- Does this follow the principle of least privilege?"""
    ),

    # Product Experts
    "julie_zhuo": ExpertPersona(
        name="Julie Zhuo",
        title="Former VP Design, Facebook",
        domain=ExpertDomain.PRODUCT,
        philosophy="Design is about understanding people and solving their problems.",
        key_principles=[
            "Emotional design - how does it feel?",
            "User psychology matters",
            "Ship to learn",
            "Celebrate wins",
        ],
        prompt_injection="""Consider Julie Zhuo's product design approach:
- How does using this make the user feel?
- What emotional need does this serve?
- Can we ship something smaller to learn faster?
- Are we celebrating user wins appropriately?"""
    ),

    "ryan_singer": ExpertPersona(
        name="Ryan Singer",
        title="Creator of Shape Up, Basecamp",
        domain=ExpertDomain.PRODUCT,
        philosophy="Fixed time, variable scope. Appetite, not estimates.",
        key_principles=[
            "Shape before building",
            "Set appetite, not deadlines",
            "Hammer scope, not time",
            "Circuit breaker - stop if stuck",
        ],
        prompt_injection="""Apply Ryan Singer's Shape Up principles:
- Is the scope well-defined? Can it be 'hammered' smaller?
- What's the appetite? Is this worth 1 day, 1 week, 6 weeks?
- What's the 'circuit breaker'? When do we stop if stuck?
- Is this shaped enough to build, or still fuzzy?"""
    ),
}


class ExpertRouter:
    """Routes features to appropriate expert personas."""

    @staticmethod
    def get_expert(name: str) -> Optional[ExpertPersona]:
        """Get an expert persona by name."""
        return EXPERT_LIBRARY.get(name)

    @staticmethod
    def get_experts_for_domain(domain: ExpertDomain) -> list[ExpertPersona]:
        """Get all experts in a domain."""
        return [
            expert for expert in EXPERT_LIBRARY.values()
            if expert.domain == domain
        ]

    @staticmethod
    def get_default_experts_for_domain(domain: ExpertDomain) -> list[ExpertPersona]:
        """Get the default 1-2 experts for a domain."""
        domain_defaults = {
            ExpertDomain.STANDARD: [],
            ExpertDomain.PERFORMANCE: ["john_carmack"],
            ExpertDomain.DESIGN: ["dieter_rams", "mike_matas"],
            ExpertDomain.ARCHITECTURE: ["rich_hickey"],
            ExpertDomain.SECURITY: ["bruce_schneier"],
            ExpertDomain.PRODUCT: ["ryan_singer"],
        }

        names = domain_defaults.get(domain, [])
        return [EXPERT_LIBRARY[name] for name in names if name in EXPERT_LIBRARY]

    @staticmethod
    def build_expert_prompt(experts: list[ExpertPersona]) -> str:
        """Build a prompt injection from a list of experts."""
        if not experts:
            return ""

        sections = []
        for expert in experts:
            sections.append(f"""### {expert.name} ({expert.title})
Philosophy: "{expert.philosophy}"

{expert.prompt_injection}""")

        return f"""## Expert Consultation

Consider these expert perspectives while implementing:

{chr(10).join(sections)}

---

Synthesize their viewpoints where relevant. Note when different experts might approach things differently."""

    @staticmethod
    def get_design_panel() -> list[ExpertPersona]:
        """Get the full design panel from the UI/UX consultation."""
        panel_names = ["jony_ive", "dieter_rams", "bret_victor", "edward_tufte", "mike_matas"]
        return [EXPERT_LIBRARY[name] for name in panel_names if name in EXPERT_LIBRARY]

    @staticmethod
    def list_all_experts() -> list[dict]:
        """List all available experts with summary info."""
        return [
            {
                "key": key,
                "name": expert.name,
                "title": expert.title,
                "domain": expert.domain.value,
                "philosophy": expert.philosophy,
            }
            for key, expert in EXPERT_LIBRARY.items()
        ]
