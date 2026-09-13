// First run the process to establish the operating point
process.run();

// autoSize creates constraints based on current operating point + design margin
comp.autoSize(1.2);  // 20% design margin above current operating point
