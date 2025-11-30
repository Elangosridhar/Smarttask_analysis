from django.test import TestCase
from datetime import date, timedelta
from .scoring import TaskScorer

class TaskScoringTestCase(TestCase):
    def setUp(self):
        self.scorer = TaskScorer()
        self.sample_tasks = [
            {
                'title': 'Urgent Important Task',
                'due_date': str(date.today()),
                'estimated_hours': 2,
                'importance': 9,
                'dependencies': []
            },
            {
                'title': 'Future Task',
                'due_date': str(date.today() + timedelta(days=30)),
                'estimated_hours': 8,
                'importance': 3,
                'dependencies': []
            }
        ]
    
    def test_urgency_score_calculation(self):
        # Test today's date - should be high urgency
        today_score = self.scorer.calculate_urgency_score(str(date.today()))
        self.assertGreater(today_score, 0.8)
        
        # Test future date - should be lower urgency
        future_score = self.scorer.calculate_urgency_score(str(date.today() + timedelta(days=30)))
        self.assertLess(future_score, 0.5)
        
        # Test past due date - should be highest urgency
        past_score = self.scorer.calculate_urgency_score(str(date.today() - timedelta(days=1)))
        self.assertEqual(past_score, 1.0)
    
    def test_importance_score_calculation(self):
        self.assertEqual(self.scorer.calculate_importance_score(10), 1.0)
        self.assertEqual(self.scorer.calculate_importance_score(5), 0.5)
        self.assertEqual(self.scorer.calculate_importance_score(1), 0.1)
    
    def test_effort_score_calculation(self):
        # Low effort should get high score
        low_effort_score = self.scorer.calculate_effort_score(1)
        self.assertGreater(low_effort_score, 0.8)
        
        # High effort should get low score
        high_effort_score = self.scorer.calculate_effort_score(10)
        self.assertLess(high_effort_score, 0.5)
    
    def test_task_analysis(self):
        analyzed_tasks = self.scorer.analyze_tasks(self.sample_tasks)
        
        # Should return both tasks
        self.assertEqual(len(analyzed_tasks), 2)
        
        # Urgent important task should be first
        self.assertEqual(analyzed_tasks[0]['task']['title'], 'Urgent Important Task')
        self.assertGreater(analyzed_tasks[0]['final_score'], analyzed_tasks[1]['final_score'])
    
    def test_circular_dependency_detection(self):
        tasks_with_circular_deps = [
            {
                'title': 'Task A',
                'due_date': str(date.today()),
                'estimated_hours': 2,
                'importance': 5,
                'dependencies': [1]  # Depends on Task B
            },
            {
                'title': 'Task B',
                'due_date': str(date.today()),
                'estimated_hours': 2,
                'importance': 5,
                'dependencies': [0]  # Depends on Task A - circular!
            }
        ]
        
        circular_deps = self.scorer.detect_circular_dependencies(tasks_with_circular_deps)
        self.assertEqual(len(circular_deps), 1)
        self.assertEqual(len(circular_deps[0]), 2)