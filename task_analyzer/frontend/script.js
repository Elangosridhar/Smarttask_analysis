class TaskManager {
    constructor() {
        this.tasks = [];
        this.currentTaskId = 0;
        this.apiBaseUrl = 'http://localhost:8000/api'; // Keep for potential API fallback
        
        this.initializeEventListeners();
        this.loadSampleTasks();
    }
    
    initializeEventListeners() {
        // Task form submission
        document.getElementById('taskForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addTaskFromForm();
        });
        
        // Enter key in bulk input
        document.getElementById('bulkInput').addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.loadBulkTasks();
            }
        });
    }
    
    loadSampleTasks() {
        // Load some sample tasks to get started
        const sampleTasks = [
            {
                title: 'Fix critical login bug',
                due_date: this.getFormattedDate(new Date()),
                estimated_hours: 3,
                importance: 9,
                dependencies: []
            },
            {
                title: 'Write API documentation',
                due_date: this.getFormattedDate(new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)),
                estimated_hours: 4,
                importance: 7,
                dependencies: [0]
            },
            {
                title: 'Update user profile page design',
                due_date: this.getFormattedDate(new Date(Date.now() + 3 * 24 * 60 * 60 * 1000)),
                estimated_hours: 6,
                importance: 6,
                dependencies: []
            }
        ];
        
        this.tasks = sampleTasks.map((task, index) => ({
            ...task,
            id: index
        }));
        this.currentTaskId = this.tasks.length;
        this.updateTaskList();
    }
    
    getFormattedDate(date) {
        return date.toISOString().split('T')[0];
    }
    
    addTaskFromForm() {
        const title = document.getElementById('title').value;
        const dueDate = document.getElementById('dueDate').value;
        const estimatedHours = parseFloat(document.getElementById('estimatedHours').value);
        const importance = parseInt(document.getElementById('importance').value);
        const dependencies = document.getElementById('dependencies').value
            .split(',')
            .map(dep => dep.trim())
            .filter(dep => dep !== '')
            .map(dep => parseInt(dep));
        
        // Validate dependencies exist
        const invalidDeps = dependencies.filter(dep => dep >= this.currentTaskId);
        if (invalidDeps.length > 0) {
            alert(`Invalid dependencies: ${invalidDeps.join(', ')}. Task IDs only go up to ${this.currentTaskId - 1}`);
            return;
        }
        
        const newTask = {
            id: this.currentTaskId++,
            title,
            due_date: dueDate,
            estimated_hours: estimatedHours,
            importance,
            dependencies
        };
        
        this.tasks.push(newTask);
        this.updateTaskList();
        this.clearForm();
    }
    
    clearForm() {
        document.getElementById('taskForm').reset();
        document.getElementById('dueDate').value = '';
    }
    
    updateTaskList() {
        const taskList = document.getElementById('taskList');
        taskList.innerHTML = '';
        
        this.tasks.forEach((task, index) => {
            const taskElement = document.createElement('div');
            taskElement.className = 'task-item';
            taskElement.innerHTML = `
                <div class="task-info">
                    <div class="task-title">${task.title}</div>
                    <div class="task-details">
                        Due: ${task.due_date} | Hours: ${task.estimated_hours} | 
                        Importance: ${task.importance}/10 | 
                        Dependencies: [${task.dependencies.join(', ')}]
                    </div>
                </div>
                <button class="remove-task" onclick="taskManager.removeTask(${index})">×</button>
            `;
            taskList.appendChild(taskElement);
        });
    }
    
    removeTask(index) {
        this.tasks.splice(index, 1);
        this.updateTaskList();
    }
    
    loadBulkTasks() {
        const bulkInput = document.getElementById('bulkInput').value;
        
        if (!bulkInput.trim()) {
            alert('Please enter some JSON data');
            return;
        }
        
        try {
            const newTasks = JSON.parse(bulkInput);
            
            if (!Array.isArray(newTasks)) {
                throw new Error('Input must be a JSON array');
            }
            
            // Add new tasks with proper IDs
            newTasks.forEach(task => {
                this.tasks.push({
                    ...task,
                    id: this.currentTaskId++
                });
            });
            
            this.updateTaskList();
            document.getElementById('bulkInput').value = '';
            
        } catch (error) {
            alert('Invalid JSON format: ' + error.message);
        }
    }
    
    async analyzeTasks() {
        if (this.tasks.length === 0) {
            alert('Please add some tasks first');
            return;
        }
        
        const strategy = document.getElementById('strategy').value;
        
        // Show loading
        this.showLoading();
        this.hideError();
        
        try {
            // Try API first, fallback to local calculation if API fails
            const response = await fetch(`${this.apiBaseUrl}/tasks/analyze/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    tasks: this.tasks,
                    strategy: strategy
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.displayResults(data);
            } else {
                throw new Error('API unavailable, using local calculation');
            }
            
        } catch (error) {
            console.warn('API failed, falling back to local analysis:', error.message);
            // Fallback to local analysis
            this.localAnalyzeTasks(strategy);
        } finally {
            this.hideLoading();
        }
    }
    
    // Local analysis method (fallback)
    localAnalyzeTasks(strategy) {
        const now = new Date();
        const analyzedTasks = this.tasks.map(task => {
            const dueDate = new Date(task.due_date);
            const daysUntilDue = Math.max(0, Math.ceil((dueDate - now) / (1000 * 60 * 60 * 24)));
            
            let finalScore = 0;
            let componentScores = { urgency: 0, importance: 0, effort: 0, dependency: 0 };
            let explanation = '';
            
            switch (strategy) {
                case 'smart_balance':
                    const urgencyScore = daysUntilDue === 0 ? 1.0 : Math.max(0, 1.0 - daysUntilDue * 0.02);
                    const importanceScore = task.importance / 10;
                    const effortScore = Math.max(0, 1.0 - task.estimated_hours * 0.05);
                    const dependencyScore = Math.max(0, 1.0 - task.dependencies.length * 0.1);
                    finalScore = (urgencyScore * 0.3) + (importanceScore * 0.3) + (effortScore * 0.2) + (dependencyScore * 0.2);
                    componentScores = { 
                        urgency: urgencyScore.toFixed(2), 
                        importance: importanceScore.toFixed(2), 
                        effort: effortScore.toFixed(2), 
                        dependency: dependencyScore.toFixed(2) 
                    };
                    explanation = `Balanced prioritization considering urgency, importance, effort, and dependencies.`;
                    break;
                case 'fastest_wins':
                    finalScore = Math.max(0, 1.0 - task.estimated_hours * 0.1);
                    componentScores.effort = finalScore.toFixed(2);
                    explanation = `Prioritizing based on estimated effort - shorter tasks first.`;
                    break;
                case 'high_impact':
                    finalScore = task.importance / 10;
                    componentScores.importance = finalScore.toFixed(2);
                    explanation = `Prioritizing based on importance rating.`;
                    break;
                case 'deadline_driven':
                    finalScore = daysUntilDue === 0 ? 1.0 : Math.max(0, 1.0 - daysUntilDue * 0.02);
                    componentScores.urgency = finalScore.toFixed(2);
                    explanation = `Prioritizing based on deadline urgency.`;
                    break;
            }
            
            return {
                task,
                final_score: parseFloat(finalScore.toFixed(2)),
                component_scores: componentScores,
                explanation
            };
        });
        
        // Sort by score descending, then by dependencies
        analyzedTasks.sort((a, b) => {
            if (a.final_score !== b.final_score) return b.final_score - a.final_score;
            return a.task.dependencies.length - b.task.dependencies.length;
        });
        
        // Check for circular dependencies
        const circularDeps = this.detectCircularDependencies();
        
        const data = {
            tasks: analyzedTasks,
            circular_dependencies: circularDeps
        };
        
        this.displayResults(data);
    }
    
    // Detect circular dependencies
    detectCircularDependencies() {
        const graph = {};
        const visited = new Set();
        const recStack = new Set();
        
        // Build graph
        this.tasks.forEach(task => {
            graph[task.id] = task.dependencies;
        });
        
        function hasCycle(node) {
            if (recStack.has(node)) return true;
            if (visited.has(node)) return false;
            
            visited.add(node);
            recStack.add(node);
            
            for (const dep of graph[node] || []) {
                if (hasCycle(dep)) return true;
            }
            
            recStack.delete(node);
            return false;
        }
        
        const cycles = [];
        for (const task of this.tasks) {
            if (hasCycle(task.id)) {
                cycles.push(task.id);
            }
        }
        
        return cycles;
    }
    
    displayResults(data) {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = '';
        
        if (data.circular_dependencies && data.circular_dependencies.length > 0) {
            const warningDiv = document.createElement('div');
            warningDiv.className = 'circular-deps-warning';
            warningDiv.innerHTML = `
                <strong>Warning: Circular dependencies detected!</strong>
                <br>This may affect task prioritization.
            `;
            resultsDiv.appendChild(warningDiv);
        }
        
        data.tasks.forEach((scoredTask, index) => {
            const taskDiv = document.createElement('div');
            
            let priorityClass = 'priority-medium';
            if (scoredTask.final_score > 0.7) {
                priorityClass = 'priority-high';
            } else if (scoredTask.final_score < 0.4) {
                priorityClass = 'priority-low';
            }
            
            taskDiv.className = `priority-task ${priorityClass}`;
            taskDiv.innerHTML = `
                <div class="task-header">
                    <h3>${index + 1}. ${scoredTask.task.title}</h3>
                    <div class="task-score">${scoredTask.final_score}</div>
                </div>
                <div class="task-explanation">${scoredTask.explanation}</div>
                <div class="task-details">
                    <strong>Due:</strong> ${scoredTask.task.due_date} | 
                    <strong>Hours:</strong> ${scoredTask.task.estimated_hours} | 
                    <strong>Importance:</strong> ${scoredTask.task.importance}/10 | 
                    <strong>Dependencies:</strong> [${scoredTask.task.dependencies.join(', ')}]
                </div>
                <div class="score-breakdown">
                    <div class="score-item">
                        <div class="score-label">Urgency</div>
                        <div class="score-value">${scoredTask.component_scores.urgency}</div>
                    </div>
                    <div class="score-item">
                        <div class="score-label">Importance</div>
                        <div class="score-value">${scoredTask.component_scores.importance}</div>
                    </div>
                    <div class="score-item">
                        <div class="score-label">Effort</div>
                        <div class="score-value">${scoredTask.component_scores.effort}</div>
                    </div>
                    <div class="score-item">
                        <div class="score-label">Dependency</div>
                        <div class="score-value">${scoredTask.component_scores.dependency}</div>
                    </div>
                </div>
            `;
            
            resultsDiv.appendChild(taskDiv);
        });
    }
    
    showLoading() {
        document.getElementById('loading').classList.remove('hidden');
        document.getElementById('results').innerHTML = '';
    }
    
    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
    }
    
    showError(message) {
        const errorDiv = document.getElementById('error');
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
    }
    
    hideError() {
        document.getElementById('error').classList.add('hidden');
    }
    
    clearAllTasks() {
        if (confirm('Are you sure you want to clear all tasks?')) {
            this.tasks = [];
            this.currentTaskId = 0;
            this.updateTaskList();
            document.getElementById('results').innerHTML = '';
            this.hideError();
        }
    }
}

// Global functions for HTML onclick handlers
function analyzeTasks() {
    taskManager.analyzeTasks();
}

function loadBulkTasks() {
    taskManager.loadBulkTasks();
}

function clearAllTasks() {
    taskManager.clearAllTasks();
}

// Initialize the task manager when page loads
let taskManager;
document.addEventListener('DOMContentLoaded', () => {
    taskManager = new TaskManager();
    
    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('dueDate').min = today;
});
