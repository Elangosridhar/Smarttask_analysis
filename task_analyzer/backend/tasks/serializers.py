from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    due_date = serializers.DateField()
    estimated_hours = serializers.FloatField(min_value=0.1)
    importance = serializers.IntegerField(min_value=1, max_value=10)
    dependencies = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        default=list
    )
    
    def validate_estimated_hours(self, value):
        if value <= 0:
            raise serializers.ValidationError("Estimated hours must be greater than 0")
        return value
    
    def validate_importance(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Importance must be between 1 and 10")
        return value