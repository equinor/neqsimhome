"""Correct stochastic interpretation and replace the resource-inconsistent NPV case."""
import ast,json,re
from pathlib import Path
BOOK=Path(__file__).resolve().parents[1]
p=next((BOOK/'chapters').glob('ch27_*/chapter.md'));original=p.read_text(encoding='utf-8-sig')
b=BOOK/'.build/backups/scientific_revision'/p.parent.name/'uncertainty_input.md';b.parent.mkdir(parents=True,exist_ok=True)
if not b.exists():b.write_text(original,encoding='utf-8')
t=b.read_text(encoding='utf-8');changes=[]
def r(old,new):
 global t
 if old not in t:raise AssertionError(old[:100])
 t=t.replace(old,new);changes.append({'before':old,'after':new})
r('Chapters 25 through 27','Chapters 22 through 26')
r('Sections 28.','Sections 27.')
r('and 28.','and 27.')
r('through 28.','through 27.')
r('The practical motivation is compelling. Consider a gas field development decision where the key uncertainties are gas-initially-in-place (GIP), gas price, and facility CAPEX. A deterministic analysis using "best estimate" values might yield a healthy NPV of 3,000 MNOK. But a Monte Carlo analysis sampling all three uncertainties reveals that the NPV distribution has a 15% probability of being negative — a risk that never appears in the deterministic calculation. Moreover, the tornado analysis shows that gas price has twice the impact of GIP on NPV, redirecting the risk mitigation strategy from appraisal wells to hedging contracts.', 'A deterministic base case cannot establish the probability of negative NPV or the value of more information. Those claims require declared joint input distributions, physically consistent production profiles, cash-flow timing and explicit sampling error. Section 27.11 supplies a reproducible reservoir-tank example instead of assuming a risk percentage or sensitivity ranking.')
r('Typical Range | Impact on Production','Illustrative range requiring calibration | Impact on Production')
r('Compressor efficiency decline | 2–5% per year','Compressor efficiency decline | Service-specific; no annual rate established here')
r('the decision $x$ must be feasible regardless of which future materializes.', 'the same decision $x$ must satisfy every included scenario. This is not a guarantee for unrepresented futures or the entire continuous uncertainty set.')
r('In oil and gas, where investments are large and irreversible, risk neutrality is rarely appropriate.', 'Risk attitude is a declared decision preference; project size and irreversibility alone do not determine it.')
r('where $\\alpha$ is the confidence level (typically 0.05 or 0.10).', 'Here $\\alpha$ is a lower-tail probability, such as 0.05, rather than the usual upper-tail loss confidence of 0.95. The conditional-mean notation applies to continuous distributions; for atoms use the threshold formulation in Chapter 22.')
r('A `ScenarioRequest` encapsulates a named scenario with its own process system, feed stream, optimization configuration, and probability weight.', 'A `ScenarioRequest` encapsulates a named scenario with its own process system, feed stream and optimization configuration. Keep probability weights explicitly in the application-level decision analysis.')
r('where $f_s^*$ is the optimal objective value for scenario $s$. The variance of performance provides a measure of robustness:', 'Here each $f_s^*$ uses a separately optimized decision. Its weighted mean is a wait-and-see (perfect-information/adaptive) value, not the achievable expected value of one here-and-now decision. To evaluate one decision $x$, use $f(x,\\xi_s)$ in every term. The corresponding variance summarizes spread:')
r('The multi-scenario VFP tables ensure that the coupling is valid across the full range of uncertain parameters, not just the base case.', 'Qualified tables support interpolation only inside their tested axes and physical validity range. Additional scenarios alone do not validate extrapolation, well hydraulics or convergence of the coupling.')
r('This guarantees that the marginal distribution of each parameter is uniformly sampled, even for moderate $N$.', 'This stratifies each marginal probability scale, not necessarily the physical value scale. Apply inverse marginal CDFs and a justified dependence model; random pairing represents independent inputs.')
r('The improvement in efficiency is significant. For a 5-parameter problem, LHS with $N = 200$ samples typically provides comparable accuracy to simple random sampling with $N = 1000$ — a fivefold reduction in computational cost.', 'The benefit of LHS depends on the response and dependence structure. There is no general fivefold sample reduction, particularly for rare events, discontinuities or tail quantiles. Compare independent replicated designs at the required precision \\cite{jcgm101mc}.')
a=t.index('A critical question in Monte Carlo analysis is:');z=t.index('\n---',a)
t=t[:a]+'''For independent identically distributed samples with finite variance, the mean's standard error is $s/\\sqrt{N}$. Quantile precision additionally depends on the density near the quantile: asymptotically $\\operatorname{SE}(\\hat q_p)\\approx\\sqrt{p(1-p)/N}/f_Y(q_p)$. No universal $N=200$ rule guarantees a percentage error. LHS requires an appropriate variance estimator or independent randomized replications; ordinary IID formulas do not automatically apply.

Use independent repeated seeds and confidence intervals for each decision-relevant output, including failure probability. A stable running median does not demonstrate stable tails. State the percentile convention: this chapter uses **CDF percentiles**, so P10 is the lower 10th percentile and P90 the upper 90th percentile. Petroleum reserves reporting often uses exceedance probabilities with reversed labels; never mix the conventions.
''' +t[z:]
changes.append({'topic':'Replaced unsupported MC sample-size guarantee with mean/quantile uncertainty and percentile conventions'})
r('The total swing $|\\Delta f_j^{+}| + |\\Delta f_j^{-}|$ measures the overall sensitivity to parameter $j$.', 'Use the range of the low/base/high responses to describe an OAT swing. Summing absolute endpoint deviations overstates the range when both endpoints lie on the same side of the base. OAT does not quantify interactions or global variance contributions.')
r('If gas price has the largest impact on NPV, hedging contracts are more valuable than appraisal wells.', 'A large price sensitivity does not prove that hedging is more valuable than appraisal; compare feasible mitigation costs, residual risk and the value of information.')
r('where $k = 1.5$–$2.0$ for typical industrial applications, corresponding to approximately 90–95% confidence that the constraint will not be violated.', 'A mean-plus-$k\\sigma$ rule is a distributional chance-constraint approximation, not robust feasibility over a bounded set. Under a known Gaussian model, one-sided coverage is $\\Phi(k)$: about 93.3% at 1.5 and 97.7% at 2.0. Non-Gaussian tails, uncertain moments and multiple constraints require separate treatment.')
r('The NeqSim constraint framework (Chapter 25) supports this through the `SOFT` constraint type, which applies a penalty rather than a hard cutoff. By increasing the penalty weight, the optimizer is incentivized to maintain a margin from the constraint boundary.', 'Enforce the chosen limits explicitly in every required NeqSim scenario. A `SOFT` penalty can influence the objective but does not establish robust feasibility or a minimum safety margin.')
r('the direct implementation of the robust formulation above.', 'a finite-scenario selection rule whose returned decision still needs independent replay, coverage checks and an explicit percentile convention. A sampled feasible fraction is not a confidence bound.')
r('Because each case is independent, the speed-up is near-linear in the number of cores.', 'Concurrency performance depends on JVM memory, model cost, shared resources and worker count; benchmark a sequential reference before claiming speed-up.')
r('The optimal design is typically larger than the deterministic optimum for the base case, because the upside from capturing high-demand production outweighs the downside of higher CAPEX.', 'Whether the stochastic design is larger or smaller than a base-case design depends on the scenario distribution, costs and recourse options; no universal direction follows.')
r('The value of the second-stage decisions — the ability to adapt operations to observed conditions — is called the **value of recourse**. It can be quantified as the difference between the stochastic program solution and the "wait-and-see" solution (where the uncertainty is known before deciding):', 'Recourse is the ability to adapt later decisions using information actually available then. Its value compares otherwise identical models with and without that flexibility. The following different quantity is the **expected value of perfect information**, comparing fully anticipative wait-and-see decisions with the nonanticipative stochastic solution:')
r('The option value is typically 10–30% of the static NPV for oil and gas developments, depending on the degree of uncertainty and the flexibility available.', 'Calculate flexibility value for the specified information timing, admissible decisions and costs. No generic percentage of static NPV is established here.')
a=t.index('### 27.11.1');z=t.index('<!-- September 2026',a)
source=(BOOK/'devtools/scientific_uncertainty_probe.py').read_text(encoding='utf-8')
tree=ast.parse(source);node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='depletion_profile')
function=ast.get_source_segment(source,node)
replacement='''### 27.11.1 Physical and Economic Basis

The illustrative dry-gas resource is triangular with lower endpoint 65, mode 100 and upper endpoint 145 GSm³. These are distribution parameters, not P10/P50/P90. The two facility capacities are 6 and 10 GSm³/year with assumed time-zero CAPEX of 12,000 and 18,000 MNOK. A 1 GSm³ resource cannot sustain the previous multi-GSm³/year plateau; production must close against the actual sampled inventory.

Each sample runs a NeqSim `SimpleReservoir` at constant 100°C, initialized at 250 bara with pure methane and SRK. A declared rate-control rule tapers withdrawal towards 50 bara; NeqSim solves the fixed-volume pressure at each annual step. This is an isothermal tank and assumed operating policy, not a calibrated reservoir-well-facility forecast. It has no aquifer, tubing, compressor or resource replacement. The imposed temperature entails an external heat supply; an adiabatic energy balance is not claimed.

Gas price is triangular (0.8, 1.5, 2.5) NOK/Sm³ and CAPEX multiplier is triangular (0.85, 1.0, 1.4). All three inputs are assumed independent. The cash-flow calculation is **pre-tax**, with CAPEX at time zero, annual OPEX at 2% of installed CAPEX and year-end sales over 25 years, discounted at 8%. It is not a Norwegian fiscal model. Each plan uses the same 200 stratified samples; this reduces comparison noise but does not establish tail confidence.

### 27.11.2 Monte Carlo with NeqSim Depletion

```python
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import qmc, triang
import jpype
jneqsim = jpype.JPackage("neqsim")
Path("figures").mkdir(parents=True,exist_ok=True)

''' + function + '''

n_mc=200
u=qmc.LatinHypercube(d=3,seed=42).random(n_mc)
def triangular_quantiles(values,low,mode,high):
    return triang.ppf(values,(mode-low)/(high-low),loc=low,scale=high-low)
gip_samples=triangular_quantiles(u[:,0],65.,100.,145.)
price_samples=triangular_quantiles(u[:,1],.8,1.5,2.5)
capex_samples=triangular_quantiles(u[:,2],.85,1.,1.4)
plans={"Conservative":(6.,12000.),"Aggressive":(10.,18000.)}
outputs={}
discount=(1.08)**(-np.arange(1,26))
for name,(capacity,base_capex) in plans.items():
    records=[]
    for i in range(n_mc):
        profile=depletion_profile(float(gip_samples[i]),capacity)
        production=np.array(profile["production_GSm3"])
        installed=base_capex*capex_samples[i]
        cash=production*price_samples[i]*1000.0-.02*installed
        npv=float(-installed+cash@discount)
        assert np.isfinite(npv)
        records.append({"npv_MNOK":npv,**profile})
    outputs[name]=records
summary={}
for name,records in outputs.items():
    npvs=np.array([v["npv_MNOK"] for v in records])
    summary[name]={"N":len(records),"npv_cdf_P10_P50_P90_MNOK":
                   np.percentile(npvs,[10,50,90]).tolist(),
                   "probability_negative_sample":float(np.mean(npvs<0)),
                   "mean_npv_MNOK":float(npvs.mean()),
                   "recovery_cdf_P10_P50_P90":np.percentile(
                     [v["recovery_fraction"] for v in records],[10,50,90]).tolist(),
                   "total_gas_cdf_P10_P50_P90_GSm3":np.percentile(
                     [sum(v["production_GSm3"]) for v in records],[10,50,90]).tolist(),
                   "max_relative_mass_error":max(
                     v["max_relative_mass_error"] for v in records)}
summary["gip_cdf_P10_P50_P90_GSm3"]=np.percentile(gip_samples,[10,50,90]).tolist()
Path("ch27_depletion_monte_carlo.json").write_text(
    json.dumps({"summary":summary,"samples":outputs},indent=2))
print(json.dumps(summary,indent=2))
fig,axes=plt.subplots(1,2,figsize=(11,4))
for name,records in outputs.items():
    values=np.array([v["npv_MNOK"] for v in records])
    axes[0].hist(values,bins=25,alpha=.5,label=name)
    axes[1].plot(np.sort(values),np.arange(1,n_mc+1)/n_mc,label=name)
for ax in axes:
    ax.set_xlabel("Pre-tax NPV (MNOK)");ax.grid(alpha=.3);ax.legend()
axes[0].set_ylabel("Sample count");axes[1].set_ylabel("Empirical CDF")
fig.tight_layout()
fig.savefig("figures/ch27_verified_resource_npv.png",dpi=170,bbox_inches="tight")
plt.close(fig)
```

![Pre-tax NPV from 200 common LHS scenarios per plan, using a NeqSim isothermal gas tank and the declared annual withdrawal rule](figures/ch27_verified_resource_npv.png)

The figure compares the distribution under the stated resource and economic assumptions. Every annual withdrawal closes against the simulated tank inventory to relative mass error below $10^{-9}$; temperature and positive pressure are checked. The saved result reports resource, recovery and cumulative production percentiles alongside NPV, so economic results cannot be detached from their resource basis. A plan's larger production capacity accelerates withdrawal but also increases assumed CAPEX and OPEX. The balance of those effects, not a presumed risk ranking, determines the sampled NPV.

### 27.11.3 Decision and Remaining Qualification

Use the printed distributions to compare these two **fixed policies**, not to claim a robust optimum or a real option. Check annual-step sensitivity, probability distributions/dependence, operating costs and abandonment rules before an investment interpretation. A conditional expansion requires a separate nonanticipative decision tree with the expansion cost and information time. Neither the old arbitrary 10–20% option value nor a presumed hedging/appraisal ranking is supported by this example.

<!-- scientific-evidence test=devtools/scientific_uncertainty_probe.py baseline=verification/scientific_revision/ch27_depletion_probe.json -->

---

'''
t=t[:a]+replacement+t[z:]
changes.append({'topic':'Replaced resource-inconsistent, non-LHS, flat-tax NPV with 400 actual NeqSim depletion profiles and independent inventory checks'})
r('With $N = 200$–$500$ NeqSim evaluations, robust estimates of quantiles and risk metrics are achievable.', 'Sample size must be justified from precision of the relevant tails and failure probabilities; stratification alone supplies no universal guarantee.')
r('robust optimization (maximize the P10 gas production)', 'lower-tail reward optimization (maximize the CDF P10 gas production) with separately enforced scenario feasibility')
r('The capacity cost is 500 $/kg/hr of capacity. Lost production due to insufficient capacity costs 0.10 $/kg for each kg/hr of excess production beyond capacity.', 'The time-zero capacity cost is 500 USD per (kg/hr) installed. Assume 8,000 equivalent discounted operating hours; each unserved kg has a 0.10 USD opportunity cost. Apply that time factor to convert the loss rate into comparable present value.')
markers=lambda x:re.findall(r'<!-- reviewed-notebook-results:start -->.*?<!-- reviewed-notebook-results:end -->',x,re.S)
assert markers(t)==markers(original)
p.write_text(t,encoding='utf-8')
(BOOK/'verification/scientific_revision/uncertainty_corrections.json').write_text(json.dumps(changes,indent=2,ensure_ascii=False),encoding='utf-8')
print(f'Applied {len(changes)} uncertainty corrections')
