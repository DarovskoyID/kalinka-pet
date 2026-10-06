#include "task_resolver.hpp"

#include <algorithm>

namespace resolver {

std::vector<int> resolve_order(std::vector<TaskInfo> tasks) {
    std::vector<std::pair<int, int>> order;
    std::vector<int> weights = {15, -5};

    for (auto task : tasks) {
        int cost = task.priority * weights[0] + task.days_left * weights[1];
        order.push_back(std::make_pair(task.id, cost));
    }

    std::sort(order.begin(), order.end(), [](const auto& a, const auto& b) {return a.second > b.second;});
    std::vector<int> result;
    for (auto elem : order) {
        result.push_back(elem.first);
    }
    return result;
}

std::string version() { return "0.1.1"; }

}  // namespace resolver
