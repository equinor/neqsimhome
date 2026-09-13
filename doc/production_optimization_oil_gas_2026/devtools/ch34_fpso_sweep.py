from pathlib import Path
Path("figures").mkdir(exist_ok=True)
water_cuts = np.linspace(.10, .80, 15)
fpso_sweep = []
for water_cut in water_cuts:
    plant, equipment = build_fpso_model(float(water_cut))
    plant.run()
    fpso_sweep.append(verify_fpso(equipment))
assert len(fpso_sweep) == 15
x = [row["water_cut_pct"] for row in fpso_sweep]
fig, axes = plt.subplots(2, 2, figsize=(10, 7))
for key, label in (("oil_rate_m3hr", "Final oil at 2.5 bara"),
                   ("sep1_water_m3hr", "Water at first separator")):
    axes[0, 0].plot(x, [r[key] for r in fpso_sweep], "o-", label=label)
axes[0, 0].set_ylabel("Separate product volumes at local state (m³/h)")
axes[0, 0].legend(fontsize=8)
for ax, key, label in ((axes[0, 1], "gas_rate_MSm3d", "Export gas (MSm³/day)"),
                       (axes[1, 0], "compression_MW", "Total compressor shaft power (MW)"),
                       (axes[1, 1], "sep1_liquid_util_pct", "First-separator liquid utilization (%)")):
    ax.plot(x, [r[key] for r in fpso_sweep], "o-")
    ax.set_ylabel(label)
axes[1, 1].axhline(100, ls="--", color="#a64b3c", label="Assumed 400 m³/h actual limit")
axes[1, 1].legend(fontsize=8)
for ax in axes.flat:
    ax.set_xlabel("Feed water cut at 15 °C, 1.01325 bara (%)")
    ax.grid(alpha=.2)
fig.suptitle("Verified CPA separation/compression: fixed 200 m³/h reference liquid")
fig.tight_layout()
fig.savefig("figures/ch23_case2_water_cut_sensitivity.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print(json.dumps(fpso_sweep, indent=2))
