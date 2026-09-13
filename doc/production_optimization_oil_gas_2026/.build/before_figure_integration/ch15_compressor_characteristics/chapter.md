# Compressor Characteristics and Performance Curves

**Running the examples.** Start the source-workspace Python session described in Chapter 1, then run this chapter's Python blocks in reading order. Java blocks form a separate sequence using the same NeqSim build; carry forward objects from preceding Java blocks. The release execution records are in `verification/`; a successful run establishes API compatibility, while physical validation also requires the checks discussed in the text.

<!-- Chapter metadata -->
<!-- Notebooks: 01_compressor_curves.ipynb, 02_surge_analysis.ipynb, 03_off_design_performance.ipynb, 04_parallel_operation.ipynb, 05_field_monitoring.ipynb -->
<!-- Estimated pages: 35 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Interpret compressor performance maps (head, efficiency, and power vs. flow)
2. Define and calculate surge, stonewall, and the stable operating envelope
3. Apply fan laws and affinity laws for speed variation analysis
4. Convert between actual and reduced (referred) conditions
5. Generate compressor curves from a single design point using NeqSim
6. Correct performance curves for off-design gas composition and suction conditions
7. Model compressor maps in NeqSim using CompressorChart and CompressorCurve
8. Analyze parallel and series compressor operation
9. Implement field performance monitoring for efficiency degradation and fouling detection
10. Use compressor curves for production optimization

## 15.1 Introduction

The previous chapter covered the fundamental thermodynamics of gas compression. This chapter focuses on the detailed characterization of centrifugal compressor performance through performance maps — the essential tool for understanding how a compressor behaves across its operating range.

A compressor performance map is not just a manufacturer's data sheet — it is the key interface between the rotating equipment engineer and the process engineer. The map determines what the compressor can deliver at any operating condition, how efficiently it operates, where its stability limits lie, and how it responds to changes in process conditions. For production optimization, the compressor map is arguably the single most important piece of equipment data.

Understanding compressor maps is essential because:

- **Production rate** is limited by compressor capacity at the stonewall (choke) limit
- **Turndown** is limited by the surge line
- **Energy consumption** depends on the efficiency at the actual operating point
- **Equipment life** depends on how close the operating point is to surge
- **Optimization** requires accurate prediction of compressor response to changed conditions

This chapter provides a comprehensive treatment of compressor performance characterization, from the fundamental theory of performance maps through practical applications in production optimization, including detailed NeqSim implementation examples.

![Typical centrifugal compressor performance map showing head vs. flow curves at different speeds](figures/compressor_map_overview.png)

*Figure 15.1: Centrifugal compressor performance map showing polytropic head vs. actual inlet volume flow for multiple speed lines. The surge line (left boundary), stonewall line (right boundary), and constant efficiency contours define the operating envelope.*

## 15.2 Performance Map Fundamentals

### 15.2.1 Head vs. Flow Curves

The primary representation of centrifugal compressor performance is the head vs. flow diagram. For each rotational speed, a curve shows how the polytropic head varies with volumetric flow rate:

- **At low flow** (near surge): Head is at or near maximum, but flow is unstable
- **At design point**: Optimal balance of head and flow with peak efficiency
- **At high flow** (stonewall/choke): Head drops rapidly as internal velocities approach Mach 1

The head produced by an impeller is fundamentally determined by the change in angular momentum of the gas (Euler's turbomachinery equation):

$$H_{\text{Euler}} = U_2 C_{u2} - U_1 C_{u1}$$

where $U$ is the impeller tip speed (m/s), $C_u$ is the tangential component of absolute gas velocity, and subscripts 1 and 2 refer to impeller inlet and outlet.

For a centrifugal compressor with radial inlet ($C_{u1} = 0$) and backward-curved blades:

$$H_{\text{Euler}} = U_2 C_{u2} = U_2 (U_2 - C_{m2} \cot \beta_2)$$

where $C_{m2}$ is the meridional (radial) velocity at the impeller outlet and $\beta_2$ is the blade exit angle.

This equation reveals that:
- Head increases with tip speed ($U_2$) — hence the benefit of high rotational speed
- Head decreases with increasing flow ($C_{m2}$ increases with flow) — hence the negative slope of the head-flow curve
- The blade angle $\beta_2$ determines the curve steepness

### 15.2.2 Efficiency vs. Flow Curves

The polytropic efficiency varies across the operating envelope, typically reaching a peak at or near the design point:

$$\eta_p = \frac{H_p}{H_{\text{actual}}} = \frac{H_p}{H_{\text{Euler}} \times \text{slip factor} - \text{losses}}$$

Efficiency losses include:

| Loss Mechanism | Typical Magnitude | Flow Dependence |
|----------------|-------------------|-----------------|
| Incidence loss | 1–3% | Increases away from design |
| Friction loss | 2–5% | Proportional to flow$^2$ |
| Diffuser loss | 2–4% | Complex dependency |
| Leakage loss | 1–3% | Relatively constant |
| Disk friction | 1–2% | Proportional to speed$^3$ |
| Recirculation | 0–5% | Increases at low flow |

*Table 15.1: Sources of efficiency loss in centrifugal compressors and their approximate magnitudes.*

The efficiency vs. flow curve has a characteristic parabolic shape with a peak at or near the design flow rate. The best efficiency point (BEP) is defined as the flow rate at which polytropic efficiency reaches its maximum for a given speed.

### 15.2.3 Power vs. Flow Curves

The absorbed power (gas power) varies across the operating range:

$$\dot{W} = \dot{m} \cdot \frac{H_p}{\eta_p}$$

Since head decreases with flow while mass flow increases, the power curve typically:
- Increases monotonically from surge to choke for low-molecular-weight gases
- May peak and decrease at high flow for heavy gases
- Driver power rating must accommodate the maximum power demand across the expected operating range

## 15.3 Surge and Stonewall

### 15.3.1 Surge Phenomenon

Surge is the most critical stability limit for centrifugal compressors. It occurs when the flow rate decreases below the minimum stable value at which the compressor can maintain the required head. At this point, the gas pressure downstream exceeds what the compressor can produce, and flow reversal occurs.

The surge cycle consists of:

1. **Flow reduction** below the surge point
2. **Flow reversal** — gas flows backward through the compressor
3. **Depressurization** of the discharge system
4. **Flow re-establishment** in the forward direction
5. **Cycle repeats** if the operating conditions remain below the surge point

The surge frequency is typically 0.5–5 Hz, depending on the system volume and compressor characteristics.

Surge is destructive:
- Violent axial thrust reversals damage bearings
- High gas velocities during flow reversal cause impeller erosion
- Temperature excursions from repeated compression–decompression cycles
- Vibration can cause shaft fatigue, seal damage, and foundation damage

### 15.3.2 Surge Line Characterization

The surge line connects the minimum stable flow points at each speed, forming the left boundary of the operating envelope. The surge line can be characterized as:

$$H_{\text{surge}} = a \cdot Q_{\text{surge}}^2 + b$$

where $a$ and $b$ are constants determined from compressor test data or manufacturer's curves.

More commonly, surge is expressed in terms of the surge flow ratio:

$$\text{SFR} = \frac{Q_{\text{surge}}}{Q_{\text{design}}}$$

Typical surge flow ratios for centrifugal compressors:

| Impeller Type | SFR at Design Speed |
|---------------|---------------------|
| Backward-curved (2D) | 0.55–0.70 |
| Backward-curved (3D) | 0.50–0.60 |
| Radial | 0.45–0.55 |
| Mixed flow | 0.60–0.75 |

*Table 15.2: Typical surge flow ratios (ratio of surge flow to design flow) for different impeller types.*

### 15.3.3 Stonewall (Choke)

Stonewall occurs when gas velocity at any point in the compressor (typically the impeller throat or the diffuser throat) reaches sonic velocity ($\text{Ma} = 1$). Beyond this point, no additional flow can pass through the restricted area — the compressor is choked.

At stonewall:
- Head drops to zero or near zero
- Flow rate reaches maximum
- Efficiency drops severely
- Gas heating increases due to shock losses

The stonewall flow depends on the gas molecular weight and temperature. For the same physical machine, a heavier gas (higher MW) chokes at a lower volumetric flow rate because the sonic velocity is lower:

$$c_{\text{sonic}} = \sqrt{\frac{\gamma Z R T}{MW}}$$

### 15.3.4 Operating Envelope

The complete operating envelope is bounded by:
- **Left**: Surge line (minimum flow for stable operation)
- **Right**: Stonewall line (maximum flow capacity)
- **Top**: Maximum speed line (mechanical/driver limit)
- **Bottom**: Minimum speed line (below which head is insufficient)
- **Power limit**: Maximum driver power curve (may be binding at high flow/speed)

![Operating envelope with surge, stonewall, speed lines, and constant efficiency contours](figures/operating_envelope.png)

*Figure 15.2: Complete compressor operating envelope showing surge line, stonewall line, speed lines, constant efficiency contours, and the operating window. The anti-surge control line (ASCL) is set at a safety margin to the right of the surge line.*

## 15.4 Reduced (Referred) Conditions

### 15.4.1 Why Reduced Conditions?

Compressor performance maps are typically generated from factory acceptance tests at specific suction conditions (temperature, pressure, gas composition). In the field, suction conditions vary continuously due to:

- Seasonal ambient temperature changes
- Reservoir depletion (changing gas composition, GOR)
- Process upsets and operating mode changes
- Compressor fouling and degradation

To apply the manufacturer's map at field conditions, the operating point must be converted to **reduced (referred) conditions** that correspond to the map reference conditions.

### 15.4.2 Reduced Parameters

The key reduced parameters are defined as:

**Reduced speed**:

$$N_{\text{red}} = N \times \sqrt{\frac{Z_{\text{ref}} R_{\text{ref}} T_{\text{ref}}}{Z_{\text{act}} R_{\text{act}} T_{\text{act}}}} = N \times \sqrt{\frac{(ZRT/MW)_{\text{ref}}}{(ZRT/MW)_{\text{act}}}}$$

**Reduced flow (actual inlet volume flow)**:

$$Q_{\text{red}} = Q_{\text{act}} \times \frac{N_{\text{red}}}{N}$$

**Reduced head**:

$$H_{\text{red}} = H_{\text{act}} \times \frac{(ZRT/MW)_{\text{ref}}}{(ZRT/MW)_{\text{act}}}$$

These transformations ensure that the Mach number and flow coefficient are preserved, which are the dimensionless groups that determine the compressor's aerodynamic behavior.

### 15.4.3 Simplified Correction Factors

For small deviations from reference conditions, the correction can be expressed as multiplicative factors:

$$\frac{H_{\text{act}}}{H_{\text{ref}}} = \frac{(ZRT/MW)_{\text{act}}}{(ZRT/MW)_{\text{ref}}}$$

$$\frac{Q_{\text{act}}}{Q_{\text{ref}}} = \frac{N_{\text{act}}}{N_{\text{ref}}} \times \frac{1}{\sqrt{(ZRT/MW)_{\text{act}} / (ZRT/MW)_{\text{ref}}}}$$

$$\frac{W_{\text{act}}}{W_{\text{ref}}} = \frac{\dot{m}_{\text{act}}}{\dot{m}_{\text{ref}}} \times \frac{H_{\text{act}}}{H_{\text{ref}}} \times \frac{\eta_{\text{ref}}}{\eta_{\text{act}}}$$

These corrections are important because they quantify the effect of gas composition changes. As reservoir pressure declines and GOR increases, the gas becomes lighter (lower MW), which means:
- Head produced at the same speed increases (beneficial for pressure ratio)
- Volumetric flow to choke increases (beneficial for capacity)
- But surge flow also shifts, potentially narrowing the operating window

## 15.5 Fan Laws and Affinity Laws

### 15.5.1 The Fan Laws

The fan laws (also called similarity laws or affinity laws) relate the performance of a centrifugal compressor at one speed to its performance at a different speed, assuming dynamically similar conditions:

$$\frac{Q_2}{Q_1} = \frac{N_2}{N_1}$$

$$\frac{H_2}{H_1} = \left(\frac{N_2}{N_1}\right)^2$$

$$\frac{W_2}{W_1} = \left(\frac{N_2}{N_1}\right)^3$$

where $Q$ is volumetric flow, $H$ is head, $W$ is power, and $N$ is rotational speed.

These laws are exact for an ideal (incompressible) fluid and provide an excellent approximation for gas compressors at moderate pressure ratios (Mach number < 0.8). At high Mach numbers, the deviation from the fan laws increases due to compressibility effects.

### 15.5.2 Speed Lines on the Performance Map

Each speed line on the compressor map is related to the adjacent speed lines through the fan laws. Starting from a single known speed line (e.g., 100% speed from the factory test), speed lines at other speeds can be generated:

For a point $(Q_1, H_1)$ on the reference speed line at speed $N_1$, the corresponding point on the speed line at $N_2$ is:

$$Q_2 = Q_1 \times \frac{N_2}{N_1}$$

$$H_2 = H_1 \times \left(\frac{N_2}{N_1}\right)^2$$

This mapping transforms the entire speed line, including the surge point. The surge line itself follows the fan law parabola:

$$H_{\text{surge}} \propto Q_{\text{surge}}^2$$

or more precisely, the surge points at different speeds lie on a parabola through the origin.

### 15.5.3 Limitations of Fan Laws

The fan laws assume:
- **Geometric similarity**: The same physical machine
- **Dynamic similarity**: Same flow coefficient and Mach number
- **Negligible Reynolds number effects**: Valid for fully turbulent flow

Deviations occur when:
- Mach number exceeds about 0.8 (compressibility effects)
- Flow coefficient is very different from design (incidence effects)
- Gas properties change significantly (MW, $\gamma$, $Z$)
- The machine is operating near surge or choke

For production optimization applications, the fan laws provide a practical engineering tool for speed variation analysis, typically accurate to within 2–3% for speed variations of ±20% from design.

## 15.6 Compressor Performance Curves — Detailed Theory

### 15.6.1 Dimensionless Performance Parameters

The performance of a centrifugal compressor is governed by three dimensionless groups:

**Flow coefficient**:

$$\phi = \frac{Q}{N D^3}$$

where $Q$ is actual volume flow (m$^3$/s), $N$ is speed (rev/s), and $D$ is impeller diameter (m).

**Head coefficient (work coefficient)**:

$$\psi = \frac{H}{N^2 D^2}$$

where $H$ is polytropic head (J/kg).

**Machine Mach number**:

$$\text{Ma}_U = \frac{U_2}{c_{\text{sonic}}} = \frac{\pi N D}{\sqrt{\gamma Z R T / MW}}$$

For geometrically similar machines, the performance in terms of $\psi$ vs. $\phi$ is a single curve, independent of speed, diameter, and gas properties (within the limitations of dynamic similarity). This is the fundamental basis for:
- Scaling compressor designs to different sizes
- Predicting performance at different speeds
- Correcting for different gas compositions

### 15.6.2 Generating Curves from a Design Point

In many practical situations, only the design point is known (from the manufacturer's data sheet), and a complete performance curve must be generated for simulation purposes. The procedure is:

**Step 1**: From the design point, calculate the design flow coefficient $\phi_d$ and head coefficient $\psi_d$.

**Step 2**: Use a generic (non-dimensional) performance curve that represents the impeller type. Typical curve shapes:

$$\psi(\phi) = \psi_d \left[a_0 + a_1 \left(\frac{\phi}{\phi_d}\right) + a_2 \left(\frac{\phi}{\phi_d}\right)^2 + a_3 \left(\frac{\phi}{\phi_d}\right)^3\right]$$

where the coefficients $a_0, a_1, a_2, a_3$ define the curve shape. A typical set for a backward-curved impeller:

$$a_0 = 0.5, \quad a_1 = 0.8, \quad a_2 = -0.3, \quad a_3 = 0.0$$

(These are approximate — actual coefficients depend on the specific impeller design.)

**Step 3**: Generate speed lines by applying the fan laws to the design-speed curve.

**Step 4**: Generate efficiency curves. A common model for efficiency variation:

$$\eta_p(\phi) = \eta_{p,d} \left[1 - c_1 \left(\frac{\phi - \phi_d}{\phi_d}\right)^2\right]$$

where $c_1 \approx 0.5$–$1.5$ determines how rapidly efficiency degrades away from the BEP.

### 15.6.3 Surge Line Prediction

The surge line can be approximated if the surge flow ratio at the design speed is known. For each speed line, the surge point is located at a characteristic flow coefficient $\phi_{\text{surge}}$:

$$\phi_{\text{surge}} \approx \text{SFR} \times \phi_d$$

At different speeds, the surge points trace a parabola:

$$H_{\text{surge}} = K_{\text{surge}} \cdot Q_{\text{surge}}^2$$

where $K_{\text{surge}}$ is determined from the design-speed surge point.

## 15.7 Anti-Surge Control

### 15.7.1 Anti-Surge Control System

The anti-surge control system (ASCS) prevents the compressor from operating below the surge line. The key components are:

1. **Surge controller**: Calculates the proximity to surge based on measured variables
2. **Anti-surge control valve (ASCV)**: A fast-acting recycle valve that opens to increase compressor throughput when approaching surge
3. **Transmitters**: Suction pressure, discharge pressure, suction temperature, and flow measurement

### 15.7.2 Surge Parameter

The surge controller uses a calculated surge parameter to determine proximity to the surge line. Common formulations:

**Pressure ratio vs. corrected flow**:

$$\text{SP} = \frac{P_d/P_s}{\left(P_d/P_s\right)_{\text{surge at same } Q_{\text{corr}}}}$$

**Polytropic head vs. actual flow**:

$$\text{SP} = \frac{H_p}{H_{p,\text{surge}}(Q_{\text{act}})}$$

The anti-surge control line (ASCL) is set at a margin to the right of the surge line:

$$Q_{\text{ASCL}} = Q_{\text{surge}} \times (1 + \text{SM}/100)$$

where SM is the surge margin (typically 10–15%).

### 15.7.3 Anti-Surge Valve Sizing

The anti-surge valve must be sized to handle the maximum recycle flow needed to keep the compressor above the surge line at any operating condition. The critical condition is usually minimum process flow at maximum speed:

$$Q_{\text{recycle}} = Q_{\text{surge}}(N_{\text{max}}) - Q_{\text{process,min}}$$

The valve must also be fast enough to respond to rapid load changes. The full-stroke time should be less than 2 seconds, and the stroking time from closed to 50% open should be less than 1 second.

### 15.7.4 Recycle Cooling

Gas recycled through the anti-surge valve heats up due to compression and valve friction. If the recycle gas is not cooled before returning to suction, the suction temperature increases progressively (thermal runaway), which:

- Reduces compressor head (higher suction temperature)
- Increases power consumption
- Can lead to machinery overheating

A recycle cooler (often the compressor after-cooler) is essential for any anti-surge system that may operate for extended periods.

### 15.7.5 Hot Bypass vs. Cold Recycle

Two alternative recycle configurations are used for anti-surge protection, each with distinct advantages:

| Feature | Hot Bypass (Hot Gas Recycle) | Cold Recycle (Cooled Recycle) |
|---------|---------------------------|----------------------------|
| Configuration | Recycle directly from discharge to suction (no cooling) | Recycle through after-cooler before returning to suction |
| Response time | Very fast (short piping run) | Slower (longer piping, cooler residence time) |
| Suction temperature | Increases progressively | Maintained near design |
| Extended operation | Limited — thermal runaway risk | Indefinite — thermally stable |
| Piping cost | Lower (short, direct) | Higher (includes cooler) |
| Power penalty | Higher (hot gas reduces density) | Lower (cool gas at design density) |
| Typical application | Emergency protection, brief events | Normal turndown, extended low-load |
| Risk | Overheating if sustained > 5–10 minutes | Cooler fouling, longer response |

Most modern compressor systems use a **combined approach**: a fast-acting hot bypass valve for rapid surge protection (opens in < 1 second) combined with a slower cold recycle path through the after-cooler for sustained low-load operation. The hot bypass valve closes automatically once the cold recycle flow stabilizes the operating point.

### 15.7.6 Capacity Control Methods

When production requirements fall below the compressor's design throughput, capacity control methods are used to reduce the compressor output while maintaining stable operation above the surge line:

**Variable Speed Drive (VSD):**

The most energy-efficient method. Reducing speed shifts the entire performance map according to the fan laws (Section 15.5): flow scales linearly with speed, head scales with speed squared, and power scales with speed cubed. The result is that power reduction at part-load is very favorable:

$$
\frac{W_{\text{reduced}}}{W_{\text{design}}} = \left(\frac{N_{\text{reduced}}}{N_{\text{design}}}\right)^3
$$

At 80% speed, power consumption drops to approximately 51% of design. VSDs add cost (30–50% premium over fixed-speed motors) and complexity but are strongly preferred for compressors with variable load profiles.

**Inlet Guide Vanes (IGVs):**

Adjustable vanes at the compressor inlet impart a pre-swirl to the gas, shifting the head-flow curve. Positive pre-swirl (in the direction of impeller rotation) reduces head and flow at constant speed, effectively moving the surge point to the left and allowing operation at lower flow rates without recycling.

IGVs provide reasonable efficiency at part-load (70–80% of design flow) but become increasingly inefficient below 70% flow. They are commonly used on fixed-speed centrifugal compressors where a VSD is not practical.

**Suction Throttling:**

A control valve at the compressor suction reduces the suction pressure, which increases the volumetric flow entering the compressor (for the same mass flow), moving the operating point to the right on the performance map. This prevents surge but at a significant energy penalty — the compressor does additional work to overcome the throttling pressure drop.

Suction throttling is the simplest capacity control method but the least efficient. It is typically used only as a last resort when neither VSD nor IGVs are available.

| Method | Efficiency at 70% Load | Capital Cost | Complexity | Best For |
|--------|----------------------|-------------|-----------|---------|
| Variable speed | 85–90% of design | High | Moderate | Variable-load, large machines |
| Inlet guide vanes | 75–85% of design | Moderate | Low | Fixed-speed, moderate turndown |
| Suction throttle | 60–70% of design | Low | Low | Simple systems, small machines |
| Recycle (hot bypass) | 50–60% of design | Low | Low | Emergency protection only |

In practice, many offshore compressor systems combine VSD with anti-surge recycle: the VSD handles normal load variation, while the recycle system provides protection during rapid transients (slug arrival, well trip, emergency shutdown).

## 15.8 Off-Design Performance

### 15.8.1 Gas Composition Changes

As reservoir pressure declines, the produced gas composition changes:
- GOR increases (more gas per barrel of oil)
- Gas becomes leaner (lower MW) as heavier components condense in the reservoir
- CO$_2$ concentration may change
- Water vapor content changes

These composition changes affect the compressor performance through changes in:

| Gas Property | Effect on Compressor |
|-------------|---------------------|
| MW decrease | Head increases, capacity increases, surge shifts right |
| $\gamma$ decrease | Head coefficient changes, efficiency may change |
| $Z$ increase | Head increases (more ideal gas behavior) |
| $T$ increase | Volumetric flow increases, head decreases per unit of pressure |

*Table 15.3: Effect of gas property changes on centrifugal compressor performance.*

### 15.8.2 Curve Shifting Procedure

To predict compressor performance at new gas conditions, the following procedure is used:

1. Convert the operating point to reduced conditions using the reference gas properties
2. Look up the reduced head and efficiency from the map
3. Convert back to actual conditions using the actual gas properties

The shift in the performance map can be visualized as:
- **Lighter gas** (lower MW): Map shifts to the right and up (more head, more flow)
- **Heavier gas** (higher MW): Map shifts to the left and down (less head, less flow)
- **Higher temperature**: Map shifts to the right (more volume flow for same mass flow)

### 15.8.3 Volume Ratio and Real Gas Effects

The polytropic volume exponent $n_v$ (different from the polytropic temperature exponent $n$) determines the volume ratio across the compressor:

$$\frac{v_2}{v_1} = \left(\frac{P_1}{P_2}\right)^{1/n_v}$$

For real gases, $n_v \neq n$ and both deviate from the ideal gas value. The volume ratio affects the internal flow path and impeller loading, which in turn affects efficiency and surge characteristics.

NeqSim calculates these real gas properties directly from the equation of state, providing accurate predictions even at high pressures where real gas effects are significant.

## 15.9 Multi-Section Compressors

### 15.9.1 Tandem Arrangements

Large compression duties often use multi-section compressors with two or more impeller groups (sections) in a single casing, sometimes with intercooling between sections (side-stream or external). Each section has its own performance map.

The overall performance is the combination of individual section performances:

$$H_{\text{total}} = \sum_i H_i(Q_i)$$

$$\dot{W}_{\text{total}} = \sum_i \frac{\dot{m}_i H_i}{\eta_{p,i}}$$

Sidestream injection between sections changes the mass flow and composition for downstream sections, requiring careful matching of section performances.

### 15.9.2 Parallel Operation

Parallel compressors share a common suction and discharge header. The combined performance is:

$$Q_{\text{total}} = \sum_j Q_j(H_{\text{common}})$$

at a common discharge pressure (head). The flow distributes among the machines such that all operate at the same discharge pressure.

**Challenges of parallel operation**:
- Surge risk if one machine trips (remaining machines see increased flow, but discharge pressure drops, potentially pushing them toward surge)
- Unequal load sharing if machines have different characteristics
- Start-up sequencing to avoid surge

### 15.9.3 Series Operation

Series compressors operate with the discharge of one feeding the suction of the next. The combined performance is:

$$H_{\text{total}} = \sum_j H_j(Q_j)$$

at a common mass flow rate. Each machine operates at its own pressure level.

## 15.10 API 617 Testing

### 15.10.1 Factory Acceptance Test

API 617 (8th Edition) specifies the requirements for centrifugal compressor testing. The factory acceptance test (FAT) verifies that the compressor meets its guaranteed performance at the specified conditions.

Key test measurements:
- Suction temperature and pressure
- Discharge temperature and pressure
- Flow rate (orifice plate or venturi)
- Speed
- Power (torque meter or heat balance)

The test gas may differ from the design gas. In such cases, the results must be corrected to design conditions using the reduced parameter method.

### 15.10.2 Acceptance Criteria

API 617 specifies the following tolerances:

| Parameter | Tolerance |
|-----------|-----------|
| Polytropic head | ≥ specified value minus 2% |
| Polytropic efficiency | ≥ specified value minus 2 points |
| Power | ≤ specified value plus 4% |
| Surge flow | ≤ specified value |

*Table 15.4: API 617 performance acceptance criteria for centrifugal compressors.*

## 15.11 Field Performance Monitoring

### 15.11.1 Why Monitor?

Compressor performance degrades over time due to:
- **Fouling**: Deposits on impellers and diffusers (hydrocarbon condensation, corrosion products, salt)
- **Erosion**: Wear from entrained solids or liquid droplets
- **Seal degradation**: Increased internal leakage
- **Bearing wear**: Increased friction losses

These effects reduce head, efficiency, and capacity, ultimately limiting production. Early detection of degradation allows timely maintenance intervention before the impact becomes severe.

### 15.11.2 Performance Indicators

Key performance indicators for field monitoring:

**Polytropic head deviation**:

$$\Delta H_p = \frac{H_{p,\text{actual}} - H_{p,\text{expected}}}{H_{p,\text{expected}}} \times 100\%$$

**Polytropic efficiency deviation**:

$$\Delta \eta_p = \eta_{p,\text{actual}} - \eta_{p,\text{expected}}$$

**Power deviation**:

$$\Delta W = \frac{W_{\text{actual}} - W_{\text{expected}}}{W_{\text{expected}}} \times 100\%$$

The "expected" values come from the manufacturer's performance map corrected to actual suction conditions.

### 15.11.3 Degradation Patterns

| Degradation Type | Head Effect | Efficiency Effect | Typical Onset |
|-----------------|------------|------------------|---------------|
| Fouling | −2 to −5% | −1 to −3 pts | Gradual (months) |
| Erosion | −3 to −10% | −2 to −5 pts | Gradual (years) |
| Seal leakage | −1 to −3% | −1 to −2 pts | Gradual (months) |
| Bearing wear | 0% | −0.5 to −1 pt | Gradual (years) |
| Surge damage | Variable | Variable | Sudden (event) |

*Table 15.5: Typical performance degradation patterns for centrifugal compressors.*

### 15.11.4 Monitoring Methodology

A robust field monitoring program includes:

1. **Continuous data acquisition**: Suction T, P; discharge T, P; flow rate; speed; vibration
2. **Performance calculation**: Convert raw data to polytropic head and efficiency
3. **Condition correction**: Correct to reference conditions to isolate degradation from operating point changes
4. **Trending**: Track performance indicators over time with statistical filtering
5. **Alarm thresholds**: Alert when deviations exceed predefined limits (typically −3% head, −2 points efficiency)
6. **Root cause analysis**: Distinguish between fouling (gradual, recoverable by washing) and erosion (gradual, permanent)

## 15.12 Compressor Maps in Production Optimization

### 15.12.1 The Compressor as a Constraint

In production optimization, compressors are often the binding constraint that limits production rate. The compressor operating point is determined by the intersection of the compressor characteristic (head vs. flow) with the system resistance curve (pressure drop vs. flow):

$$H_{\text{compressor}}(Q) = H_{\text{system}}(Q) = \frac{P_{\text{discharge}} - P_{\text{suction}}}{\rho \cdot g} + f(Q^2)$$

As process conditions change (reservoir pressure decline, well interventions, equipment changes), the system curve shifts, and the operating point moves along the compressor curve. Understanding this interaction is essential for predicting:

- Maximum production rate (stonewall limit)
- Minimum stable production rate (surge limit)
- Energy consumption at each production rate
- Impact of adding wells, changing separator pressures, or modifying the process

### 15.12.2 Speed Selection for Optimization

Variable speed operation provides the most efficient way to match compressor output to process demand. The optimal speed at any production rate minimizes power consumption while meeting the required discharge pressure:

$$N_{\text{optimal}} = N_{\text{ref}} \times \sqrt{\frac{H_{\text{required}}}{H_{\text{ref}}(\phi)}}$$

NeqSim's compressor curve functionality allows this optimization to be performed automatically within the process simulation framework.

## 15.13 NeqSim Implementation

### 15.13.1 CompressorChart and CompressorCurve Classes

NeqSim provides two main classes for modeling compressor performance maps:

- **`CompressorChart`**: Represents the complete compressor map with multiple speed lines
- **`CompressorCurve`**: Represents a single performance curve (head vs. flow, efficiency vs. flow, etc.)

The `CompressorChart` is attached to a `Compressor` object and used during process simulation to determine the actual operating point based on suction conditions and discharge pressure.

### 15.13.2 Setting Up Compressor Curves

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Define gas
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 30.0, 5.0)
gas.addComponent("nitrogen", 0.5)
gas.addComponent("CO2", 2.0)
gas.addComponent("methane", 82.0)
gas.addComponent("ethane", 7.0)
gas.addComponent("propane", 4.5)
gas.addComponent("i-butane", 1.0)
gas.addComponent("n-butane", 2.0)
gas.addComponent("n-pentane", 0.5)
gas.addComponent("n-hexane", 0.5)
gas.setMixingRule("classic")

# Create feed stream
feed = jneqsim.process.equipment.stream.Stream("Compressor Inlet", gas)
feed.setFlowRate(16000.0, "kg/hr")
feed.setTemperature(30.0, "C")
feed.setPressure(5.0, "bara")

# Create compressor
compressor = jneqsim.process.equipment.compressor.Compressor(
    "1st Stage Compressor", feed)
compressor.setOutletPressure(15.0)

# Set up compressor chart with speed lines
# Flow values in m3/hr (actual inlet volume)
# Head values in kJ/kg (polytropic head)
# Efficiency values as fraction

# Speed line at 100% (design speed, e.g. 11500 rpm)
speed100_flow = [3000.0, 3500.0, 4000.0, 4500.0, 5000.0, 5500.0]
speed100_head = [120.0, 115.0, 108.0, 98.0, 85.0, 70.0]
speed100_eff  = [0.72, 0.76, 0.80, 0.79, 0.75, 0.68]

# Speed line at 90%
speed90_flow = [2700.0, 3150.0, 3600.0, 4050.0, 4500.0, 4950.0]
speed90_head = [97.0, 93.0, 87.0, 79.0, 69.0, 57.0]
speed90_eff  = [0.71, 0.75, 0.79, 0.78, 0.74, 0.67]

# Speed line at 80%
speed80_flow = [2400.0, 2800.0, 3200.0, 3600.0, 4000.0, 4400.0]
speed80_head = [77.0, 74.0, 69.0, 63.0, 55.0, 45.0]
speed80_eff  = [0.70, 0.74, 0.78, 0.77, 0.73, 0.66]

# Get the compressor chart
chart = compressor.getCompressorChart()

# setCurves also fits the reduced head and efficiency functions.
# addCurve alone leaves the default polynomial chart uninitialized.
feed.run()
conditions = [feed.getFluid().getMolarMass() * 1000.0,
              feed.getTemperature("K"), feed.getPressure("bara"),
              feed.getFluid().getPhase("gas").getZ()]
chart.setCurves(conditions, [11500.0, 10350.0, 9200.0],
                [speed100_flow, speed90_flow, speed80_flow],
                [speed100_head, speed90_head, speed80_head],
                [[v * 100.0 for v in row] for row in
                 [speed100_eff, speed90_eff, speed80_eff]])

# Set surge curve (flow vs head at surge)
surge_flow = [2400.0, 2700.0, 3000.0]
surge_head = [77.0, 97.0, 120.0]
SafeSplineSurgeCurve = jneqsim.process.equipment.compressor.SafeSplineSurgeCurve
chart.setSurgeCurve(SafeSplineSurgeCurve(surge_flow, surge_head))

# Enable chart-based calculation
chart.setHeadUnit("kJ/kg")
chart.setUseCompressorChart(True)
compressor.setSpeed(11500.0)

# Build and run process
process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(compressor)
process.run()

# Report results
print("=== Compressor with Performance Chart ===")
print(f"Suction:    {feed.getTemperature('C'):.1f} C / "
      f"{feed.getPressure():.1f} bara")
print(f"Discharge:  "
      f"{compressor.getOutletStream().getTemperature('C'):.1f} C / "
      f"{compressor.getOutletStream().getPressure():.1f} bara")
print(f"Power:      {compressor.getPower()/1e3:.1f} kW")
print(f"Poly. eff:  {compressor.getPolytropicEfficiency()*100:.1f}%")
print(f"Poly. head: {compressor.getPolytropicFluidHead():.1f} kJ/kg")
```

### 15.13.3 Generating Curves from Design Point

When only the design point is available, NeqSim can generate approximate performance curves using the fan laws and assumed curve shapes:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Define gas and feed
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 35.0, 3.0)
gas.addComponent("methane", 85.0)
gas.addComponent("ethane", 6.0)
gas.addComponent("propane", 4.0)
gas.addComponent("n-butane", 2.0)
gas.addComponent("CO2", 2.0)
gas.addComponent("nitrogen", 1.0)
gas.setMixingRule("classic")

feed = jneqsim.process.equipment.stream.Stream("Feed", gas)
feed.setFlowRate(25000.0, "kg/hr")
feed.setTemperature(35.0, "C")
feed.setPressure(3.0, "bara")

# Create compressor with design-point specification
comp = jneqsim.process.equipment.compressor.Compressor(
    "Recompressor", feed)
comp.setOutletPressure(10.0)
comp.setPolytropicEfficiency(0.80)
comp.setUsePolytropicCalc(True)

# Run to get design point values
process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(comp)
process.run()

design_head = comp.getPolytropicFluidHead()  # kJ/kg
design_power = comp.getPower() / 1000.0  # kW

print("=== Design Point ===")
print(f"Head:   {design_head:.1f} kJ/kg")
print(f"Power:  {design_power:.0f} kW")
print(f"T_out:  {comp.getOutletStream().getTemperature('C'):.1f} C")

# Generate curves from design point using fan laws
# For multiple flow rates at design speed
import numpy as np

# Approximate head-flow curve using quadratic
# H(Q) = H_design * [1 + a*(Q/Q_d - 1) + b*(Q/Q_d - 1)^2]
# where a < 0 (head decreases with flow)

flow_design = feed.getFlowRate("Am3/hr")  # actual m3/hr
head_design = design_head

flows_pct = np.array([0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
flows_actual = flows_pct * flow_design

# Typical curve shape coefficients for backward-curved impeller
a_coeff = -0.3
b_coeff = -0.5

heads = head_design * (1 + a_coeff * (flows_pct - 1) +
                        b_coeff * (flows_pct - 1)**2)

# Efficiency curve (parabolic around design point)
eff_design = 0.80
eff_dropoff = 1.2  # How fast efficiency drops from BEP
effs = eff_design * (1 - eff_dropoff * (flows_pct - 1)**2)

print("\n=== Generated Performance Curve (100% Speed) ===")
print(f"{'Flow (m3/hr)':>14} {'Head (kJ/kg)':>14} {'Eff (%)':>10}")
print("-" * 42)
for q, h, e in zip(flows_actual, heads, effs):
    print(f"{q:>14.0f} {h:>14.1f} {e*100:>10.1f}")
```

### 15.13.4 Compressor Map Visualization

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import matplotlib.pyplot as plt
import numpy as np

# ============================================================
# Generate and Visualize a Complete Compressor Map
# ============================================================

# Design point parameters
flow_design = 4500.0   # m3/hr actual inlet volume
head_design = 105.0    # kJ/kg polytropic head
eff_design = 0.80      # polytropic efficiency
speed_design = 11500.0 # rpm

# Generate speed lines from 70% to 105% speed
speeds_pct = [0.70, 0.80, 0.90, 1.00, 1.05]
flow_fracs = np.linspace(0.60, 1.35, 20)

fig, axes = plt.subplots(2, 1, figsize=(12, 14), sharex=True)

# Head vs. Flow plot
ax1 = axes[0]
surge_flows_all = []
surge_heads_all = []

for spd in speeds_pct:
    flows = flow_fracs * flow_design * spd
    heads = head_design * spd**2 * (
        1 - 0.3 * (flow_fracs / spd - 1) -
        0.5 * (flow_fracs / spd - 1)**2)

    # Find surge point (approx at 65% of design flow for that speed)
    surge_idx = 2  # approximate
    surge_flows_all.append(flows[surge_idx])
    surge_heads_all.append(heads[surge_idx])

    label = f"{spd*100:.0f}% speed ({spd*speed_design:.0f} rpm)"
    ax1.plot(flows, heads, '-', linewidth=1.5, label=label)

# Surge line
ax1.plot(surge_flows_all, surge_heads_all, 'r--',
         linewidth=2.5, label='Surge Line')
ax1.fill_betweenx([0, max(surge_heads_all)*1.2],
                   0, min(surge_flows_all)*0.8,
                   alpha=0.1, color='red')

ax1.set_ylabel("Polytropic Head (kJ/kg)", fontsize=12)
ax1.set_title("Compressor Performance Map", fontsize=14)
ax1.legend(fontsize=9, loc='upper right')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, head_design * 1.3)

# Efficiency vs. Flow plot
ax2 = axes[1]

for spd in speeds_pct:
    flows = flow_fracs * flow_design * spd
    effs = eff_design * (
        1 - 1.2 * (flow_fracs / spd - 1)**2) * (
        1 - 0.02 * abs(spd - 1.0) / 0.1)

    label = f"{spd*100:.0f}% speed"
    ax2.plot(flows, effs * 100, '-', linewidth=1.5, label=label)

ax2.set_xlabel("Actual Inlet Volume Flow (m³/hr)", fontsize=12)
ax2.set_ylabel("Polytropic Efficiency (%)", fontsize=12)
ax2.set_title("Efficiency Map", fontsize=14)
ax2.legend(fontsize=9, loc='upper right')
ax2.grid(True, alpha=0.3)
ax2.set_ylim(50, 90)

plt.tight_layout()
plt.savefig("figures/compressor_map_complete.png", dpi=150,
            bbox_inches="tight")
plt.show()
```

![Complete compressor performance map with head and efficiency curves at multiple speeds](figures/compressor_map_complete.png)

*Figure 15.3: Generated compressor performance map showing (top) polytropic head vs. actual inlet volume flow at five speeds from 70% to 105% of design, with the surge line marked in red; and (bottom) polytropic efficiency vs. flow at the same speeds. The design point is at 100% speed, 4500 m$^3$/hr, with 80% polytropic efficiency.*

### 15.13.5 Parallel Compressor Operation

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# ============================================================
# Parallel Compressor Operation
# ============================================================

# Two compressors sharing a common suction and discharge header

# Define gas
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 30.0, 5.0)
gas.addComponent("methane", 85.0)
gas.addComponent("ethane", 6.0)
gas.addComponent("propane", 4.0)
gas.addComponent("n-butane", 2.0)
gas.addComponent("CO2", 2.0)
gas.addComponent("nitrogen", 1.0)
gas.setMixingRule("classic")

# Main feed (total flow to both compressors)
main_feed = jneqsim.process.equipment.stream.Stream("Total Feed", gas)
main_feed.setFlowRate(50000.0, "kg/hr")
main_feed.setTemperature(30.0, "C")
main_feed.setPressure(5.0, "bara")

# Split the flow between two compressors
splitter = jneqsim.process.equipment.splitter.Splitter(
    "Flow Splitter", main_feed, 2)
splitter.setSplitFactors([0.5, 0.5])  # Equal split

# Compressor A
comp_a = jneqsim.process.equipment.compressor.Compressor(
    "Compressor A", splitter.getSplitStream(0))
comp_a.setOutletPressure(15.0)
comp_a.setPolytropicEfficiency(0.80)
comp_a.setUsePolytropicCalc(True)

# Compressor B
comp_b = jneqsim.process.equipment.compressor.Compressor(
    "Compressor B", splitter.getSplitStream(1))
comp_b.setOutletPressure(15.0)
comp_b.setPolytropicEfficiency(0.78)  # Slightly different
comp_b.setUsePolytropicCalc(True)

# Merge discharge streams
mixer = jneqsim.process.equipment.mixer.Mixer("Discharge Mixer")
mixer.addStream(comp_a.getOutletStream())
mixer.addStream(comp_b.getOutletStream())

# Build and run
process = jneqsim.process.processmodel.ProcessSystem()
process.add(main_feed)
process.add(splitter)
process.add(comp_a)
process.add(comp_b)
process.add(mixer)
process.run()

# Report
print("=== Parallel Compressor Operation ===")
print(f"\nTotal feed:  {main_feed.getFlowRate('kg/hr'):.0f} kg/hr "
      f"at {main_feed.getPressure():.1f} bara")

power_a = comp_a.getPower() / 1000.0
power_b = comp_b.getPower() / 1000.0

print(f"\nCompressor A: {comp_a.getInletStream().getFlowRate('kg/hr'):.0f} kg/hr")
print(f"  Power:  {power_a:.0f} kW")
print(f"  Eta_p:  {comp_a.getPolytropicEfficiency()*100:.1f}%")
print(f"  T_out:  {comp_a.getOutletStream().getTemperature('C'):.1f} C")

print(f"\nCompressor B: {comp_b.getInletStream().getFlowRate('kg/hr'):.0f} kg/hr")
print(f"  Power:  {power_b:.0f} kW")
print(f"  Eta_p:  {comp_b.getPolytropicEfficiency()*100:.1f}%")
print(f"  T_out:  {comp_b.getOutletStream().getTemperature('C'):.1f} C")

print(f"\nTotal power: {power_a + power_b:.0f} kW")
print(f"Combined discharge: "
      f"{mixer.getOutletStream().getFlowRate('kg/hr'):.0f} kg/hr "
      f"at {mixer.getOutletStream().getPressure():.1f} bara, "
      f"{mixer.getOutletStream().getTemperature('C'):.1f} C")
```

### 15.13.6 Off-Design Performance Prediction

This example demonstrates how to evaluate compressor performance when gas composition changes during field life:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# ============================================================
# Effect of Gas Composition Change on Compressor Performance
# ============================================================

# Define three gas compositions representing field life stages
compositions = {
    "Year 1 (rich)": {
        "methane": 72.0, "ethane": 8.0, "propane": 6.0,
        "i-butane": 2.0, "n-butane": 3.5, "i-pentane": 1.2,
        "n-pentane": 1.0, "n-hexane": 0.8, "CO2": 3.5,
        "nitrogen": 2.0
    },
    "Year 5 (medium)": {
        "methane": 80.0, "ethane": 7.0, "propane": 4.5,
        "i-butane": 1.2, "n-butane": 2.0, "i-pentane": 0.5,
        "n-pentane": 0.3, "n-hexane": 0.2, "CO2": 3.0,
        "nitrogen": 1.3
    },
    "Year 10 (lean)": {
        "methane": 88.0, "ethane": 4.5, "propane": 2.0,
        "i-butane": 0.5, "n-butane": 0.8, "CO2": 2.5,
        "nitrogen": 1.7
    }
}

print(f"{'Scenario':<22} {'MW':>6} {'Power':>8} {'T_out':>7} "
      f"{'Head':>8} {'PR':>5}")
print("=" * 60)

for name, comp_dict in compositions.items():
    fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 30.0, 5.0)
    for component, frac in comp_dict.items():
        fluid.addComponent(component, float(frac))
    fluid.setMixingRule("classic")

    feed = jneqsim.process.equipment.stream.Stream("Feed", fluid)
    feed.setFlowRate(30000.0, "kg/hr")
    feed.setTemperature(30.0, "C")
    feed.setPressure(5.0, "bara")

    comp = jneqsim.process.equipment.compressor.Compressor("Comp", feed)
    comp.setOutletPressure(15.0)
    comp.setPolytropicEfficiency(0.80)
    comp.setUsePolytropicCalc(True)

    process = jneqsim.process.processmodel.ProcessSystem()
    process.add(feed)
    process.add(comp)
    process.run()

    mw = feed.getFluid().getMolarMass() * 1000.0
    power = comp.getPower() / 1000.0
    t_out = comp.getOutletStream().getTemperature("C")
    head = comp.getPolytropicFluidHead()
    pr = comp.getOutletStream().getPressure() / feed.getPressure()

    print(f"{name:<22} {mw:>6.1f} {power:>6.0f} kW "
          f"{t_out:>5.1f} C {head:>7.1f} {pr:>5.1f}")
```

### 15.13.7 Field Performance Monitoring Example

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import numpy as np

# ============================================================
# Compressor Performance Monitoring — Degradation Detection
# ============================================================

# Simulate "measured" field data with progressive fouling
# Clean machine baseline
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 30.0, 5.0)
gas.addComponent("methane", 83.0)
gas.addComponent("ethane", 7.0)
gas.addComponent("propane", 4.0)
gas.addComponent("n-butane", 2.0)
gas.addComponent("CO2", 3.0)
gas.addComponent("nitrogen", 1.0)
gas.setMixingRule("classic")

# Baseline run (clean compressor)
feed_clean = jneqsim.process.equipment.stream.Stream("Feed Clean", gas)
feed_clean.setFlowRate(25000.0, "kg/hr")
feed_clean.setTemperature(30.0, "C")
feed_clean.setPressure(5.0, "bara")

comp_clean = jneqsim.process.equipment.compressor.Compressor(
    "Clean Compressor", feed_clean)
comp_clean.setOutletPressure(15.0)
comp_clean.setPolytropicEfficiency(0.80)
comp_clean.setUsePolytropicCalc(True)

process_clean = jneqsim.process.processmodel.ProcessSystem()
process_clean.add(feed_clean)
process_clean.add(comp_clean)
process_clean.run()

baseline_head = comp_clean.getPolytropicFluidHead()
baseline_power = comp_clean.getPower() / 1000.0
baseline_eff = comp_clean.getPolytropicEfficiency()
baseline_tout = comp_clean.getOutletStream().getTemperature("C")

print("=== Baseline (Clean Machine) ===")
print(f"Head:   {baseline_head:.1f} kJ/kg")
print(f"Power:  {baseline_power:.0f} kW")
print(f"Eff:    {baseline_eff*100:.1f}%")
print(f"T_out:  {baseline_tout:.1f} C")

# Simulate degradation at different efficiency levels
print("\n=== Degradation Monitoring ===")
print(f"{'Month':>6} {'Eff_actual':>12} {'Head_dev':>10} "
      f"{'Eff_dev':>10} {'Power_dev':>10} {'Status':>10}")
print("-" * 62)

fouling_progression = [0.80, 0.79, 0.78, 0.77, 0.76, 0.75, 0.74]

for month, eff in enumerate(fouling_progression):
    fluid = gas.clone()
    feed = jneqsim.process.equipment.stream.Stream("Feed", fluid)
    feed.setFlowRate(25000.0, "kg/hr")
    feed.setTemperature(30.0, "C")
    feed.setPressure(5.0, "bara")

    comp = jneqsim.process.equipment.compressor.Compressor("Comp", feed)
    comp.setOutletPressure(15.0)
    comp.setPolytropicEfficiency(eff)
    comp.setUsePolytropicCalc(True)

    process = jneqsim.process.processmodel.ProcessSystem()
    process.add(feed)
    process.add(comp)
    process.run()

    head = comp.getPolytropicFluidHead()
    power = comp.getPower() / 1000.0
    actual_eff = comp.getPolytropicEfficiency()

    head_dev = (head - baseline_head) / baseline_head * 100
    eff_dev = actual_eff - baseline_eff
    power_dev = (power - baseline_power) / baseline_power * 100

    status = "OK"
    if abs(eff_dev) > 0.03:
        status = "WARNING"
    if abs(eff_dev) > 0.05:
        status = "ALARM"

    print(f"{month*3:>6} {actual_eff*100:>10.1f}% {head_dev:>9.1f}% "
          f"{eff_dev*100:>8.1f} pts {power_dev:>9.1f}% {status:>10}")
```

## 15.14 Advanced Topics

### 15.14.1 Compressor Selection Methodology

Compressor selection for a new project follows a systematic procedure:

1. **Define operating conditions**: Suction T, P; discharge P; gas composition; flow range (min/normal/max)
2. **Calculate thermodynamic requirements**: Polytropic head, power, discharge temperature
3. **Screen compressor types**: Based on flow rate and pressure ratio (see Table 12.1)
4. **Request vendor bids**: Provide process data sheets per API 617 Data Sheet format
5. **Evaluate bids**: Compare efficiency, operating range, surge margin, mechanical design
6. **Performance verification**: Factory acceptance test per API 617

### 15.14.2 Wet Gas Compression

Wet gas (containing liquid droplets) poses special challenges:
- Liquid impingement erodes impellers
- Evaporative cooling changes thermodynamic path
- Phase change during compression complicates performance analysis

For wet gas compression, the polytropic analysis must account for the two-phase nature of the process. NeqSim can model this by performing the compression with multiphase flash calculations at intermediate pressure steps.

### 15.14.3 CO$_2$ Compression

CO$_2$ compression for CCS applications requires special consideration:
- CO$_2$ has a critical point at 31.1°C and 73.8 bara — near typical compression conditions
- Properties change rapidly near the critical point
- Integrally geared compressors with 8–10 stages are common
- Dense phase pumping may replace compression above the critical pressure
- Impurity effects (H$_2$O, N$_2$, H$_2$S, O$_2$) significantly affect phase behavior

NeqSim's accurate real-gas property calculations are particularly valuable for CO$_2$ compression analysis, where ideal gas approximations fail spectacularly near the critical point.

## 15.15 Summary

This chapter has provided a comprehensive treatment of compressor characteristics and performance curves:

1. **Performance maps** (head vs. flow, efficiency vs. flow) define the complete operating envelope of a centrifugal compressor, bounded by surge (minimum flow), stonewall (maximum flow), and speed limits.

2. **Surge** is the most critical stability limit. Anti-surge control systems using fast-acting recycle valves and real-time surge parameter monitoring are essential for safe operation.

3. **Reduced (referred) conditions** allow manufacturer's performance maps to be applied at field conditions that differ from the test conditions, by preserving the Mach number and flow coefficient.

4. **Fan laws** provide the relationship between performance at different speeds and are the basis for variable speed control and curve generation from a single design-speed test.

5. **Performance curves can be generated** from a single design point using the fan laws and assumed curve shape coefficients, providing approximate maps for simulation when detailed vendor data is unavailable.

6. **Off-design performance** due to gas composition changes (MW, $\gamma$, $Z$) can be predicted through reduced parameter corrections, which is essential for life-of-field compressor evaluation.

7. **Field performance monitoring** based on polytropic head and efficiency deviation detects degradation from fouling, erosion, and mechanical wear, enabling condition-based maintenance.

8. **NeqSim's CompressorChart** class integrates performance map data directly into the process simulation, allowing the simulation to automatically determine the operating point, efficiency, and power based on actual process conditions.

9. **Production optimization** requires accurate compressor models because compressors are often the binding constraint on production rate and the largest energy consumers in the facility.

---

## 15.14 Compressor Type Selection

### 15.14.1 Compressor Types for Oil and Gas Service

Three principal compressor types are used in oil and gas production: centrifugal, reciprocating, and screw (rotary positive displacement). Each type has a distinct operating envelope and is suited to different applications.

**Centrifugal compressors** are the dominant type for large-volume, moderate-pressure-ratio applications on offshore platforms and gas processing plants. They use high-speed rotating impellers to convert kinetic energy into pressure rise through a diffuser. Key characteristics: high reliability (mean time between failure > 50,000 hours), continuous flow (no pulsation), compact footprint for the throughput, and suitability for variable-speed operation. However, centrifugal machines are sensitive to gas MW changes, have a limited turndown range (typically 70–100% of design flow), and are not well suited to very high pressure ratios per stage (typically limited to 3:1 per stage with impeller tip speed constraints).

**Reciprocating compressors** use pistons driven by a crankshaft to compress gas in a positive-displacement cycle. They are preferred for low-flow, high-pressure-ratio applications such as gas reinjection, wellhead compression, and instrument air. Key characteristics: can achieve very high pressure ratios (up to 10:1 per stage), efficient across a wide range of flow rates, capable of handling varying gas compositions with minimal performance change, and inherently self-adjusting to changes in suction conditions. Disadvantages include pulsating flow (requires pulsation dampeners per API 618), higher maintenance requirements (valve replacement, piston ring wear), larger footprint, and higher vibration levels.

**Screw compressors** (twin-screw or single-screw) use meshing helical rotors to compress gas in a continuous positive-displacement process. They are used for low-pressure boosting (< 10 bara discharge), wet gas compression, and applications where liquid tolerance is required. Key characteristics: can handle liquid slugs without damage (oil-flooded designs), continuous flow with low pulsation, compact and robust. Limitations: limited to low-to-moderate pressure ratios (< 5:1), lower efficiency than centrifugal at high flows, and internal leakage limits performance at high pressure ratios.

### 15.14.2 Selection Criteria

The primary factors governing compressor type selection are:

| Criterion | Centrifugal | Reciprocating | Screw |
|-----------|------------|--------------|-------|
| Flow range (actual m³/hr) | 1,000–500,000 | 10–50,000 | 100–30,000 |
| Pressure ratio per stage | 1.5–3.0 | Up to 10 | 1.5–5.0 |
| Maximum discharge pressure | 250 bara | 1,000+ bara | 40 bara |
| Gas MW sensitivity | High | Low | Low |
| Liquid tolerance | Very low | Low (with knock-out) | High (oil-flooded) |
| Turndown range | 70–100% | 0–100% (step or stepless) | 10–100% (slide valve) |
| Reliability (MTBF) | > 50,000 hours | 20,000–40,000 hours | 30,000–50,000 hours |
| Maintenance intensity | Low | High | Moderate |
| Pulsation | None | Significant (API 618 study required) | Low |
| Footprint per MW | Small | Large | Moderate |
| Variable speed benefit | High | Moderate | Moderate |
| Typical driver | Gas turbine, electric motor | Electric motor, gas engine | Electric motor |

### 15.14.3 Selection Decision Framework

The following decision logic guides compressor type selection:

1. **If actual volumetric flow > 5,000 m³/hr AND pressure ratio < 4:1**: Centrifugal is the default choice. It offers the best combination of reliability, compact footprint, and efficiency for high-throughput moderate-ratio applications typical of gas export, recompression, and gas lift compression.

2. **If required discharge pressure > 250 bara OR pressure ratio > 6:1 per casing**: Reciprocating is required. This includes gas reinjection compressors (300–500 bara), wellhead gas compression with high GOR, and small gas-to-wire applications.

3. **If actual volumetric flow < 1,000 m³/hr AND moderate pressure ratio**: Reciprocating is preferred due to its superior part-load efficiency and adaptability to varying conditions. Common for late-life low-pressure gas recovery and satellite compression.

4. **If wet gas or liquid slugging is expected**: Screw compressor is preferred for subsea boosting pilots and applications where conventional knock-out drums cannot guarantee dry gas.

5. **If composition varies significantly over field life (large MW swing)**: Reciprocating machines are less affected by composition changes. Centrifugal machines may require restaging or speed range extension to handle the full range.

For many offshore platforms, a combination of types is used: centrifugal for the main export compression (high volume, moderate ratio), reciprocating for gas injection or fuel gas boosting (low volume, high ratio), and possibly screw for vapor recovery (low pressure, liquid-tolerant).

## Exercises

**Exercise 15.1**: A centrifugal compressor has the following design point data: flow = 5000 m$^3$/hr (actual), polytropic head = 95 kJ/kg, polytropic efficiency = 82%, speed = 10,000 rpm. Using the fan laws, calculate the head, flow, and power at 90%, 80%, and 70% speed. Assume the operating point moves along the design head-flow curve.

**Exercise 15.2**: Construct a complete compressor performance map using the design point from Exercise 15.1. Generate head vs. flow and efficiency vs. flow curves for speeds from 70% to 105%. Plot the surge line assuming a surge flow ratio of 0.60 at the design speed.

**Exercise 15.3**: A compressor designed for a gas with MW = 22 and $\gamma = 1.28$ is now operating with a leaner gas (MW = 18, $\gamma = 1.32$) due to reservoir depletion. At the same speed:
(a) How does the maximum polytropic head change?
(b) How does the volumetric flow at surge change?
(c) Does the compressor have more or less operating range?

**Exercise 15.4**: Model two identical compressors in parallel using NeqSim. The total flow is 60,000 kg/hr of natural gas at 5 bara, 30°C to be compressed to 15 bara. Compare the total power for (a) equal 50/50 split, (b) 60/40 split, (c) 70/30 split. Is there a benefit to unequal loading?

**Exercise 15.5**: Implement a simple field performance monitoring tool in Python that:
(a) Reads operating data (T$_s$, P$_s$, T$_d$, P$_d$, flow rate, speed)
(b) Calculates polytropic head and efficiency using NeqSim
(c) Compares to baseline values
(d) Flags deviations exceeding defined thresholds

**Exercise 15.6**: Design an anti-surge system for the compressor in Exercise 15.1. Determine:
(a) The surge control line location (10% margin)
(b) The maximum recycle rate required at 40% turndown
(c) The recycle cooler duty to maintain 35°C suction temperature
(d) The anti-surge valve $C_v$ required

**Exercise 15.7**: A recompression compressor is expected to operate for 15 years. Over this period, the gas MW decreases from 24 to 18 and the suction pressure decreases from 5 to 3 bara. Model the compressor performance at 5-year intervals using NeqSim and determine when the compressor reaches its surge limit or maximum speed limit.

**Exercise 15.8**: Compare the polytropic head and power calculated by NeqSim (using the SRK equation of state) with ideal gas calculations for:
(a) Methane at 30°C, 5 to 15 bara (low pressure, should match well)
(b) CO$_2$ at 30°C, 20 to 80 bara (near critical, significant deviation expected)
(c) A rich gas at 30°C, 50 to 150 bara (high pressure, real gas effects)
Plot the percentage deviation between ideal gas and NeqSim results.

**Exercise 15.9**: Generate compressor performance curves from a design point using the methodology in Section 15.6.2, and then verify by comparing with NeqSim calculations. How sensitive are the results to the assumed curve shape coefficients $a_0$–$a_3$?

**Exercise 15.10**: A platform has three compressor trains in parallel, each rated at 10 MW. Production requires a total compression power of 25 MW. Evaluate the optimal operating strategy:
(a) Run all three at 83% capacity
(b) Run two at 100% and one at 50%
(c) Run two at full speed and one at reduced speed
Which strategy minimizes total fuel gas consumption? Use NeqSim to calculate the efficiency at each operating point.

## References

1. API Standard 617 (2022). Axial and Centrifugal Compressors and Expander-Compressors, 8th ed. American Petroleum Institute.
2. Brown, R.N. (2005). *Compressors: Selection and Sizing*, 3rd ed. Gulf Professional Publishing.
3. Bloch, H.P. (2006). *A Practical Guide to Compressor Technology*, 2nd ed. John Wiley & Sons.
4. Hundseid, Ø., Bakken, L.E., and Grüner, T.G. (2006). Wet gas performance of a single-stage centrifugal compressor. *Proceedings of ASME Turbo Expo*, GT2006-90455.
5. Schultz, J.M. (1962). The polytropic analysis of centrifugal compressors. *Journal of Engineering for Power*, 84(1), 69–82.
6. Sandberg, M.R. and Colby, G.M. (2013). Limitations of ASME PTC 10 in accurately evaluating centrifugal compressor thermodynamic performance. *Proceedings of the 42nd Turbomachinery Symposium*.
7. Lüdtke, K.H. (2004). *Process Centrifugal Compressors: Basics, Function, Operation, Design, Application*. Springer.
8. Boyce, M.P. (2012). *Gas Turbine Engineering Handbook*, 4th ed. Butterworth-Heinemann.
9. ASME PTC 10 (1997). Performance Test Code on Compressors and Exhausters. American Society of Mechanical Engineers.
10. Gresh, M.T. (2001). *Compressor Performance: Aerodynamics for the User*, 2nd ed. Butterworth-Heinemann.
11. Giampaolo, T. (2010). *Compressor Handbook: Principles and Practice*. CRC Press.
12. Japikse, D. (1996). *Centrifugal Compressor Design and Performance*. Concepts ETI.
13. NORSOK P-002 (2014). Process System Design. Standards Norway.
14. ISO 5389 (2005). Turbocompressors — Performance test code. International Organization for Standardization.
15. Brun, K. and Kurz, R. (2019). *Compression Machinery for Oil and Gas*. Gulf Professional Publishing.


## Figures

![Figure 15.1: Efficiency Vs Flow](figures/ch13_efficiency_vs_flow.png)

*Figure 15.1: Efficiency Vs Flow*

![Figure 15.2: Head Vs Flow](figures/ch13_head_vs_flow.png)

*Figure 15.2: Head Vs Flow*

![Figure 15.3: Operating Envelope](figures/ch13_operating_envelope.png)

*Figure 15.3: Operating Envelope*
