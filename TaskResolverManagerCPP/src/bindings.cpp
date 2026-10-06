#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>

#include "task_resolver.hpp"

namespace nb = nanobind;
using namespace resolver;

// Чтобы экспортировать новую функцию в Python: объяви её в task_resolver.hpp,
// реализуй в task_resolver.cpp и добавь m.def(...) ниже.
NB_MODULE(task_resolver, m) {
    m.doc() = "C++ task resolver for kalinka";

    nb::class_<TaskInfo>(m, "TaskInfo")
        .def(nb::init<>())
        .def("__init__", [](TaskInfo* self, int id, int priority, int days_left) {
            new (self) TaskInfo{id, priority, days_left};
        }, nb::arg("id"), nb::arg("priority"), nb::arg("days_left"))
        .def_rw("id", &TaskInfo::id)
        .def_rw("priority", &TaskInfo::priority)
        .def_rw("days_left", &TaskInfo::days_left);

    m.def("resolve_order", &resolve_order, nb::arg("tasks"),
          "Return task ids ordered by priority, then by deadline.");
    m.def("version", &version);
}
