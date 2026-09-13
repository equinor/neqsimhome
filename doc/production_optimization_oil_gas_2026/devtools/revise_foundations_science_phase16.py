from revise_foundations_science_phase3 import R
R('ch18','steam_backpressure_case','steam_turbine.setOutletPressure(0.08, "bara")','steam_turbine.setOutletPressure(10.0, "bara")  # verified backpressure case, not a condensing turbine')
R('ch18','steam_initialize','steam.run()\nsteam_turbine =','steam.run()\nsteam.getFluid().initProperties()\nsteam_turbine =')
R('ch18','HRSG_evidence_scope','## 18.5 Fuel Gas Systems','## 18.5 Fuel Gas Systems') if False else None
# Insert beside the actual recovered-duty example, not beside unrelated figures.
R('ch18','steam_rejected_boundary','```python\n# Heat-recovery screening from an explicitly specified exhaust composition.', '''The following calculation accepts a **40-to-10 bara backpressure steam expansion**. With the stated synthetic exhaust it recovers 27.758 MW, supplies 9.362 kg/s steam on a consistent SRK water basis, and produces 2.773 MW shaft work. The initially attempted 0.08 bara condensing case returned 8.788 MW although the independently initialized outlet enthalpy implied only 5.901 MW; that result is rejected. The successful higher-backpressure case closes the steam duty and turbine first law. It does not validate SRK water properties against steam tables, establish a combustor exhaust balance, or model the downstream steam consumer/condenser.

```python
# Heat-recovery screening from an explicitly specified exhaust composition.''')
