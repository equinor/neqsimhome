from revise_foundations_science_phase3 import R
R('ch14','fresh_optimizer_fixture','''ProductionOptimizer = jneqsim.process.util.optimizer.ProductionOptimizer
optimizer = ProductionOptimizer()
result = optimizer.optimizeThroughput(process, feed, 10000.0, 60000.0, "kg/hr", None)
print("Feasible:", result.isFeasible(), "Rate (kg/hr):", result.getOptimalRate())
print(ProductionOptimizer.formatUtilizationTable(result.getUtilizationRecords()))''','''ProductionOptimizer = jneqsim.process.util.optimizer.ProductionOptimizer
# A fresh fixed-ratio case prevents reusing the earlier train's unset capacity data.
feed = Stream("Optimization feed", gas.clone())
feed.setTemperature(30.0, "C")
feed.setPressure(10.0, "bara")
feed.setFlowRate(30000.0, "kg/hr")
compressor = Compressor("Power-limited compressor", feed)
compressor.setOutletPressure(30.0, "bara")
compressor.setPolytropicEfficiency(0.80)
compressor.setUsePolytropicCalc(True)
compressor.updatePowerConstraint(2000.0)  # kW; fixed installed rating
process = ProcessSystem()
process.add(feed)
process.add(compressor)
process.run()
base_power_kW = compressor.getPower("kW")
# With fixed inlet state, pressure ratio and efficiency, power scales with flow.
# The default throughput optimizer's utilization limit is 0.95.
analytic_rate = min(60000.0, 30000.0 * (0.95 * 2000.0) / base_power_kW)
optimizer = ProductionOptimizer()
result = optimizer.optimizeThroughput(process, feed, 10000.0, 60000.0, "kg/hr", None)
assert result.isFeasible()
feed.setFlowRate(result.getOptimalRate(), "kg/hr")
process.run()  # Verify the returned candidate explicitly.
assert 10000.0 <= result.getOptimalRate() <= 60000.0
assert compressor.getPower("kW") <= 0.95 * 2000.0 * (1.0 + 1e-6)
assert abs(result.getOptimalRate() / analytic_rate - 1.0) < 0.01
print("Feasible:", result.isFeasible(), "Rate (kg/hr):", result.getOptimalRate())
print("Independent linear-power boundary (kg/hr):", analytic_rate)
print(ProductionOptimizer.formatUtilizationTable(result.getUtilizationRecords()))''')
R('ch14','optimizer_infeasible_history','The `ProductionOptimizer` in NeqSim automatically identifies which compressor constraint is binding at the maximum production rate:', 'The following accepted case uses a fresh fixed-pressure-ratio compressor and a declared 2 MW rating. Its returned rate is checked against the power limit and an independent linear-power boundary. Reusing the earlier train with unset capacity data returned an infeasible 10,000 kg/hr candidate and is not accepted as an optimum. The default 0.95 utilization ceiling is a numerical scenario input, not a universal equipment operating margin:')
R('ch14','map_generation_scope','creates realistic performance curves from a single design point, using the physics of centrifugal compressor aerodynamics:', 'creates synthetic performance curves around a design point. They illustrate map handling and approximate aerodynamic trends; a single point cannot establish the actual surge, choke or efficiency envelope of a machine:')
