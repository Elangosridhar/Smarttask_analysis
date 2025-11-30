from datetime import date, timedelta
from typing import List, Dict, Any

class TaskScorer:
    def __init__(self, strategy="smart_balance"):
        self.strategy = strategy
        self.config = {
            "smart_balance": {
                "urgency_weight": 0.35,
                "importance_weight": 0.30,
                "effort_weight": 0.20,
                "dependency_weight": 0.15
            },
            "fastest_wins": {
                "urgency_weight": 0.20,
                "importance_weight": 0.20,
                "effort_weight": 0.50,
                "dependency_weight": 0.10
            },
            "high_impact": {
                "urgency_weight": 0.20,
                "importance_weight": 0.60,
                "effort_weight": 0.10,
                "dependency_weight": 0.10
            },
            "deadline_driven": {
                "urgency_weight": 0.70,
                "importance_weight": 0.15,
                "effort_weight": 0.10,
                "dependency_weight": 0.05
            }
        }
    
    def calculate_urgency_score(self, due_date: str, today: date = None) -> float:
        """Calculate urgency score based on due date"""
        if today is None:
            today = date.today()
        
        due_date_obj = due_date if isinstance(due_date, date) else date.fromisoformat(due_date)
        days_until_due = (due_date_obj - today).days
        
        # Handle past due dates - they get highest urgency
        if days_until_due < 0:
            return 1.0  # Maximum urgency for overdue tasks
        
        # Normalize urgency: tasks due sooner get higher scores
        if days_until_due == 0:
            return 0.9
        elif days_until_due <= 1:
            return 0.8
        elif days_until_due <= 3:
            return 0.7
        elif days_until_due <= 7:
            return 0.5
        else:
            # Exponential decay for further dates
            return max(0.1, 1.0 / (days_until_due / 7 + 1))
    
    def calculate_importance_score(self, importance: int) -> float:
        """Normalize importance to 0-1 scale"""
        return importance / 10.0
    
    def calculate_effort_score(self, estimated_hours: float) -> float:
        """Calculate effort score - lower effort gets higher score"""
        # Normalize effort: tasks taking <= 2 hours get high score, >8 hours get low score
        if estimated_hours <= 2:
            return 0.9
        elif estimated_hours <= 4:
            return 0.7
        elif estimated_hours <= 8:
            return 0.5
        else:
            return max(0.1, 1.0 / (estimated_hours / 4))
    
    def calculate_dependency_score(self, dependencies: List[int], all_tasks: List[Dict]) -> float:
        """Calculate dependency score - tasks with more dependencies get higher score"""
        if not dependencies:
            return 0.3  # Base score for independent tasks
        
        # Check if this task blocks other tasks
        blocking_count = 0
        current_task_ids = [task.get('id', i) for i, task in enumerate(all_tasks)]
        
        for task in all_tasks:
            task_deps = task.get('dependencies', [])
            # If this task's ID is in another task's dependencies, it's blocking
            if any(dep in current_task_ids for dep in task_deps):
                blocking_count += 1
        
        # Normalize based on how many tasks this blocks
        total_tasks = len(all_tasks)
        if total_tasks == 0:
            return 0.5
        
        dependency_score = min(1.0, blocking_count / total_tasks * 2)
        return max(0.3, dependency_score)
    
    def detect_circular_dependencies(self, tasks: List[Dict]) -> List[List[int]]:
        """Detect circular dependencies in the task graph"""
        circular_deps = []
        task_dict = {i: task for i, task in enumerate(tasks)}
        
        def dfs(current, visited, path):
            if current in visited:
                if current in path:
                    cycle_start = path.index(current)
                    cycle = path[cycle_start:]
                    if len(cycle) > 1 and cycle not in circular_deps:
                        circular_deps.append(cycle)
                return
            
            visited.add(current)
            path.append(current)
            
            for dep in task_dict[current].get('dependencies', []):
                if dep in task_dict:
                    dfs(dep, visited, path)
            
            path.pop()
        
        for task_id in task_dict:
            dfs(task_id, set(), [])
        
        return circular_deps
    
    def calculate_task_score(self, task: Dict, all_tasks: List[Dict], strategy: str = None) -> Dict:
        """Calculate comprehensive score for a single task"""
        if strategy is None:
            strategy = self.strategy
        
        weights = self.config.get(strategy, self.config["smart_balance"])
        
        # Calculate individual component scores
        urgency_score = self.calculate_urgency_score(task['due_date'])
        importance_score = self.calculate_importance_score(task['importance'])
        effort_score = self.calculate_effort_score(task['estimated_hours'])
        dependency_score = self.calculate_dependency_score(task.get('dependencies', []), all_tasks)
        
        # Calculate weighted final score
        final_score = (
            urgency_score * weights["urgency_weight"] +
            importance_score * weights["importance_weight"] +
            effort_score * weights["effort_weight"] +
            dependency_score * weights["dependency_weight"]
        )
        
        return {
            'task': task,
            'final_score': round(final_score, 3),
            'component_scores': {
                'urgency': round(urgency_score, 3),
                'importance': round(importance_score, 3),
                'effort': round(effort_score, 3),
                'dependency': round(dependency_score, 3)
            },
            'explanation': self.generate_explanation(task, final_score, urgency_score, 
                                                   importance_score, effort_score, dependency_score)
        }
    
    def generate_explanation(self, task, final_score, urgency, importance, effort, dependency):
        """Generate human-readable explanation for the score"""
        factors = []
        
        if urgency > 0.7:
            factors.append("very urgent")
        elif urgency > 0.4:
            factors.append("moderately urgent")
        
        if importance > 0.7:
            factors.append("high importance")
        elif importance > 0.4:
            factors.append("moderate importance")
        
        if effort > 0.7:
            factors.append("quick to complete")
        elif effort < 0.3:
            factors.append("time-consuming")
        
        if dependency > 0.6:
            factors.append("blocks other tasks")
        
        if not factors:
            factors.append("average priority")
        
        explanation = f"This task is {', '.join(factors)}."
        
        if final_score > 0.7:
            priority = "High"
        elif final_score > 0.4:
            priority = "Medium"
        else:
            priority = "Low"
        
        return f"{priority} priority: {explanation}"
    
    def analyze_tasks(self, tasks: List[Dict], strategy: str = "smart_balance") -> List[Dict]:
        """Analyze and sort all tasks by priority"""
        # Validate tasks
        if not tasks:
            return []
        
        # Detect circular dependencies
        circular_deps = self.detect_circular_dependencies(tasks)
        if circular_deps:
            # For circular dependencies, we'll still process but note it
            print(f"Warning: Circular dependencies detected: {circular_deps}")
        
        # Calculate scores for all tasks
        scored_tasks = []
        for task in tasks:
            scored_task = self.calculate_task_score(task, tasks, strategy)
            scored_tasks.append(scored_task)
        
        # Sort by final score (descending)
        scored_tasks.sort(key=lambda x: x['final_score'], reverse=True)
        
        return scored_tasks
    
    def suggest_top_tasks(self, tasks: List[Dict], strategy: str = "smart_balance", top_n: int = 3) -> Dict:
        """Get top N tasks with explanations"""
        analyzed_tasks = self.analyze_tasks(tasks, strategy)
        
        return {
            'strategy': strategy,
            'top_tasks': analyzed_tasks[:top_n],
            'total_tasks_analyzed': len(tasks),
            'circular_dependencies': self.detect_circular_dependencies(tasks)
        }