# Scientific review: optimization chapters

All16 assigned chapters were read and scientifically revised. Every numerical case is explicitly inventoried and linked to its current solution-verification evidence. Software/configuration/reporting and external patterns have separate scopes. **Solution verification does not establish universal experimental or field-model validity.** Rejected native candidates are retained as diagnostics.

Numerical coverage complete: **True**. Unresolved solution cases: `0`.

Pinned NeqSim source: `6cc8026202a5d3f9383c9abd1d97d448993813f9`. Current executable-hash gate: **True**.

Execution counts: `{"passed": 313, "integration_pattern": 30}`; `343` literal Python/Java fences in16 chapters.

## Chapter review coverage

| Chapter | Scientific focus | Executed | Patterns | Explicitly mapped checks |
|---|---|---:|---:|---:|
| 19 | Export thermodynamics, ISO6976 references, measurement uncertainty and fiscal scope | 8 | 0 | 8 |
| 20 | Equipment capacity metrics, physical dimensions, utilization and coupled bottlenecks | 11 | 0 | 10 |
| 21 | Debottlenecking API, enabled constraints, automatic sizing and economic comparisons | 39 | 0 | 27 |
| 22 | Optimization theory, KKT/globality, separator staging, gas lift and compression | 9 | 0 | 9 |
| 23 | Current NeqSim process architecture, automation, optimizer and strict evidence contracts | 39 | 0 | 14 |
| 24 | Production optimization implementation, capacity constraints and acceptance | 73 | 9 | 30 |
| 25 | Capacity surveillance, measurements, uncertainty and operating recommendations | 16 | 1 | 11 |
| 26 | Well/network allocation, hydraulic boundaries and a verified reduced allocation problem | 14 | 3 | 12 |
| 27 | Scenarios, Monte Carlo, tornado sensitivity, robustness and resource economics | 8 | 0 | 6 |
| 28 | VFP construction, production-flow orientation and export contracts | 19 | 5 | 13 |
| 29 | Dynamic inventories, control, depressurization and protective-system scope | 13 | 0 | 9 |
| 30 | Digital-twin data contracts, model calibration, MPC, hybrid models and automation | 22 | 7 | 11 |
| 31 | Flash, recycle, adjuster and numerical solver mathematics | 5 | 2 | 5 |
| 32 | Advanced optimization, local calibration contracts, surrogate uncertainty and batch execution | 23 | 2 | 20 |
| 34 | Integrated production examples with explicit process boundaries and generated sensitivities | 8 | 1 | 8 |
| 35 | Emissions, CO2, hydrogen, energy integration and prospective methods | 6 | 0 | 6 |

## Chapter19: Export thermodynamics, ISO6976 references, measurement uncertainty and fiscal scope

Source SHA256: `9d530c1754dc565f73ff57a8537e6e3329fd5ab42d256d13d9c004f3366e573b`. Full text reviewed: yes.

- Corrected SI isothermal Darcy pressure-square equation and compression efficiency convention.
- Separated ISO6976 composition calculations from the assumed sales-quality envelope and water/hydrocarbon dew points.
- Corrected prover pulse factor, covariance-aware GUM propagation and RSS rounding; abbreviated orifice correlation is not fiscal ISO5167 implementation.
- Removed unsupported contractual/standards compliance claims and clarified flow-reference conditions.
- Every literal property case now has specific checks: same-basis ISO6976 identities, eight CPA water-dewpoint onset brackets, phase-envelope terminal-slot handling and pipeline conservation/domain.

**Acceptance and limitations.** Solution checks establish the declared property identities, phase boundaries and pipeline budgets. Contract acceptance, installed metering calibration and fiscal uncertainty still require independent site evidence.

| Fence | Language | Execution | Scientific classification | Exact code SHA256 |
|---:|---|---|---|---|
| 1 | python | passed | solution_verified_numerical | `19cbf01e1b6472bc4213e45761b4fb6728e76727ebd47fffcf49383d7234290c` |
| 2 | python | passed | solution_verified_numerical | `1f242295a4a0696d7b876799301609999185806a3aa137079fc4976815bf081c` |
| 3 | python | passed | solution_verified_numerical | `fa9acb4436b78a3be4565bd4261c3f132cbf0d5edb7af15c30e25c136a85491a` |
| 4 | python | passed | solution_verified_numerical | `3040e44026ac91c92590723409cd22051670366a0b9a7e18ed1f058d29448f09` |
| 5 | python | passed | solution_verified_numerical | `bd9fe9c52d1f27721bab77786601094a472fde6c38007c1efc3447dedabeac2c` |
| 6 | python | passed | solution_verified_numerical | `4ba7ed4d4d7b10829e3465d356b479818e6ca5eb432925d35c8c3b2fc19b1c9f` |
| 7 | python | passed | solution_verified_numerical | `beea294d2a9cf9d14677dce81b5bca1de286e2d1359f69f0025b4b24e7567f32` |
| 8 | python | passed | solution_verified_numerical | `cc7c26f56b45396f6f3a4f8df20cb568df8246f7457ecca9affb15b961941e91` |

## Chapter20: Equipment capacity metrics, physical dimensions, utilization and coupled bottlenecks

Source SHA256: `9f58884bc1eea3c266a9fd9de59b502aa5d68512b1cefeca0f9460234d84fe0c`. Full text reviewed: yes.

- Corrected margin factors, surge denominator, head units, heat-transfer terminal approaches, flow coefficients and pipeline length units.
- Replaced arbitrary UA times 50K utilization with two solved clean/fouled heat-exchanger cases and explicit two-stream enthalpy closure.
- Added missing-equipment coverage rejection, corrected source-backed pipeline checks and removed unsupported universal debottlenecking percentages.
- Separated installed evidence, generated chart assumptions and nonlinear whole-process feasibility.
- Corrected polytropic mode and fixed-reference-volume water cut; replaced invalid API relief expression with a dimensionally checked ideal-gas nozzle illustration; verified all10 calculations and one coverage contract.

**Acceptance and limitations.** Computed capacity/dimension/energy examples and the coverage contract have explicit solution checks. No supplied vendor map, separator carryover test or certified relief calculation establishes installed capacity.

| Fence | Language | Execution | Scientific classification | Exact code SHA256 |
|---:|---|---|---|---|
| 1 | python | passed | solution_verified_numerical | `306f2c527582be372316a54625981a5270b8477cbd15d33937db7d88aac3913a` |
| 2 | python | passed | solution_verified_numerical | `a2f4a6c2698d79d3a951a1d7a5c84bd973da7a7d577e7e3bd58f964ecc20578a` |
| 3 | python | passed | solution_verified_numerical | `0340df1a97b96502908802e214b045268a1455500a6b52b62c413d97d10f1860` |
| 4 | python | passed | solution_verified_numerical | `05f8a919af0809b65781dc270dd74f40d95a172012a7ed03a98c6dabd0396960` |
| 5 | python | passed | solution_verified_numerical | `2cdbf4cfa4321778de10387a667b50cd30813c76d807441eae6a19093db82741` |
| 6 | python | passed | solution_verified_numerical | `993c2c707bfc1a5d8651c0bddd83dcfbdc9342f415b69eaa8de194745fa81389` |
| 7 | python | passed | solution_verified_numerical | `1b411eb91dac1bebda9f402006c99daa53a787682bf0205ddd8cecdaf88fa2a5` |
| 8 | python | passed | solution_verified_numerical | `062db760578e508e14f90a70002045dff6503400980092a01c71cde4b9a56929` |
| 9 | python | passed | solution_verified_numerical | `fe1df22c418f33e24a8f958bb306c5a5eb7ef39c3583efd1195f1fffdf6881a1` |
| 10 | python | passed | solution_verified_numerical | `b6ce1463bd4b00cd62fa5ca6f09d6b4ccdfe5825d57fdabf2a527e97f29bbefd` |
| 11 | python | passed | software_API_config/reporting | `634a2c2b48b9dc9b7af3cd57d6825c979070158199635762b2cd5c4de40b9a71` |

- Fence3: Exact literal execution with supplementary numerical/physical/software solution checks; not field calibration.

- Fence5: Exact literal execution with supplementary numerical/physical/software solution checks; not field calibration.

- Fence11: Reviewed definition/configuration/serialization or reporting of previously computed values in the documented sequential fixture; no independent installed-equipment claim.

## Chapter21: Debottlenecking API, enabled constraints, automatic sizing and economic comparisons

Source SHA256: `febbe37baea23460d8ac353b92442c53daea8851969dad8f95fe22fc6acb5fea`. Full text reviewed: yes.

- Corrected multiplicative automatic-size factors to 1.x and distinguished sizing heuristics from hydraulic re-rating.
- Corrected all31 Java fixtures/signatures; preset enablement and disabled checks do not increase physical feed capacity.
- Removed fabricated optimization statistics, clarified hypothetical economics, corrected profitability-index and currency/payback relationships.
- Additional root/specialist solution gates cover all8 Python and31 Java fences, including percentage units, fresh final-state replay,51-point grids, explicit disabled-chart sentinels and5 assumed economics cases.

**Acceptance and limitations.** All literal numerical/API cases have specific solution or software checks. Preset names, masking and auto-sizing remain assumptions; they do not qualify installed equipment or an investment.

| Fence | Language | Execution | Scientific classification | Exact code SHA256 |
|---:|---|---|---|---|
| 1 | java | passed | solution_verified_numerical | `881a78f61368ed8ec7a68d7129d8bd2c273ccdd5dc20292962bbb086db7ca3e1` |
| 2 | java | passed | software_API_config/reporting | `6d1c58ccee8263d624752ed824f0f359ef21627f29f85b05a452f71fe744d3ff` |
| 3 | java | passed | software_API_config/reporting | `717f70477dc9c14b03060a95ddd78a1421e61805c427e9cea5a2cee941e9ffed` |
| 4 | java | passed | software_API_config/reporting | `5f39dd9a6c598171be2e7c14256cfab051ac3d572f4954dfb724ece8027446e2` |
| 5 | java | passed | software_API_config/reporting | `de56198602ce4ac6d52f0ab1194622ec81e1c4965f59ac92d4d8f2124ed84d8a` |
| 6 | java | passed | solution_verified_numerical | `e23f8608a354760b3eff8f82992e60cf25608149edb1b4573f235a23c70de271` |
| 7 | java | passed | solution_verified_numerical | `a69432e5b9b762be8fa0f0dbcd7f7815117c700e05bfb2219755eab099e174cf` |
| 8 | java | passed | solution_verified_numerical | `95d7bcc72235d48160f385b952ddfbf44ba5b7d7a09276e98c45e909c5d5766c` |
| 9 | java | passed | software_API_config/reporting | `04d6081cf7be6072fc754edc7f2bb318cbea6145cf0c535f039f30b3add56d95` |
| 10 | java | passed | solution_verified_numerical | `313000af1c2d3018d9391583ea4258d1e4bedc70ecd67d64636d60d82ee01701` |
| 11 | java | passed | software_API_config/reporting | `2748ae05c1b26c63fed23a2d8773177bc5fff86ed83e8078405a388e0859af4a` |
| 12 | java | passed | software_API_config/reporting | `60608c7cc905bbb6f5ae7ba845cce72aed73d95bd01ea6e1f9d7fef9c06ce968` |
| 13 | java | passed | solution_verified_numerical | `a1fbae51efe81b789306c015d2e83e5af46efc02cf2ebc9e04c9fa943b29bcdb` |
| 14 | java | passed | solution_verified_numerical | `2999e5203ae859c8a391ab1189616f6f9d53f46a5b71b8e21c5e850f157ffe87` |
| 15 | java | passed | solution_verified_numerical | `ef95ca088044bacd8b16e04bb89dddc098f4d6941513683cf074ddc8c78307da` |
| 16 | java | passed | solution_verified_numerical | `2d389445a6f0704401f5a9bd723fb438ecacc78261f9f0612c5a094d25c936da` |
| 17 | java | passed | solution_verified_numerical | `de5128403303c5914a18fcb5f91b01b01d3dc6e0be20cdfd78bc7435ea8e5dca` |
| 18 | java | passed | solution_verified_numerical | `f28341f8a73aa3a1e7694af5f91136e3054d842bc133a7e5b193007eeb3dca82` |
| 19 | java | passed | solution_verified_numerical | `3709938577876e3f788118f4f0cfe05f26bc2992dce9410f2029af2828f0a618` |
| 20 | java | passed | solution_verified_numerical | `68f654119bfc464885c21979ebe3133013ce94aecd5763f5d7f9f054622059e7` |
| 21 | java | passed | solution_verified_numerical | `09dc5d16003c231c10f8ceff90eb832945759b86c8f233f0e14c7592193a0a33` |
| 22 | java | passed | software_API_config/reporting | `a4734ad28490fed89b174f5f0d5e609abca984255c3619389c87eacd3072f4e4` |
| 23 | java | passed | solution_verified_numerical | `8c83aef8c3ed37ec6a9bc7cf37464e20c3195b354bd4d91b972d7df3f9b35f97` |
| 24 | java | passed | software_API_config/reporting | `14b85a3f271943209d6cdcb7fceb7d5fcef7e4e587120bd20b1832681777b88f` |
| 25 | python | passed | solution_verified_numerical | `7f4b8121236f70754aa5d433d85e955c18690762a9754cfc7f78a358f569e882` |
| 26 | java | passed | solution_verified_numerical | `eb0595fcad125ff9b9ad0826a8855b91e654318db571166ed465ed4b980399d0` |
| 27 | java | passed | solution_verified_numerical | `26072bfbe61b603d40f2229dd536caf763f4efa592692430ffac41b40692f4a4` |
| 28 | python | passed | solution_verified_numerical | `b29d8fe58f578904d02ab90565cc6d5b9ece927e8775c7375cca3a8a81082f0e` |
| 29 | python | passed | solution_verified_numerical | `2ab0885869f697d1a2019a9fbba77b86bf2ef45132e2d601bbe21669aa5620f3` |
| 30 | python | passed | solution_verified_numerical | `fc0a1f0e4c2c7a7b077e0f182b0dba75a3e19b4e5d3b5f43e9308ed03cb228da` |
| 31 | python | passed | solution_verified_numerical | `5d6e0f9d59642353490a931f0ad2164f581c10f7024fc36ab31c6fe58b539297` |
| 32 | python | passed | solution_verified_numerical | `6596a6b3279088deb8547d209dc18805b759322e8c65b7d65c8f066ad5bdd1de` |
| 33 | java | passed | software_API_config/reporting | `5151e9594e345b8e06f41eec5689197f63a68d33ad63676639d9688190c8c87f` |
| 34 | java | passed | software_API_config/reporting | `3612253f7deb4e688aedfa9eafbaf6e8cb340300880fc7127c50e0f6be024fbf` |
| 35 | java | passed | software_API_config/reporting | `d31b8862062535d938ff89f9fcbc3419a735b5a8c2fc07d85d9cb5f1e80f593b` |
| 36 | python | passed | solution_verified_numerical | `34aad94fcfff09704ab451a979fba48ff5b6aa04cc237e98165610c03320b7c0` |
| 37 | java | passed | solution_verified_numerical | `76f9f1b7e95ab1426954a0796d953a0efec14a823122a076a0e665967e3b379a` |
| 38 | java | passed | solution_verified_numerical | `dab5453a37661f2efb9d64735bda301c377ef25085bffa04cf74aab965853962` |
| 39 | python | passed | solution_verified_numerical | `fa7f8d298acb89a2aab7af7e6ae0c13314c2f741dc1d2f9702f8e95b057f7bd0` |

## Chapter22: Optimization theory, KKT/globality, separator staging, gas lift and compression

Source SHA256: `b3a83dbd307f36c4b2e5f28ec46f012d6f28c80cfbb16ccb5c8f25e26073b798`. Full text reviewed: yes.

- Corrected BFGS minimization sign, convexity conditions, compressor staging assumptions and objective-unit consistency.
- Replaced invented gas-lift API with real NeqSim curves and an allocation checked by budget, marginals, direct objective replay and a 1000Sm3/day grid.
- Added separator material/enthalpy and compressor shaft-energy checks; corrected steady-state ratio and data-reconciliation interpretation.
- Removed unsupported performance claims and corrected the Nwachukwu primary reference.
- Replaced incorrectly oriented nodal calculation with forward upward hydraulics and a checked intersection; replayed intermediate compression and Pareto dominance at every sampled point.

**Acceptance and limitations.** Numerical intersection, balances, optimum logic and dominance are checked in the stated examples. Declared gas-lift curves and model compositions are not calibrated field performance.

| Fence | Language | Execution | Scientific classification | Exact code SHA256 |
|---:|---|---|---|---|
| 1 | python | passed | solution_verified_numerical | `4a2820abc60d28ab9a4b9c392e3ef385161216a256471d4f7d4a285fca31c6bc` |
| 2 | python | passed | solution_verified_numerical | `499708ddc34753d5fd27842458fa12aa3aba2b5c1e7de83f1ddf390740fcef8d` |
| 3 | python | passed | solution_verified_numerical | `65bdc5b5dd1920b060aa17bb058fcf168870999f9d99af16bec48953598da307` |
| 4 | python | passed | solution_verified_numerical | `e3a03b9b7b4816d927c4f35aae28a9e84c50644d163d398eb7cedc77c8d5d202` |
| 5 | python | passed | solution_verified_numerical | `a9682d5c41d9291a2780ef564371b237bad60bda469aeef6e0c14d817b872244` |
| 6 | python | passed | solution_verified_numerical | `466d1f09fb109a1778ac663bafcb9c958515bed52e97732b7b9f6f9f1f2330bd` |
| 7 | python | passed | solution_verified_numerical | `63a13f618aad8eaf619f8f3a6f5f9c0fa38ba1d82185960a5bc74511334c3400` |
| 8 | python | passed | solution_verified_numerical | `ca5562d72ab7e078ffd2d07e0335ed31c4b2cae49a9e538f19e741cd9df48540` |
| 9 | python | passed | solution_verified_numerical | `ae23299ecf521a555bbf5e2c5d8a8b21ca1583cc082253775c156ad36921906d` |

- Fence2: Exact literal execution with supplementary numerical/physical/software solution checks; not field calibration.

- Fence3: Exact literal execution with supplementary numerical/physical/software solution checks; not field calibration.

- Fence4: Exact literal execution with supplementary numerical/physical/software solution checks; not field calibration.

- Fence5: Exact literal execution with supplementary numerical/physical/software solution checks; not field calibration.

## Chapter23: Current NeqSim process architecture, automation, optimizer and strict evidence contracts

Source SHA256: `f8e8a24c23e5b7a7205e6202882bc71701f8c00972f6b7b9760bd7242f7e507a`. Full text reviewed: yes.

- Updated ProcessAutomation.evaluate, ProductionOptimizer final-point replay and strict separator/pipeline/shared-resource coverage at the pinned source commit.
- Separated plant-capacity output from well-BHP VFP export, and generated compressor charts from installed maps.
- Corrected head units, source package/API names, feasibility acceptance and local-search claims.
- Capacity-engine native candidates are checked after replay; rejected points are retained alongside independently feasible bounded grids. Corrected minimum-outlet requirement versus actual compressor setter, disabled-chart sentinel labeling and head/power units.

**Acceptance and limitations.** Native source-engine failures are rejected and accompanied by independently accepted sampled candidates. Finite grids certify only sampled states; generated charts and strategy limits are not installed equipment evidence.

| Fence | Language | Execution | Scientific classification | Exact code SHA256 |
|---:|---|---|---|---|
| 1 | python | passed | solution_verified_numerical | `d7134ec08ef030d0be74abd2fb1f10648cae739f3cc47967d290caa19a9f7d04` |
| 2 | python | passed | software_API_config/reporting | `6260cfd051ed76211b476186d71d5413d1f1b1c369b0c1c854e224a23c29c0a4` |
| 3 | python | passed | solution_verified_numerical | `68ef0d556f2bf50952f473d308ce3bbbca45db823f6601ac1df8cfc939566e86` |
| 4 | python | passed | software_API_config/reporting | `49638670bd38ae96dfa24bd7a80227f1e1a66cacf6bcd2875f0908bfc41ba523` |
| 5 | python | passed | software_API_config/reporting | `a3a6c50cfc70df4f5e3b2411984f2352cd5f22056e9eeab7ae78f1337d18bde5` |
| 6 | python | passed | software_API_config/reporting | `6a3551b160c9eaeeb095649bad1cc39d9ed91c3f3a2e4be0d95a2ecfa1759088` |
| 7 | python | passed | software_API_config/reporting | `4194484db1e146552721a7dee688f3f99865391049ff95a7f43e3b04260eef78` |
| 8 | python | passed | software_API_config/reporting | `0d673867b0ace05121e608de65d3d9c12cdf8534b9a03182d150afb38714ea78` |
| 9 | python | passed | software_API_config/reporting | `3c83bbe6d63102733685462b04eacaeccda46d8c215b59f85463227b9b159545` |
| 10 | python | passed | solution_verified_numerical | `5df611018a76dc5a9d7cf86f967292031f3b698a8ff63cb68af1481b8b57ed12` |
| 11 | python | passed | software_API_config/reporting | `66d0aaf2c1d400c2a4eecc3dd392621cd2acd70a63fb98524a781a2b50b452d4` |
| 12 | python | passed | software_API_config/reporting | `673d056a65a5036750d61fc529b0f2152636250c150dfd4cde4d282091e87766` |
| 13 | python | passed | software_API_config/reporting | `eda34b4eaec37a6f517a83be7a70a4acecff4c31daf702814968afae9f31fd72` |
| 14 | python | passed | software_API_config/reporting | `212e65b5441d6c92903a71150de5f0462714e9763c1259f3fc2e5a3f8f5aee9f` |
| 15 | python | passed | solution_verified_numerical | `1fc9d5ee8572e1d5a25e76c8101977a29be3b288c204914d3ad3aa60ba5dfb67` |
| 16 | python | passed | solution_verified_numerical | `8fca4f83007377aa78d2d4817d4555b9f6c50f90eb39b64ff2b9dd884879f309` |
| 17 | python | passed | software_API_config/reporting | `199bc48d1871b6fbc8e168a7e28f51e6e506414e986a17c1a3ce9fd15485db6d` |
| 18 | python | passed | software_API_config/reporting | `6dceec2dcadeb0f1aa5446c4e77569da8e90b225725ddf56b4ec8a300f8d942e` |
| 19 | python | passed | software_API_config/reporting | `95fd169f99f239997d4c5a33d67a6c742cdd2bd305451618fbbf6f46184e9ec6` |
| 20 | python | passed | software_API_config/reporting | `70bab3bdcdccf262f11b1c46f0e4012c8546c19868b3ed02531cea619bdd2bcd` |
| 21 | python | passed | software_API_config/reporting | `71ccb13b16e31508c443182d9117d7dc80af9a207c3b87c3d7774156c5ed3be9` |
| 22 | python | passed | solution_verified_numerical | `20b9ba02624163951aaca929e55ed86df706c12eb143e7e6ef1e73e95a898f85` |
| 23 | python | passed | solution_verified_numerical | `0446eb49bc384821c4c2ceaaa2441047920abdfe227323c746507d282da6a2f8` |
| 24 | python | passed | software_API_config/reporting | `1284bc4fd72daf942d7b85667c2dcd7c86eac60827c95b011b0f5a4bc42bb4ce` |
| 25 | python | passed | solution_verified_numerical | `cd0565a040665391ac91b22410c28f14f0f2766e89d16685f53c20b0211f064a` |
| 26 | python | passed | software_API_config/reporting | `3854726d6e87acdb5e3d616b8b1c0b9351fb51ec83e9a676efe22db96670dcd4` |
| 27 | python | passed | solution_verified_numerical | `cc1f466dee3a96e829e0cb97fa8a2df3e354cf8872941abbed93234a616d3846` |
| 28 | python | passed | solution_verified_numerical | `4e17ee5b0a2cc1dee6c6f0c05c8d8e811140602542910e1c44ad095f49792c20` |
| 29 | python | passed | software_API_config/reporting | `ad437fa84a0c027c7065c45ec406f5d7e1fa42d55ea6e47d3aa80ff09c8e9634` |
| 30 | python | passed | software_API_config/reporting | `2caf4c7acf68548b35b3ddf187855f586d724514b73f160dfc99c40587c5d114` |
| 31 | python | passed | solution_verified_numerical | `d7857825c13e8250fabba582e99eca05a9cd5d801d6f2fe00003965925bf8385` |
| 32 | python | passed | software_API_config/reporting | `5a1577760673cc4ff6b8518185e3e00940fc9b7bdcd9b272628fe016bf043b16` |
| 33 | python | passed | software_API_config/reporting | `d9245b953eec1dce8ec04eb055f8bf085aa4d80a047d0589a2e2cfe110875375` |
| 34 | python | passed | software_API_config/reporting | `7b88b0218354dbe863da148b8a235c2a19fc22c0fc91a4784c7ca9e37d7abb0d` |
| 35 | python | passed | solution_verified_numerical | `09557f7e31c923f1aa2c8b5f4e0aee16594dfcdbb5ab0bd1ea3b3d2ad81c82b2` |
| 36 | python | passed | software_API_config/reporting | `b50912515e39c4654f3abc7ccfa99cad0cb04f3b909a9b585093aead19588a31` |
| 37 | python | passed | solution_verified_numerical | `219e4baec798077a6dc944afdc795e30935c473e7796c1274ae590755c3eb792` |
| 38 | python | passed | software_API_config/reporting | `229a7217773c79aad5fb9b81da71d82365dd10a9c7edbf8c64a72d2b969223b1` |
| 39 | python | passed | solution_verified_numerical | `ddf0680882dde1504788d0d9eaa719ecb791793e92a81407b3adef981ec3bff9` |

## Chapter24: Production optimization implementation, capacity constraints and acceptance

Source SHA256: `55eb15dd92a6fddbd859681644282c7946acc9334f6dfe6efd6019a7ad330d4c`. Full text reviewed: yes.

- Corrected objective signs, penalty scaling, hard/soft feasibility, bounds and final-state replay requirements.
- Corrected equipment geometry, pressure/flow units, gas valve assumptions, NPSH/UA/pipeline scope and automatic-size factors.
- Replaced false steady-state autocorrelation/Celsius CV claims with current ratio/slope behavior and signal-specific criteria.
- Separated interface examples, external integrations, rejected points and hypothetical economic comparisons.
- Supplementary checks cover every executed process solve, Pareto replay and weighted reconciliation; explicit polytropic mode and percent-to-fraction conversion fixed. Added real80km pipeline and axial mesh comparison, independent capacity grid, and32 attempted pressure states with30 accepted/two explicitly rejected trace-phase balance failures. Economics no longer converts masked total-feed gain into oil sales. Final figure review also rejected liquid Sm3/day as stock-tank volume: Java/Python upstream oil objectives now use kg/hr, while28 stock-tank flashes price only actual oil-phase volume at15C/1.01325bara with material/density/heat identities.

**Acceptance and limitations.** Two of32 pressure states fail the strict1ppm material gate and remain explicit rejected candidates; selection uses30 accepted states. Capacity grids are sampled comparisons, not global certificates. Pipeline mesh/domain checks do not independently validate its thermal correlation. External historian/NLopt/plant adapters remain declared patterns.

| Fence | Language | Execution | Scientific classification | Exact code SHA256 |
|---:|---|---|---|---|
| 1 | java | passed | software_API_config/reporting | `a04cef0ed18cb44c8e59d53705d4d0f6e428e79884a69ac9affba4896916d3ca` |
| 2 | java | passed | solution_verified_numerical | `94f542d4395f484f1333b84ac9b9e95934ca264ae50634a4b82f0bd1b8efb601` |
| 3 | java | passed | software_API_config/reporting | `a8df7dc9058422fa50ad63738e934168b13862a7ae9bddf8baa87d9ac2ced179` |
| 4 | java | passed | software_API_config/reporting | `1b78f09bbc681f38b05f9a6b8cd95c64b2a1061ec7e165d465342283551efacb` |
| 5 | python | passed | solution_verified_numerical | `c0d656d0ca7cb62e1bdb0f286d61bde19d833508cf6ba006ee368ed644f4c8e5` |
| 6 | java | passed | software_API_config/reporting | `41f2347543ef732be7dd19d6798214ca983eb971cd796555df266c7df7566947` |
| 7 | java | passed | software_API_config/reporting | `0cc1c1eb4eaf3cb776047db93cb3572a9c37cd9ff83e2d14d5fc101fc7646b17` |
| 8 | java | passed | software_API_config/reporting | `63342f1e3b6535fa51f7a601b8a83e3fbcaf6989a4d2612fb059e84fb4427d81` |
| 9 | java | passed | software_API_config/reporting | `43acf1fd862c964fe7706863b2e2924eb53a7c68b419485e6b6838d32b4f7181` |
| 10 | java | passed | software_API_config/reporting | `961f1563856792443da3fe71c5bf1a57e2c9026bcbdbeb39292627185f8c2279` |
| 11 | java | passed | software_API_config/reporting | `9785a913223c41c8855d6fbd7b657c6cdd271187aaaa5635ebfa56a0a137dc10` |
| 12 | java | passed | solution_verified_numerical | `1cfe50bc9f6869b1dc03ed66b6ef531095d5093c802e833c66d9ba4b6839a238` |
| 13 | python | passed | solution_verified_numerical | `1e9cc5ef5c0c69fdf24ba6ce87be46a846984805b3c40a8b05d273530d93d96c` |
| 14 | java | passed | solution_verified_numerical | `186db9af9ff411afa85da020d316731cfc5003cc51043fb873c2d44f6d315a76` |
| 15 | java | passed | software_API_config/reporting | `9e6a633dd1f010fa6052773b39cafe589fe6e6c2ad8cf6e036856e63a6b734dc` |
| 16 | python | passed | solution_verified_numerical | `0bcc97379b7a3e6f04740f60ad6013ede7ca5c02f9836faf5044906871660c70` |
| 17 | python | passed | solution_verified_numerical | `46dfef0f8244f0c91e19be6d5bb4f6a7252b411eebffe3b7739e93f702a01311` |
| 18 | python | passed | solution_verified_numerical | `aeccd04feccabfcf2f83f15b77a20e2db23040a0c48bdad8c41c8a276a2aa710` |
| 19 | java | passed | software_API_config/reporting | `78ff94f1bd28db999a42a1915b7335a0279bb44f60242d95e0e2e514d122117d` |
| 20 | python | passed | software_API_config/reporting | `2ea4aa8bdbceea6f00d9175a9a56ac5b11acfabc3ea7ddaf23f34067ac847f6d` |
| 21 | java | passed | software_API_config/reporting | `c74180dc49847bd232e5a5c51cab810a7bd6054487e497a1557e53b7d78d85a1` |
| 22 | java | passed | solution_verified_numerical | `6c4a6f9444d28818b1c395700d9195b4791764b37417f02cdec161daa819a7b3` |
| 23 | python | passed | solution_verified_numerical | `6250e9b5c38cdd4e6eb103d8920eada3ac355ee653997b108d3d7352fee34fea` |
| 24 | java | passed | solution_verified_numerical | `62963e43d6199d06d9ee3efbb4fd50dc7a18303850346d97a0c73028d4a539d7` |
| 25 | java | passed | software_API_config/reporting | `2ebe5659ede894ae7716b6ae7ddb689b5443f298d4eff88f22748df23ced6aa0` |
| 26 | java | passed | software_API_config/reporting | `d2e2e66db0ce7d5862e15be2e8da134a0cd7e93eb71abd5f4feeda44d34b2d68` |
| 27 | python | passed | software_API_config/reporting | `3ad507f043f98b7cb74877ce92f2ce67983acc775f8b55d05030871b9ff2fb4a` |
| 28 | python | passed | software_API_config/reporting | `bfa86010cd4ed94e47a92cca9823b43f31001d152c62e07a9b80d89c83e6dfdd` |
| 29 | java | passed | software_API_config/reporting | `766ed115aaf7732e10b754e2bc1a715e8cff08d27d15c748daae6f3838639e2d` |
| 30 | java | passed | software_API_config/reporting | `57534e3cca46f592721e2a5e4895be158caa506ce1ee777c34ad51a36418c10e` |
| 31 | java | passed | software_API_config/reporting | `b32b981fed49172c13bc630e9f0fde33d04d6df294e45bfec3ac69eb0f49ba14` |
| 32 | python | passed | software_API_config/reporting | `0a3183bde47b420e4b258bf3e25de2cd914c85755410474e989a69a2d656b019` |
| 33 | python | passed | solution_verified_numerical | `36129bf1324284be490b26d489c98682cad0fc038fc3c3b3108e87dd662383a1` |
| 34 | python | passed | solution_verified_numerical | `23ab996d4b21eba937735becb25ed7d0d850491a4ea32adf1372e74967230ebc` |
| 35 | python | passed | software_API_config/reporting | `98876f0823f76d16bb307dab21b23706e993178009b4a49318eab312d2853f4e` |
| 36 | java | passed | software_API_config/reporting | `55e4b75156a871e44a19150b0ebe4635cfd74771cec9fd37d0c242de3181601c` |
| 37 | python | passed | software_API_config/reporting | `e8d097604502b3743f7c44de2b7b0e74de33dbbc8f61e78c6ac9efe5af861b71` |
| 38 | java | passed | software_API_config/reporting | `505ecc2a60ca15dedb84ceffc16fef278bec144eaa27f6f8e1fb85a55249ff9f` |
| 39 | python | passed | software_API_config/reporting | `f722ce24162af4decb45505d511f6cf4ad14a4b4f9e8cdabfb80da7708c7319a` |
| 40 | java | passed | solution_verified_numerical | `834f6fe78a0029bba0836682ea2eccef63b9fbc8faeb190929d3595343ab6f6b` |
| 41 | python | passed | solution_verified_numerical | `b77c0fe779e888a10c5171bb385a85136459fe0dc45315f19b3ff0ecb4100d96` |
| 42 | java | passed | solution_verified_numerical | `ce9bfd93a6a3cf072cb2513e4a1454d3fcc165765d51f07dcf85cac262798015` |
| 43 | java | passed | solution_verified_numerical | `723f4460f8ab79ef7e7f52a0d620b19e60eb804227c55c66dcbad10321e3ade2` |
| 44 | python | passed | solution_verified_numerical | `4824f92ad4f295082f4a348d9f27fd9de62dc61c970834687033e25360a079fd` |
| 45 | java | passed | software_API_config/reporting | `497242b92c0483cfce174c1e853086265f312af0d5673c04eb5d4c1e0b2dbf8b` |
| 46 | java | passed | software_API_config/reporting | `34ab90df8709ade8738bf32ebd808253b55d7a38f91a791dc0fac15937bb0094` |
| 47 | java | passed | software_API_config/reporting | `1946997bc582e0b17dfbbb4b207ca7d3b2e4f54e60385bea52def78a1fecfa2e` |
| 48 | python | passed | software_API_config/reporting | `4a10e9dd9fa94cb2cadaf0faec74cef6ff40984206913baed0a6d0c890cd2620` |
| 49 | java | passed | software_API_config/reporting | `53625d7847d9219cf82463f37843ddda4e1cbf681a5ddb0d781f3be03aa9caed` |
| 50 | java | passed | software_API_config/reporting | `691bfd15bc5f522d3e6239842c7d7df295368a6e6efa0c4f56ded1289740c42e` |
| 51 | java | passed | software_API_config/reporting | `1e51b345f6f794d0036666931d9ae96521b3c2fe67924d6232839c4781907efc` |
| 52 | java | passed | software_API_config/reporting | `b8415e1f0f99d73fb2ef64383a405fcb743d2187d0e79253767ca9af85c07664` |
| 53 | java | passed | software_API_config/reporting | `a4a35fc6ba67fb0e728c61fabd7c872c55509b67c6ab28b177a49aa386e93490` |
| 54 | java | passed | software_API_config/reporting | `424879afeb2073415a4982d32ab61a2ae7e8a0b5f1594f102d40e5b4df444180` |
| 55 | java | passed | software_API_config/reporting | `5cd3ad8f671bce176bddf042681a13ae45a6f89acf40bf3a6fc5524f97b32c31` |
| 56 | java | passed | software_API_config/reporting | `460aea5701cbf4e8719a6ab75d4d127ccdbf6f310e77b75fde5f22902ee78a76` |
| 57 | java | passed | software_API_config/reporting | `43f4ee55be589c56171cae798a795f67c6bcb2f142325b77e562cc6e4c0f02ed` |
| 58 | java | passed | software_API_config/reporting | `2f9f8b0bc63fa01d17f8fb986f216c7246d86bd2b39ec6f61bc33d45bcc9a1f9` |
| 59 | python | passed | solution_verified_numerical | `ca7390f221165c7ea49402fea7a612556cb1110334f379615641512cb091d526` |
| 60 | python | integration_pattern | declared_external_pattern | `053e5c5430451872a7eaab65ad40f3503f1ffab0255b91f514d0d1308266e281` |
| 61 | java | passed | solution_verified_numerical | `17492ebb16193d9af3c47aadfb943317c0b3fc93b26bdea82067329a55d26d99` |
| 62 | python | passed | solution_verified_numerical | `4aecd64d8c7e1394cfedb9dd08bd1c68a7cb18f3e936502046e4245ffb227809` |
| 63 | java | passed | solution_verified_numerical | `9c0096e387224ba5ae02df96397676680d965dddfab0b7c73478d55a4344a6c5` |
| 64 | java | passed | solution_verified_numerical | `cc76457c563e28aa64098c1612fb6650938b36d46790cc1f83713e350ced6397` |
| 65 | java | passed | solution_verified_numerical | `0cd31e7c17c4c4cb46cd63a187f88bed1c53864db93795b1fd041137f91140da` |
| 66 | python | integration_pattern | declared_external_pattern | `c8bf0a5a6cc1ff622ba7431282959c492059be5f455111098ffbe46ffdbd0463` |
| 67 | python | integration_pattern | declared_external_pattern | `67e2b1ba8662ff7fee76342e851229cbd59c1e7804d248142ffd34db9fc7c73c` |
| 68 | python | integration_pattern | declared_external_pattern | `0c2c54992704f2ed5564f3dd45ee03f43e503ef6e92b271398da05bad6ba93a6` |
| 69 | python | passed | solution_verified_numerical | `f188273ec2a0d67e5bf876f54ff7d11a497924f87f0dffcd2bf63c1e24ba5225` |
| 70 | python | integration_pattern | declared_external_pattern | `a04be98ae816dfe617dfe4721f44a4a021a931d39c90d04a3cdab388b45c4fc3` |
| 71 | python | integration_pattern | declared_external_pattern | `774544c5acc39b0f8051563b216830931fe6a22bc07c505ed4f5ab0ba145ee0e` |
| 72 | python | passed | solution_verified_numerical | `fd2cdc8776976cac5fc4d65fe8f1df024d1338ff747eee8d438948b838f5ee07` |
| 73 | python | passed | solution_verified_numerical | `94477f12a1f54f872f50624264153d1108aa956da400d6eb2cf40bb5e0831364` |
| 74 | python | passed | solution_verified_numerical | `761270e2a543fad77d5c6094263cd9f2868fbd6874ed69d335cc75a904e826b3` |
| 75 | python | passed | solution_verified_numerical | `c8d6a77a1d9886d88961062046629cac2f84044eee524de51fd79e5b85212395` |
| 76 | python | integration_pattern | declared_external_pattern | `98b767e10f3c200afd3bd8bd53bfabf5d395ea241c2e706f7fdb41ceaac6964d` |
| 77 | python | integration_pattern | declared_external_pattern | `7abfec7a51d9054394e894a1ef7d1cd9c56410a284dc31d4769cf56064cf2980` |
| 78 | python | integration_pattern | declared_external_pattern | `7f93fbc079790b6c0f318783af2d56de14e2dc92982ea5c2151644b2b36f9d7c` |
| 79 | java | passed | software_API_config/reporting | `fea909e547d8e78c21b05fff9848cacf3dbd16ad346efca6ea2a85f127c98f37` |
| 80 | python | passed | solution_verified_numerical | `698d5b71ee872e0d1a3a1c3ffae50bb9b15b4151f27e6a8a87a27e9e55029a0f` |
| 81 | java | passed | software_API_config/reporting | `0c4b6be09ab81d1877a9fc0d4450a5d1984de12f08c0a05e70e6d66c2fa0428a` |
| 82 | java | passed | software_API_config/reporting | `b97558124435e41adf213e623c31b6b2862f705fc65995fbb5ef13954c48dcc4` |

## Chapter25: Capacity surveillance, measurements, uncertainty and operating recommendations

Source SHA256: `fd5bd68bf7291b2578a6806916013f63888fa5d8688a0a5c023473498efab347`. Full text reviewed: yes.

- Corrected utilization/margin denominators and distinguished calculated load, assumed limit and installed evidence.
- Removed unsupported field history, degradation and savings claims; marked thresholds and economics as assumed.
- Clarified history quality, consistency of units and effects of missing or disabled constraints.
- Fixed native percent/fraction boundary in every monitoring path, with independent readback and trend/rule checks. Corrected CPA water handling and connected cooler/knockout/compressor topology.

**Acceptance and limitations.** Local process equations, percentage conversions, trends and dashboard logic are checked; live historian measurements, field calibration and installed limits are not supplied.

| Fence | Language | Execution | Scientific classification | Exact code SHA256 |
|---:|---|---|---|---|
| 1 | python | passed | solution_verified_numerical | `c06228da8e6091763a25f7759958cef26321e5b2236fdb6c2537ae45bcdb1c25` |
| 2 | python | passed | software_API_config/reporting | `740447843438c868f1eb6e2fb377035a5bbe82b134dc378f64fdcb824561fbff` |
| 3 | python | integration_pattern | declared_external_pattern | `b17e2d89c2bddb6c6d5bf426d7066e7776f36e79aa3bf5fbb17d021d356b74ef` |
| 4 | python | passed | solution_verified_numerical | `ea4e4f85fd429e4e70bc9c382c2424b2cb9e4debe8748535f6356b71b2cc5d03` |
| 5 | python | passed | solution_verified_numerical | `2ff6bb8042a50e6f6429ef9e010ffafcbf7b1d35a9c4ce7bd9288c7c9cdb4980` |
| 6 | python | passed | software_API_config/reporting | `d66ac77cf4f6c7d1c2b32f2e4e3ba1c795f403839939d11815e05fd05cb0cb51` |
| 7 | python | passed | software_API_config/reporting | `a15afd3a7cce85015ee39d29cb1d58a0a44f012f3fb599fa4c9daf5bc5711e85` |
| 8 | python | passed | software_API_config/reporting | `948d59e6156ed24a701728b2a2a7bce6bc4f421f02cc3c3c099bf44f77e7cf9a` |
| 9 | python | passed | solution_verified_numerical | `f072d0e489f78295dd2087040f40dc61fcf11cc62e5ce7f16ca666feecc5a479` |
| 10 | python | passed | solution_verified_numerical | `7b1ec94be62aeeb521f9ac565a47fa0df510618caec9c6ae31ed81974ff955b2` |
| 11 | python | passed | solution_verified_numerical | `665a5db85ec179c66b60312571cba260572b2f99bdaf64d32a80cd56dd37a99d` |
| 12 | python | passed | solution_verified_numerical | `740ec4c239d5bf8630c92ebe462b7f9a7a89a4152a31c5305694830ec88e0559` |
| 13 | python | passed | solution_verified_numerical | `e8454b133afccd5997e282e11e7d1906995c7f1ef5089bd36e9142d0e06677b5` |
| 14 | python | passed | solution_verified_numerical | `7bbc194cc86810cd7aa075fa3456bb4fbc9c69f0977fead568746abc16caad29` |
| 15 | python | passed | solution_verified_numerical | `bdbfb55729f6e9ebe7d79fdae4e9b1c30d11e66696f1ae041bfff62bedfe7ab4` |
| 16 | python | passed | software_API_config/reporting | `a900fb68d4c82ee7bc18352e27a6f0fd68760ce84c59049e940ee6ae4c98294c` |
| 17 | python | passed | solution_verified_numerical | `2f597718646262135ec070946381a68b384d1d748f454313f404fcad94a50a54` |

## Chapter26: Well/network allocation, hydraulic boundaries and a verified reduced allocation problem

Source SHA256: `9b22714c730d6ff1e1d356e82be8cab93e9a3db315ee1c52d0dde03e3c0a673d`. Full text reviewed: yes.

- Corrected IPR/VFP pressure boundaries, volume-reference units, lift accounting and topology/solver interpretation.
- Replaced the central heuristic allocation with a six-well linear program, independent dual certificate and fresh NeqSim compression replay.
- Separated fixed-composition linear compression allocation from full hydraulic choke optimization and source-only integration adapters.
- Verified pressure-boundary network junction balance and corrected kg/hr readback. Native tabulated lift candidate misses the accepted7050Sm3/day segment-LP optimum; this numerical rejection is retained explicitly.

**Acceptance and limitations.** The accepted LP uses fixed GOR/water cut/composition and linear power scaling verified over the stated model; it is not a calibrated reservoir-network optimum. Other network API examples have narrower checks.

| Fence | Language | Execution | Scientific classification | Exact code SHA256 |
|---:|---|---|---|---|
| 1 | python | passed | software_API_config/reporting | `1c9a1d2e093ea5a2446b98679d986c54956db10c898ea26c7c7cc06a428e6b82` |
| 2 | python | passed | solution_verified_numerical | `d0f0abebe607b7caca0300c1dfa4c5d4054bf4a5dcbe87834ea811e2e97e5f18` |
| 3 | python | integration_pattern | declared_external_pattern | `e4a441983b96c27b6d71e760bb4c12763cf6400e86cfec4d1d764066ca3f6940` |
| 4 | python | passed | solution_verified_numerical | `c8d42da2872f2544aea1b2dad1715f1fafa11a73ca2102be400fec3f5170ffee` |
| 5 | python | passed | solution_verified_numerical | `9cbbcda899ffa9b665ad715856d416e95679223874644323ff70ae6eb9b5fc89` |
| 6 | python | passed | solution_verified_numerical | `fd7d68d8a33e4928505a866778b0b089af0119d89e1eb7d899182b9854be43ad` |
| 7 | python | integration_pattern | declared_external_pattern | `2ef0fe02c17ec3ec8291bdc6ae5cfb0e786c0ff7b00691394c7b4446fd0978f3` |
| 8 | python | passed | solution_verified_numerical | `a0edfed88f2fe46d04070c233c0205aa6347f1134c6559ae612a0c25bd326339` |
| 9 | python | passed | software_API_config/reporting | `a0e58e25a5851e532aeaf153d938a3dc1d914898b9614db849defeae73780570` |
| 10 | python | integration_pattern | declared_external_pattern | `38538337fc93106328b3260bdff11e01521a55f61ef5f71f3376932453c64888` |
| 11 | python | passed | solution_verified_numerical | `baf1a904522020d00d2252ecaba2591a0734a4a64b34450778e4fc3dd6862f92` |
| 12 | python | passed | solution_verified_numerical | `ccc2f3f18f767003a7a937d54ee6e846440c909220c7b4f2c7bfd6bce724244b` |
| 13 | python | passed | solution_verified_numerical | `c707fdb6c9dc3590abbc9e0c8fdbcc03a0afbb9a6921688e5a8508d2d4f9d63c` |
| 14 | python | passed | solution_verified_numerical | `2fd2e828e283ab5e574df139d1edc4ce06760d6d2596f3b0faa82deff1bc345f` |
| 15 | python | passed | solution_verified_numerical | `c75a0e818d139a112c9e5593b9dacc4b4c3357dae309aa3e3e7b758ba04ffe07` |
| 16 | python | passed | solution_verified_numerical | `3b0ff330b53075c73799a85ba2f2ef1970cccec3dcc27c680d3d2112cdf3d03d` |
| 17 | python | passed | solution_verified_numerical | `83541248df82c2204b1ada88417cb9336edfdb56aad72d1a6b03af4307ba2836` |

- Fence8: Exact literal execution with supplementary numerical/physical/software solution checks; not field calibration.

- Fence14: Exact literal execution with supplementary numerical/physical/software solution checks; not field calibration.

- Fence17: Six-well LP: bounds1e-8, primal capacity1e-6, nonnegative dual multipliers1e-10, dual inequalities1e-9, dual gap1e-5; fresh NeqSim power replay1e-4kW, mass1e-10 and enthalpy-power1e-5 relative.

## Chapter27: Scenarios, Monte Carlo, tornado sensitivity, robustness and resource economics

Source SHA256: `5fe74505eead6cf327bf0ee383e2277f998a5607488d0db677f5c9a29208fc68`. Full text reviewed: yes.

- Replaced non-conserving/unbounded production forecasts with400 full NeqSim25-year isothermal depletion profiles, common stratified uncertain resource/price/CAPEX samples and explicit pre-tax cash flow.
- Rebuilt200-sample surface uncertainty and11-case OAT with normalized CPA water mole fraction, three-phase separation and per-unit/whole-process conservation.
- Eliminated silent failed-sample filtering; tornado endpoint labels are low/high inputs and span includes the base.
- Verified compressor efficiency has zero upstream gas-yield effect in the prescribed-rate model while changing power.
- Corrected CDF versus exceedance percentiles, CVaR loss convention, scenario confidence, EVPI/VSS and resource-balance scope.
- Additional checks verify all five scenario process boundaries, scenario probability normalization, algebraic quantile identities and parallel toy serialization.

**Acceptance and limitations.** The reservoir is a pure-methane isothermal tank with a declared rate rule, not an IPR/well/network forecast. Sampled percentiles are not tail-confidence guarantees; no tax regime, field calibration, dependence model or mitigation value is established.

| Fence | Language | Execution | Scientific classification | Exact code SHA256 |
|---:|---|---|---|---|
| 1 | python | passed | solution_verified_numerical | `676f0397f7ec2c195da59864cf18ea61410184bfe0b59de9a9be7dc603d7d0c0` |
| 2 | python | passed | solution_verified_numerical | `1048470f571f0ee99b9b24df422a0429b6b337124402d65e9ee5ef91655e033d` |
| 3 | python | passed | software_API_config/reporting | `6aeef9d65fc156da48c6e28dc418993e83dc4cfd3ac28ff3dedf8f34743ce647` |
| 4 | python | passed | solution_verified_numerical | `d4563b93411620afce6c9d112e54a0ace199835d1e01df06af11d44b7078f869` |
| 5 | python | passed | solution_verified_numerical | `f4534247f55d90e1d375a01487385d9439cae50b7a9500b5146a0d7f34196a24` |
| 6 | python | passed | solution_verified_numerical | `45cc5159553b232eac620723f158a77843917fd000f348b6c4f26b210d6b4cdb` |
| 7 | python | passed | software_API_config/reporting | `20b3e0c3b80e0de2e09f5081e7f0dcac6fb9e7170185a955177f75a876e53f1d` |
| 8 | python | passed | solution_verified_numerical | `7b644188dfaf9e6a6b86cfa6889c2cfeebef57fc30553cf3d27df258a4f3bea6` |

- Fence4: CPA three-phase surface cases: per separator/compressor/whole process mass/components1e-7 and energy1e-5 relative, finite positive p/T and nonnegative flow, gas-only compressor inlet.200 LHS cases plus11 OAT cases. OAT verifies zero upstream gas response to efficiency within1e-6kg/hr and nonzero correctly signed power response.

- Fence5: CPA three-phase surface cases: per separator/compressor/whole process mass/components1e-7 and energy1e-5 relative, finite positive p/T and nonnegative flow, gas-only compressor inlet.200 LHS cases plus11 OAT cases. OAT verifies zero upstream gas response to efficiency within1e-6kg/hr and nonzero correctly signed power response.

- Fence8: 400 NeqSim isothermal tank profiles,25 annual steps each: initial GIP1e-8 relative, cumulative mass1e-9, positive inventory,49<P<=250bara, fixedT1e-8K,0<RF<1; finite pre-tax NPV. No adiabatic energy claim because temperature is imposed.

## Chapter28: VFP construction, production-flow orientation and export contracts

Source SHA256: `12cc0e9866a1029395aa1be4abd2ea6654c5d1744caafc78c87fe64e471bc954`. Full text reviewed: yes.

- Corrected BHP/WHP boundary semantics and the difference between well hydraulics and process maximum-flow curves.
- Documented current PipeBeggsAndBrills inverse pressure mode, outlet-setter ordering and pressure residual acceptance.
- Corrected water/GOR recombination bases, gravity/friction trends, nonmonotone production VFP behavior and software export metadata.
- Removed invented timing accuracy and automatic field-validity claims.
- Specialist verifies each literal recombination/table/root/contract case; corrected third recombination argument to standard total liquid Sm3/hr and checks realized GOR/water cut.

**Acceptance and limitations.** Literal pressure/recombination/constraint/contract results have explicit solution checks. Diagnostic process capacity is not production-well BHP, and field well-test calibration remains external.

| Fence | Language | Execution | Scientific classification | Exact code SHA256 |
|---:|---|---|---|---|
| 1 | java | integration_pattern | declared_external_pattern | `36de4dbef1e8f5f950e6bfbf245be246b94dc780297e9e430652c8e3bf44f37e` |
| 2 | java | passed | software_API_config/reporting | `297ef64d14656343155acd282859e7fa66dd4a7201f34bfdb1066900075f6e5d` |
| 3 | java | passed | solution_verified_numerical | `e2fa465b5dfee704281012ae28817bd155bebb9ab463864d1226f2f94f139376` |
| 4 | java | passed | solution_verified_numerical | `cc4e5273569a45d71ab30f0847344ba412a0e781866a74d16067454b224a48c1` |
| 5 | java | passed | solution_verified_numerical | `f2ec1f16f7db8d224cf8e0745c8245e75aa425d674694d117201e1657780dfa7` |
| 6 | java | passed | software_API_config/reporting | `a67e1e417d2ce18731601d086829ebc3ccd49861a9b12e52b4e5e0c92d0d0be7` |
| 7 | java | passed | software_API_config/reporting | `484e106633169fc2d9cefb73d939d9d008d0960b5f73fe1147b1359890b8b2c2` |
| 8 | java | passed | software_API_config/reporting | `2602f5e1df382b5ce9a000ee91224673bff7f551a7cbd0cbf4c621e98b54909c` |
| 9 | java | passed | software_API_config/reporting | `1b8f7799c0e5ceb1c698fef456add2e86f22a256e6303168105c480cea1c13c9` |
| 10 | java | passed | solution_verified_numerical | `16f9a4970ae2820baa47dd0bda397a37eaaddf53e27489da1b7db67e5cd6f5b5` |
| 11 | java | passed | solution_verified_numerical | `a33fab4b9c80df36628bd8dcd0db2ef2738917fc91d8e0ff1209bc8eb13491ba` |
| 12 | java | passed | solution_verified_numerical | `54e13b311e6a992ae15d492bbea583a6951341268dcef89aab731b9c27030443` |
| 13 | python | passed | solution_verified_numerical | `e28173dfbf0c9c3912e69d3a274dd6e8f01bf08fde88c9de7cf661345a528a1c` |
| 14 | python | integration_pattern | declared_external_pattern | `428dc8c5a31e76986aade372ee207a9d4ca6df230abcf5987fd1bf48eadb9248` |
| 15 | python | integration_pattern | declared_external_pattern | `bd92750060a21054b3cedc67e3dc45da2342fb190b8b4a9627d87f7451d20896` |
| 16 | python | passed | software_API_config/reporting | `ee167c8ddcc969724e2875c64b477a7005fba8240d30fcfe6da5ce613df5ec7f` |
| 17 | python | passed | solution_verified_numerical | `5ee5f89747462ffa2e5afc397692a15ba53e0f1847c2aa2c974844fb57fa4b1c` |
| 18 | python | passed | solution_verified_numerical | `ce1970f65d9a5c788bfa9fe842cd54bfc47dafd439f36fe13d47b23cf95f805f` |
| 19 | python | integration_pattern | declared_external_pattern | `22ffcbfea65f5e64bab0cb12ea08a04c23531cf813624c2c5ad2a2cc6ac0fff1` |
| 20 | python | passed | solution_verified_numerical | `54f9a650bb21c8bb93c4952d461862bee22ea0bdc3ac91e6a71ec15540c6dee2` |
| 21 | python | passed | solution_verified_numerical | `6671ec6827fec2300d8d811f635ecf825478e2ff2bcd457799f2be06936e0fb9` |
| 22 | python | passed | solution_verified_numerical | `3e4f2eab457ae6b5a7b8721ae569693b44719d3ffac919712376d0e7f7402e69` |
| 23 | python | passed | solution_verified_numerical | `7425ee70e8ea744883092565c3e49b35dc4245e0f49b1a6b64653104cc30472c` |
| 24 | python | integration_pattern | declared_external_pattern | `b9195d02f73ed93c09c0c4fd119d16b12d86da704dd877bbddce8a5cf03dca8d` |

## Chapter29: Dynamic inventories, control, depressurization and protective-system scope

Source SHA256: `41e9bd6ee399a17ef369e3abd033430ee0007229b480bba9b9b846e9178d9b39`. Full text reviewed: yes.

- Replaced illustrative controller output presented as dynamics with native separator inventory transients and cumulative mass/internal-energy checks.
- Corrected level feedback sign, native fraction units, circular segment free-surface area and SIMC PI tuning equation.
- Added timestep-refined depressurization including explicitly budgeted1e-6kg/s regularization; distinguished gas temperature from wall/metal temperature.
- Separated steady recycle topology from antisurge protection and imposed feed pulse from resolved slug hydrodynamics; removed blanket API52115-minute claim.
- Supplementary steady recycle now uses explicit polytropic mode, tighter recycle tolerance and whole-process enthalpy/material checks. Java measurement readbacks verified against direct stream values.

**Acceptance and limitations.** No wall thermal inertia, installed valve certificate, compressor map/surge dynamics, relief qualification or field controller validation. The blowdown has a quantified regularization inlet and coarser1e-3 energy tolerance; the companion notebook is separately an illustrative lumped controller.

| Fence | Language | Execution | Scientific classification | Exact code SHA256 |
|---:|---|---|---|---|
| 1 | python | passed | solution_verified_numerical | `4729d9a851a0a33b689e4d9bf1191a5f036aeb5cd707993a9b7b2eb4cc37584e` |
| 2 | python | passed | solution_verified_numerical | `3968961e35e6c87511354d214ee1f0f9702851ac2914c0898d3c8b320b96de1a` |
| 3 | python | passed | solution_verified_numerical | `a81a36a83b39b44091cb25249986c243dda093ecca500855a7f8a99f3509042b` |
| 4 | python | passed | solution_verified_numerical | `19f7193ab78aa24396ba962b0a6429862a75a851db3a1efaf8e4df62d19c5021` |
| 5 | python | passed | solution_verified_numerical | `352ec53776735acde02e551eb12b9315d7288bcfa4ff7b3c6c96df89cd2a47c0` |
| 6 | python | passed | solution_verified_numerical | `498fbfbe95bd7c1ccdbcf92e7c74478d082eca527a138182b3d32d3ff77f8ba8` |
| 7 | java | passed | solution_verified_numerical | `e6e0e22f0c93188963772024948a34516fb3cd057b034a983837d5e6269b03ea` |
| 8 | java | passed | software_API_config/reporting | `f82155302cf33ddaedf2c4366fecbdedbbdc905856204191638c81d258479c33` |
| 9 | java | passed | solution_verified_numerical | `dbab4b16a94b47b92d4a25a356f387a5356d3dea32c6252d652a3a9d2174018a` |
| 10 | java | passed | software_API_config/reporting | `72b0ff8a141cab8d52f29306732e59f678adfc496fa43753cd579bbd33fb42ba` |
| 11 | java | passed | software_API_config/reporting | `e2170b98cb31583920ac6ae235e42d1744b797cd471e29dc6120c00674206777` |
| 12 | java | passed | software_API_config/reporting | `45ee61c07c5bb2fc4c059f6eff5f8ba838599ee5127575b39d7834d7d2675b18` |
| 13 | python | passed | solution_verified_numerical | `826b0a76d66ff2bb4da9d5d6b38efd3f6890fb322ab55e7355d672712facf279` |

- Fence1: 120s native separator with20–40s feed pulse; integrated mass1e-10, energy1e-5 relative, finite0<level<1. dt0.5/0.25s: level difference<0.001 fraction, pressure difference<0.01bar; final level within0.002 of setpoint.

- Fence2: Exact literal execution with supplementary numerical/physical/software solution checks; not field calibration.

- Fence3: 120s80bara blowdown: mass1e-10, energy1e-3 relative; dt0.5/0.25s differences<0.05bar/<0.1C; monotone pressure decline; regularization inlet contribution<1ppm of initial inventory.

- Fence4: Imposed separator feed pulse: native mass1e-10, energy1e-5 relative and level<0.6. Uses the checked inventory integrator; not resolved pipeline slug hydrodynamics.

## Chapter30: Digital-twin data contracts, model calibration, MPC, hybrid models and automation

Source SHA256: `6c51737e4b09c856f4e8a430431f4310dbe347310e0b25ed5e31c4497919db02`. Full text reviewed: yes.

- Added local data-quality and steady-state fixtures that reject corrupt, missing, trending and oscillatory inputs.
- Corrected covariance-scaled anomaly score, data provenance, calibration uncertainty and native MPC scope.
- Corrected coupling at common physical junctions, input/output address contracts and save/restore limitations.
- Removed fabricated measured data/benefit claims and corrected primary NMPC/surrogate/informed-ML references.
- Supplementary process, batch tracking and synthetic comparison checks preserve Celsius absolute deviations; no percent-of-Celsius error or invented measured data. Java state fixtures use explicit polytropic mode.

**Acceptance and limitations.** No live historian/OPC access, field-twin calibration, closed-loop plant control, trained model or predictive fault diagnosis. Synthetic tracking is a data-plumbing illustration.

| Fence | Language | Execution | Scientific classification | Exact code SHA256 |
|---:|---|---|---|---|
| 1 | python | passed | software_API_config/reporting | `8dee61c38f00a06a1502e0e8c2eb64c5b8be84f8d146be664668fdee9eef4814` |
| 2 | python | integration_pattern | declared_external_pattern | `d160ce5dc696d6ecfd47798853fbf387f233f60fc61209a8ee1d633d2fd0b1ad` |
| 3 | python | integration_pattern | declared_external_pattern | `f2d72e1e52a3b04008e9c330a53ec4c862ed49d71b040998b016f51c319e9b62` |
| 4 | python | integration_pattern | declared_external_pattern | `d043a5564815173f37b81c05149962063f0b359cf597eedfebd474c66dd8d7a2` |
| 5 | python | passed | solution_verified_numerical | `4423c0803f523eb1238d2e869352120ff52477c1a090b9c6bc7e8d013662b528` |
| 6 | python | passed | solution_verified_numerical | `c07929cf930238fc1faeb1948dc29eb6093b3eb6c44f1874ea95c4d12b858b3a` |
| 7 | python | integration_pattern | declared_external_pattern | `260bca41c3aa5ef180fc9edae497176e49227e24e08124a914c534a2cf5bda4d` |
| 8 | python | integration_pattern | declared_external_pattern | `d0817e24739f9b58e83f537e6b122f8f687c3e05263731e578a7a979bef986c2` |
| 9 | python | passed | solution_verified_numerical | `d7e6cc5c3dbfa04da44856ba1035aca23f3899b12ec77018558530e750497aa2` |
| 10 | python | passed | software_API_config/reporting | `5b07016c5f26df147909b754e112256916dda33ca6e585fbf9c41d327cd02af7` |
| 11 | python | passed | software_API_config/reporting | `86b52963653f7024d2940acb1afc17149e95478b5a0d90ed099739e54327b827` |
| 12 | python | passed | software_API_config/reporting | `b9c96501a52351fbcfeb3579196bc7b23029efd66a433aa84a72a537f4ca685d` |
| 13 | python | passed | solution_verified_numerical | `250de80f6cd6911d5b53d318319f6e098b59859abad636e8b49dbf9056b7fb17` |
| 14 | python | passed | solution_verified_numerical | `912459a2c6e12972a35082b81aadd37662cfdf02458377c3f16ffe606b222744` |
| 15 | python | passed | software_API_config/reporting | `bd19812b0e039987c6bb4fb3e1116eff88d3d93e07364fde637f7bbba365908d` |
| 16 | python | passed | software_API_config/reporting | `d6babf805b223844db883232c44d905be76a81fb59c4aca2ac12149d010df3b9` |
| 17 | python | passed | software_API_config/reporting | `b0e589919f45cffadd113e896232836b94549a6eae6960c115bc9ba87a267cf6` |
| 18 | python | passed | solution_verified_numerical | `5fb7bf36b875f9f01139c687991ab940c96a9c6dfa3aca37413d077f8d781b19` |
| 19 | python | passed | solution_verified_numerical | `632411427db9fa32ce251592e693b3b3e9e10eac2c74fe4f0b0ca6af105b4c95` |
| 20 | python | passed | solution_verified_numerical | `cf042d92ac3b491568464ee4e06b3463a4a4d07be648bd011648e30b714024d3` |
| 21 | python | passed | solution_verified_numerical | `953ee229f3ab89a494904780f3577a3435066f2bb2572f9cf1d495adc85d2323` |
| 22 | python | integration_pattern | declared_external_pattern | `4c08f4cb86362d3ae46c4f358109ca9f078f8a15e5c54ede2282793b516b2a10` |
| 23 | python | integration_pattern | declared_external_pattern | `c5a0d30846d42ef2a597e45fc47d69c71d6b5be756ffe0245d9b2b8419aa0664` |
| 24 | java | passed | solution_verified_numerical | `abead007680d6f29aa935428ccc710addcd59655f8c31b67a57b86a85f820055` |
| 25 | java | passed | software_API_config/reporting | `e75ab8a74845fffb14c6b85085528d70b79ce3cd051ea22c76d95f8aee77f673` |
| 26 | java | passed | software_API_config/reporting | `4027ad707f19d8fd69e2563454391a2f89ab0eafed9df1973a896c08b06a2c4f` |
| 27 | java | passed | software_API_config/reporting | `42aa89357587076a411c4d50a6164f38cd06e643c154fb0809862f0764cc40f1` |
| 28 | python | passed | solution_verified_numerical | `e7c8479f5c474d40bc91dcad36b30bb26a8d7a539f2787f8ed128bf0c0119714` |
| 29 | python | passed | software_API_config/reporting | `fc54e2237d87d8b50d4499fda31c1c5482e6dd277b5222c7e39995737c26db32` |

- Fence5: Synthetic in-memory data: preserve raw values and mask implausible/missing data; steady detector accepts stationary case and rejects drift, oscillation and missing windows. No historian/field observation used.

- Fence6: Synthetic in-memory data: preserve raw values and mask implausible/missing data; steady detector accepts stationary case and rejects drift, oscillation and missing windows. No historian/field observation used.

## Chapter31: Flash, recycle, adjuster and numerical solver mathematics

Source SHA256: `682144a7c87dcacdeb3fb0d2abc3ab549d0dc27e4b8c84147d27906d21b4d66d`. Full text reviewed: yes.

- Corrected fugacity iteration, Wegstein update, molar EOS basis, Rachford-Rice and phase-stability interpretations.
- Added phase-composition/fugacity and PH target checks, actual fresh-separator recycle with16 iterations and component/material/energy closure.
- Repaired adjuster callbacks and checked a reachable40C target through independent valve replay.
- Corrected native recycle tolerance units/cache behavior, column solver enum/acceptance distinctions and explicit/implicit time-integration claims.

**Acceptance and limitations.** Column strategy and generic transient fragments need supplied consistent inventories/feed/boundaries. The accepted column example is in root-owned Chapter33. Tolerance attainment is numerical evidence, not experimental EOS validation.

| Fence | Language | Execution | Scientific classification | Exact code SHA256 |
|---:|---|---|---|---|
| 1 | python | passed | solution_verified_numerical | `2306252a9e1be1ca78dc3965d10fcc64061c49edc53d8d4dca9c7e00664abba1` |
| 2 | python | passed | solution_verified_numerical | `d0726af470e2f2df7603dfd708a22467d3456f49b89985dfab6a55ea134a8f8c` |
| 3 | python | passed | solution_verified_numerical | `86dfc4342d8284d95568f12400b4261e29b2fd5642e0c9732eb3530ee51b6f41` |
| 4 | python | passed | solution_verified_numerical | `a2344592a56862824b4cc056f2942f0ce26e122cac3e217b9515dcb6a4f5486d` |
| 5 | python | passed | solution_verified_numerical | `48c7b64bbe52a0bbe111621f7814561eb8d6c556ca49d6ee0c8bee58afc00589` |
| 6 | python | integration_pattern | declared_external_pattern | `a3a8b5b049815990b86337b5038429b3a4092f4071264a3becd4118e9ee12080` |
| 7 | python | integration_pattern | declared_external_pattern | `6a74726efdbabbc24c8e77d2b910f02cdaceb55c252c88087db8bb7534cdc06b` |

- Fence1: TP equilibrium phase composition reconstruction1e-7, phase x sums1e-8, fugacity log ratio1e-5; PH target1e-7 relative at50bara. These are solver identities, not external experimental validation.

- Fence3: Fresh separator per tear iteration: actual flow/T/composition changes1e-7; whole-process mass, component and energy1e-7 relative.16 iterations; diagnostic figure uses actual residuals.

- Fence4: Fresh separator per tear iteration: actual flow/T/composition changes1e-7; whole-process mass, component and energy1e-7 relative.16 iterations; diagnostic figure uses actual residuals.

- Fence5: Adjuster40C target with5–95bara bounds; fresh independent JT valve replay within1e-4C, flow within1e-5kg/hr and isenthalpy1e-6 relative.

## Chapter32: Advanced optimization, local calibration contracts, surrogate uncertainty and batch execution

Source SHA256: `caff729726621e0aaa402f99cc94b523a47ce53dbad8ccee1ce28616e8f438ab`. Full text reviewed: yes.

- Added a converged two-variable SciPy optimum using fresh full-process solves, independent feasible final replay and2121-point exhaustive grid bracket.
- Retained a rejected native candidate as a diagnostic instead of an accepted optimum.
- Added native steady-state ratio versus independent formula, linear reconciliation versus closed-form covariance oracle, and known-efficiency calibration with independent three-pressure replay.
- Corrected residual covariance, unit conversion boundaries, native API names, KKT/globality and ensemble/conformal coverage claims.
- Replaced invented parallel performance with compared sequential/two-worker fresh models.
- Added independent25-point Pareto trade-off grid, fresh12-case batch replay, full-model surrogate acceptance, dimensionally checked daily economics and scaled gas-lift SLSQP matching an independent KKT optimum within0.01bbl/day.

**Acceptance and limitations.** The grid brackets only the defined two-variable model and domain; it is not a general global certificate. Calibration observations are synthetic. ONNX, live historian, custom RL/plant adapters and physical surrogate certification remain external prerequisites.

| Fence | Language | Execution | Scientific classification | Exact code SHA256 |
|---:|---|---|---|---|
| 1 | java | passed | solution_verified_numerical | `49b2e6ad6a7efc9bbe4228c9dc0b9ac81ec42994fb1d14e2cd6572f72c8b7755` |
| 2 | python | passed | solution_verified_numerical | `3914a8e6cc500a37eedcdf31d2609348a810549f4bdd2b140b930c6627cd2077` |
| 3 | java | passed | solution_verified_numerical | `a1e6374574c79f135d3df54f203014defbb54699979ede662dac19de059b58e0` |
| 4 | python | passed | solution_verified_numerical | `e0dc38e6781c9f6e5588b990843c01814e4942f336c87814c5b7841b5887a1aa` |
| 5 | java | passed | solution_verified_numerical | `cd4e03b954bbcb6d04248c890c90eb10633c72de2f50325fbc7bf3e5c57858da` |
| 6 | python | passed | solution_verified_numerical | `fe92847252123d4f7709a9774e6f1189d725ddb5476011e2165c2e06ed96496b` |
| 7 | python | passed | solution_verified_numerical | `e266895279305f767866061f070b3abecae7116f3a67426e990c40e7b161d9ce` |
| 8 | python | integration_pattern | declared_external_pattern | `c68f21cbdc53e02c9de90dc746532a43d8c2ef71476a9395c81f2b02f6325220` |
| 9 | java | passed | solution_verified_numerical | `77d495d1e8673e0145d20b2e16b0d9f00b3bda15c66e89a16e36f71a0c78883d` |
| 10 | python | passed | solution_verified_numerical | `61fce18e1df8cb5fc2540fc5a2628f67ec933cff97dd4efb22d837b300bde56b` |
| 11 | java | passed | software_API_config/reporting | `d6be1c46d813c65e468062881ea0e339cf8fb535f850033c26f39dfb7ab325c9` |
| 12 | java | passed | solution_verified_numerical | `f7ece25938693f2bfa59eb0453f8a97f4ff4452ed689e3fc01c895dd0f084eb1` |
| 13 | java | passed | solution_verified_numerical | `96a44da5c6b302a69fe41d1bd1067f93b29cf7df75a0ce8487e20b7a2ce97d77` |
| 14 | java | passed | solution_verified_numerical | `de7ff30ce5bb09f4374be5d9e76cda7dbb75bbc953620be0f6c08017f400f685` |
| 15 | java | passed | solution_verified_numerical | `6adf05d49025e4d272268695278b901e0e5d3d96ea824ee13b4b5cf01b082614` |
| 16 | python | passed | solution_verified_numerical | `013fc3da82f2469d12d796a9d094cbe7aca71014a6794b0189087cf666b9677c` |
| 17 | java | passed | solution_verified_numerical | `7ff027daf565d66327d4be7d16d9fe88d8eac29643f0f780acb7f4520c82325e` |
| 18 | java | passed | software_API_config/reporting | `70dc9e0c1709b5fcac6c67ade578898a1100e1aa393179a6ee56e5767b47bf51` |
| 19 | java | passed | software_API_config/reporting | `ee44560d4b61047801d17f9dd1065514eee36b47ae1c69ae937e83f23c5e2985` |
| 20 | python | passed | solution_verified_numerical | `a7234ae0eb2832cfc871f227ef118b1ac038522bae4fba8b96f7042331a20cec` |
| 21 | python | passed | solution_verified_numerical | `a547e53430c05c47dc627b147a908310a64112fb079c36a7e664196482092d74` |
| 22 | python | passed | solution_verified_numerical | `a913a25f4880960b04db7413932863f0c3ddf8a12fa46527ccf8782272d74b47` |
| 23 | java | integration_pattern | declared_external_pattern | `2c41a30097f31fb91d041a67eaff21a17d126603c95bfcd5e15190eb1e9f9b03` |
| 24 | python | passed | solution_verified_numerical | `bafc9ea24b1f785667d907d24f4b9ac3c2d20fc449e8753c8506c1feddae8062` |
| 25 | python | passed | solution_verified_numerical | `137b358c5e9a70510252add0166f2324117482eb46943f8adedf7640cdeb351a` |

- Fence4: Exact literal execution with supplementary numerical/physical/software solution checks; not field calibration.

- Fence7: Fresh full process each objective/constraint: successful SLSQP, q50k–200k kg/hr/P40–80bara, final power<=3500.001kW, mass1e-10 and shaft-energy1e-5 relative; independent2121-case grid brackets optimum within1500.001kg/hr.

- Fence16: Native R ratio versus independent formula1e-10; native linear reconciliation versus covariance solution1e-6 and conservation1e-6; fit converged and eta within0.002 of known0.78, fresh130/150/170bara replay<0.02K; mass1e-5kg/hr and energy1e-5 relative.

- Fence20: Exact literal execution with supplementary numerical/physical/software solution checks; not field calibration.

- Fence21: Exact literal execution with supplementary numerical/physical/software solution checks; not field calibration.

- Fence25: Exact literal execution with supplementary numerical/physical/software solution checks; not field calibration.

## Chapter34: Integrated production examples with explicit process boundaries and generated sensitivities

Source SHA256: `49d610a155382212d3aa0339bc451d28d5e643fe92139eae28663dc9bca8e93c`. Full text reviewed: yes.

- Rebuilt platform topology with real cooler knockouts before compression, all product withdrawals and balanced nine-pressure sweep.
- Root rebuilt CPA FPSO with reference-volume water cut, fixed200m3/hr reference oil+water and304 unit/whole-process checks over base plus15 cases.
- Replaced one-sided exchanger/two-phase expander topology with explicit refrigeration, gas knockout and balanced NGL base/increased/nine-rate cases.
- Removed fabricated numerical tables/optima and corrected gross-revenue economics and heavy-oil claims.

**Acceptance and limitations.** Defined synthetic feed recipes, assumed screening limits and external refrigeration duty; no full vendor plant rating, detailed heavy-oil characterization, gas-lift demand, water treatment specification or selected capital project. Expander and compressors are not asserted shaft-coupled.

| Fence | Language | Execution | Scientific classification | Exact code SHA256 |
|---:|---|---|---|---|
| 1 | python | passed | solution_verified_numerical | `dc19cb522af76b375b2e1d006fdc8d54f8b582fa2dcb0d1e2aface6e87f1411e` |
| 2 | python | passed | solution_verified_numerical | `bb38e602be81c7e0294db447177c2e53279adc95a6550e63d1739be7fe51aa02` |
| 3 | python | passed | solution_verified_numerical | `a40de48a8069a9881aaf2cd6e3a15aeb5321ead85c58d60bbe6b325849b614aa` |
| 4 | python | passed | solution_verified_numerical | `9fdfe675af9bbb63f1625879dd0af80ffff2b2dbf91553ff8d6baad19cfdde49` |
| 5 | python | passed | solution_verified_numerical | `7741d5c3a1b4385000b0e1bbe7672516ee3264c5de5926875ee4be01a9cf8d55` |
| 6 | python | integration_pattern | declared_external_pattern | `f5da5e723a83e9c3b8826c6f8d9ec76896575bca17199ecb022bb83931b6a06e` |
| 7 | python | passed | solution_verified_numerical | `aeee472f8124849585b309e4e4f638bae548dee2dde90aba231c900551c5b15b` |
| 8 | python | passed | solution_verified_numerical | `2349602f99a6a45a71074eb61d5b9259ab58460eb28cdaf44e10440112dd37bc` |
| 9 | python | passed | solution_verified_numerical | `9cfdd28a1af762efe2695825496968e1f6370199b99106c68f5a557f2249af32` |

- Fence1: Fresh platform factory and nine-pressure sweep: all products included, mass/components1e-7 and energy1e-5 relative, dry compressor inlets, positive compression work and rising discharge pressure.2 is a screening-ratio report, not installed rating.

- Fence2: Fresh platform factory and nine-pressure sweep: all products included, mass/components1e-7 and energy1e-5 relative, dry compressor inlets, positive compression work and rising discharge pressure.2 is a screening-ratio report, not installed rating.

- Fence3: Fresh platform factory and nine-pressure sweep: all products included, mass/components1e-7 and energy1e-5 relative, dry compressor inlets, positive compression work and rising discharge pressure.2 is a screening-ratio report, not installed rating.

- Fence4: Root-owned CPA water-cut factory: base plus15 cases,304 unit/whole-process checks. Reference15C1.01325bara WC within1e-7, total liquid200m3/hr within1e-4; mass1e-6, components1e-7, energy1e-5 relative and dry compressor feeds.

- Fence5: Root-owned CPA water-cut factory: base plus15 cases,304 unit/whole-process checks. Reference15C1.01325bara WC within1e-7, total liquid200m3/hr within1e-4; mass1e-6, components1e-7, energy1e-5 relative and dry compressor feeds.

- Fence7: NGL two baseline rates and nine-case sweep: reused whole-boundary mass/components1e-7 and energy1e-5 relative, pre-expander/comp gas-only feeds, negative expander work and positive compressor power. Explicit refrigeration duty and independent shafts.

- Fence8: Assumed incremental saleable50MMscfd revenue at330days,0.001025MMBtu/scf and4USD/MMBtu equals67.65MUSD/year within1e-6USD. Gross revenue/CAPEX ratio is not net payback or a justified investment.

- Fence9: NGL two baseline rates and nine-case sweep: reused whole-boundary mass/components1e-7 and energy1e-5 relative, pre-expander/comp gas-only feeds, negative expander work and positive compressor power. Explicit refrigeration duty and independent shafts.

## Chapter35: Emissions, CO2, hydrogen, energy integration and prospective methods

Source SHA256: `fe80efd3e4797d2dc298233d5382ece80b881ae2287d9bb136c20a7909772c69`. Full text reviewed: yes.

- Corrected carbon atom accounting, emission boundaries and double-counting, CO2 critical-state criteria and transport versus MMP claims.
- Corrected SMR/WGS/electrolysis stoichiometry and energy basis; mixed syngas conditioning is not hydrogen purification.
- Added actual native electrolyzer atom/current/power/thermal checks at unit Faradaic efficiency.
- Corrected ISO6976 Wobbe units, dry CO2 phase screening, storage chronology, implicit differentiation and ML physical-constraint claims.
- Updated sourced flare statistics and replaced promised technology gains/roadmaps with explicitly prospective discussion.
- All11 hydrogen-blend Wobbe outputs now satisfy an independently recomputed same-basis calorific-value/relative-density identity.

**Acceptance and limitations.** Native electrolyzer example is deliberately restricted to Faradaic efficiency1; nonunit efficiency requires accounting for unreacted water not present in the current output topology. CO2 flash is not corrosion/transport/MMP qualification; no capture/PSA/reservoir physics is implied.

| Fence | Language | Execution | Scientific classification | Exact code SHA256 |
|---:|---|---|---|---|
| 1 | python | passed | solution_verified_numerical | `7b46c5203a59e3e5c41986615532365f89cd9f1106bcebe31739d4e1812e69a2` |
| 2 | python | passed | solution_verified_numerical | `e717806c1ac8d734b39a3797a00971985977201be7a6c896839d5d243b927400` |
| 3 | python | passed | solution_verified_numerical | `2ae054d36aa6abf27f618467b8bd95b9e7ced47d90bac3af599c5552411aa4c8` |
| 4 | python | passed | solution_verified_numerical | `86c1bfec2f9bac0499765d48d8dc5b1131238c2682ef36cd47b2e3364377754f` |
| 5 | python | passed | solution_verified_numerical | `1dd38f2ac5241a4189c4bbd494efd6d5abd762fbefea7067794cbc1222b3c380` |
| 6 | python | passed | solution_verified_numerical | `256799054d6dc58640e0a54362a3215468c0b3ed1dc5469379b073fbf10e8fef` |

- Fence1: Flare independent atom-carbon versus native CO2 within1e-6kg/day, imposed20% split mass1e-6kg/hr and recovery compressor enthalpy-power1e-5 relative.

- Fence2: DryCO2-rich five-pressure flashes: positive finite density, phase-composition reconstruction1e-7, x sums1e-8. No transport safety or phase-envelope validation.

- Fence3: CO2/oil single-flash mixture positive density and composition sum1e-8. Does not determine multicontact MMP or recovery.

- Fence4: CPA syngas conditioning: total product mass1e-7, whole-flow enthalpy plus shaft/cooler duty1e-5 relative; H2 component mass below mixture mass and mixture purity<99%. No reformer/PSA/capture claimed.

- Fence5: Native electrolyzer at etaFaradaic1:2mol/sH2 and1mol/sO2, atom balances1e-9mol/s, electrical power2F V nH2 within1e-6W, reaction-plus-rejected-heat1e-3 relative and52<SEC<54kWh/kg.

- Fence6: Exact literal execution with supplementary numerical/physical/software solution checks; not field calibration.

## Global qualification limits

- A successful literal execution is distinct from numerical conservation, an independent benchmark, experimental model validation and design compliance. Per-fence classifications enforce that distinction.
- Definitions, configuration and reporting are explicitly inventoried separately from numerical calculations. Every numerical calculation requires its own exact-source passing solution proof; rejected native candidates remain diagnostics and are not accepted designs.
- Examples share previous chapter definitions in a fresh JVM. Java fragments execute in a chapter-scoped JShell fixture; Java8 source compatibility was reviewed, but each fragment is not a separately compiled Java8 application.
- Assertions are recorded with code hashes; coverage is the exercised inputs and branches only. Assertions inside functions support acceptance only when the mapped example actually calls those functions.
- None of this review establishes installed equipment performance, contractual product acceptance, relief/safety-system adequacy, live historian accuracy, environmental permitting, fiscal advice or full-field reservoir calibration.
- The parent release owns legacy/generated quantitative asset replacement and104 notebook figure integrations. Whole-manuscript hashes may change through these audited editorial operations while executable-fence hashes remain fixed.
- 89 benchmark comparisons, including18 independent NIST comparisons, belong to the separate notebook benchmark dossier; they are not89 independent experimental validations of each manuscript example.

## Reproducibility

Run `devtools/summarize_optimization_verification.py` to refresh the exact-code execution gate, then run `devtools/summarize_optimization_scientific_review.py` with the selected bundled Python runtime. The latter copies current literal numerical records into `verification/scientific_revision/optimization_evidence/` and writes this report plus the complete machine-readable per-fence ledger. It never reruns simulations or infers physical acceptance from execution alone.

Primary references requested for the book are in `optimization_refs.bib`; exact metadata corrections and primary-source URLs are recorded in the JSON. The root release combines these with its bibliographic audit and source index.
