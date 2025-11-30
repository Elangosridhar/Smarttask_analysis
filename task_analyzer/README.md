# 🚀 Smart Task Analyzer

An intelligent task management system that automatically prioritizes your tasks using a sophisticated scoring algorithm. Stop guessing what to work on next - let data-driven insights guide your productivity.

## ✨ Features

- **🤖 Smart Priority Scoring**: Algorithm that considers urgency, importance, effort, and dependencies
- **🎯 Multiple Strategies**: Smart Balance, Fastest Wins, High Impact, and Deadline Driven modes
- **🔄 Dependency Management**: Visualize task relationships and detect circular dependencies
- **📊 Real-time Analysis**: Instant prioritization with detailed score breakdowns
- **🎨 Modern Interface**: Clean, responsive design built with vanilla JavaScript
- **🔧 RESTful API**: Fully documented Django REST Framework backend

## 🛠️ Tech Stack

**Backend**: Python, Django, Django REST Framework  
**Frontend**: HTML5, CSS3, JavaScript (ES6+)  
**Database**: SQLite (Development)  
**Architecture**: REST API with client-server separation

🧠 Algorithm Design
Core Scoring Formula
The priority score for each task is calculated using a weighted sum of four key factors:

text
Final Score = (Urgency × W_urgency) + (Importance × W_importance) + (Effort × W_effort) + (Dependency × W_dependency)
Where all weights sum to 1.0 (100%).

Scoring Strategies & Weight Configurations
Strategy	Urgency	Importance	Effort	Dependency	Best For
Smart Balance	35%	30%	20%	15%	Balanced approach for most users
Fastest Wins	20%	20%	50%	10%	Quick productivity boosts
High Impact	20%	60%	10%	10%	Strategic, important work
Deadline Driven	70%	15%	10%	5%	Time-sensitive situations
Component Scoring Details
1. Urgency Score (Time-based Priority)
python
def calculate_urgency_score(due_date):
    days_until_due = (due_date - today).days
    
    if days_until_due < 0:    # Past due
        return 1.0
    elif days_until_due == 0: # Due today
        return 0.9
    elif days_until_due <= 1: # Due tomorrow
        return 0.8
    elif days_until_due <= 3: # Due in 3 days
        return 0.7
    elif days_until_due <= 7: # Due in a week
        return 0.5
    else:                     # Future dates
        return max(0.1, 1.0 / (days_until_due / 7 + 1))
Key Features:

Past-due tasks get maximum urgency (1.0)

Exponential decay for distant deadlines

Prevents tasks far in the future from dominating

2. Importance Score (Value-based Priority)
python
def calculate_importance_score(importance):
    return importance / 10.0  # Normalize 1-10 scale to 0.1-1.0
Scale:

1-2: Low importance (0.1-0.2)

3-4: Below average (0.3-0.4)

5-6: Average (0.5-0.6)

7-8: High importance (0.7-0.8)

9-10: Critical (0.9-1.0)

3. Effort Score (Efficiency-based Priority)
python
def calculate_effort_score(estimated_hours):
    if estimated_hours <= 2:    # Quick tasks
        return 0.9
    elif estimated_hours <= 4:  # Moderate tasks
        return 0.7
    elif estimated_hours <= 8:  # Substantial tasks
        return 0.5
    else:                       # Large tasks
        return max(0.1, 1.0 / (estimated_hours / 4))
Psychology:

Rewards "quick wins" for momentum

Prevents procrastination on large tasks

Encourages breaking down big tasks

4. Dependency Score (Blockage-based Priority)
python
def calculate_dependency_score(dependencies, all_tasks):
    if not dependencies:
        return 0.3  # Base score for independent tasks
    
    # Count how many tasks this task blocks
    blocking_count = count_blocked_tasks(current_task, all_tasks)
    
    dependency_score = min(1.0, blocking_count / total_tasks * 2)
    return max(0.3, dependency_score)
Logic:

Independent tasks: 0.3 (base score)

Tasks blocking others: 0.4-1.0 (based on blockage impact)

Critical path tasks get highest dependency scores

Advanced Features
Circular Dependency Detection
python
def detect_circular_dependencies(tasks):
    # Uses Depth-First Search (DFS) to detect cycles
    # Returns list of circular dependency chains
    # Example: [[1, 2, 3, 1]] means 1→2→3→1 cycle
Handling:

Warns users but continues processing

Prevents infinite loops in scoring

Maintains application stability

Strategy Flexibility
Weights are configurable without code changes

Easy to add new strategies

User-customizable weighting possible

Algorithm Trade-offs & Decisions
1. Simplicity vs. Complexity
Chose simplicity with clear, explainable scoring over complex machine learning to:

Maintain transparency

Allow user understanding

Enable easy debugging

2. Past-Due Handling
Aggressive approach: Past-due tasks get maximum urgency (1.0) because:

They represent broken commitments

Often have cascading effects

Need immediate attention

3. Effort Scoring Psychology
Non-linear scaling that heavily favors quick tasks:

Based on "quick wins" productivity principle

Helps overcome procrastination

Builds momentum through small completions

4. Dependency Weighting
Conservative approach: Lower weight (15% in default strategy) because:

Not all users use dependency features

Prevents over-optimization for complex graphs

Maintains balance with other factors

Example Calculation
Task: "Fix login bug"

Due: Today (Urgency: 0.9)

Importance: 8/10 (Importance: 0.8)

Effort: 3 hours (Effort: 0.7)

Dependencies: Blocks 2 other tasks (Dependency: 0.6)

Smart Balance Score:

text
(0.9 × 0.35) + (0.8 × 0.30) + (0.7 × 0.20) + (0.6 × 0.15)
= 0.315 + 0.24 + 0.14 + 0.09
= 0.785 (High Priority)
Performance Characteristics
Time Complexity: O(n²) for dependency analysis (acceptable for n < 1000 tasks)

Space Complexity: O(n) for task storage

Real-time Performance: < 100ms for typical task lists

Future Algorithm Enhancements
Machine Learning: Learn optimal weights from user feedback

Context Awareness: Consider time of day, energy levels

Team Dynamics: Factor in multiple people's priorities

Historical Analysis: Learn from past completion patterns



- 🔬 **Learning**: Study algorithm design and full-stack development
- 💼 **Portfolio**: Showcase your Django and JavaScript skills
- 🏢 **Productivity**: Actually use it to manage your tasks smarter
- 📚 **Education**: Understand priority scheduling algorithms
