#pragma once
#include <string>
#include <vector>

namespace resolver {

struct TaskInfo {
    int id = 0;
    int priority = 1;   // 1 low, 2 medium, 3 high (см. tasksManager.models.priorities)
    int days_left = 0;  // дней до end_date
};

// Id задач в порядке выполнения: сначала высокий приоритет, затем меньше дней до дедлайна.
std::vector<int> resolve_order(std::vector<TaskInfo> tasks);

std::string version();

}  // namespace resolver
