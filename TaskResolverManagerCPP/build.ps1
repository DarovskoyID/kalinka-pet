# Сборка C++ модуля task_resolver -> task_resolver.*.pyd в корне проекта.
# Требуется: Visual Studio (C++), cmake (из PATH или из CLion), pip install nanobind в .venv
$root = Resolve-Path "$PSScriptRoot\.."
$py = "$root\.venv\Scripts\python.exe"

$cmake = (Get-Command cmake -ErrorAction SilentlyContinue).Source
if (-not $cmake) {
    $cmake = Get-ChildItem "C:\Program Files\JetBrains\CLion*\bin\cmake\win\x64\bin\cmake.exe" -ErrorAction SilentlyContinue |
        Select-Object -Last 1 -ExpandProperty FullName
}
if (-not $cmake) { throw "cmake не найден: установи CMake или CLion" }

& $cmake -S $PSScriptRoot -B "$PSScriptRoot\build" -DPython_EXECUTABLE="$py"
& $cmake --build "$PSScriptRoot\build" --config Release
