from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import date, timedelta
from .scoring import TaskScorer
from .serializers import TaskSerializer

@api_view(['POST'])
def analyze_tasks(request):
    """
    Analyze and sort tasks by priority score
    """
    try:
        tasks = request.data.get('tasks', [])
        strategy = request.data.get('strategy', 'smart_balance')
        
        # Validate tasks using serializer
        for task in tasks:
            serializer = TaskSerializer(data=task)
            if not serializer.is_valid():
                return Response({
                    'error': 'Invalid task data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Analyze tasks
        scorer = TaskScorer()
        analyzed_tasks = scorer.analyze_tasks(tasks, strategy)
        
        return Response({
            'strategy': strategy,
            'tasks': analyzed_tasks,
            'total_tasks': len(tasks)
        })
        
    except Exception as e:
        return Response({
            'error': 'Internal server error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def suggest_tasks(request):
    """
    Get top 3 suggested tasks to work on
    """
    try:
        # For GET request, we'll use sample data or accept tasks as query params
        # In a real app, you might have persistent storage
        sample_tasks = [
            {
                'title': 'Fix critical login bug',
                'due_date': str(date.today()),
                'estimated_hours': 3,
                'importance': 9,
                'dependencies': []
            },
            {
                'title': 'Write documentation',
                'due_date': str(date.today() + timedelta(days=7)),
                'estimated_hours': 2,
                'importance': 6,
                'dependencies': []
            },
            {
                'title': 'Refactor user profile page',
                'due_date': str(date.today() + timedelta(days=3)),
                'estimated_hours': 5,
                'importance': 7,
                'dependencies': [0]  # Depends on task 0
            }
        ]
        
        strategy = request.GET.get('strategy', 'smart_balance')
        scorer = TaskScorer()
        suggestions = scorer.suggest_top_tasks(sample_tasks, strategy)
        
        return Response(suggestions)
        
    except Exception as e:
        return Response({
            'error': 'Internal server error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)