# Reuse surface_case from the preceding, executed CPA Monte Carlo example.
base = dict(feed_rate=80000.,feed_pres=55.,water_mole_fraction=.15,
            temperature=35.,comp_eff=.78)
base_result = surface_case(**base)
labels = ['Feed rate (kg/hr)','Feed pressure (bara)',
          'Water mole fraction (-)','Temperature (C)','Isentropic efficiency (-)']
tornado_data = []
for (name,(low,high)),label in zip(param_ranges.items(),labels):
    low_inputs = dict(base); low_inputs[name] = low
    high_inputs = dict(base); high_inputs[name] = high
    low_result = surface_case(**low_inputs); high_result = surface_case(**high_inputs)
    offsets = [low_result['gas_production_kg_hr']-base_result['gas_production_kg_hr'],
               high_result['gas_production_kg_hr']-base_result['gas_production_kg_hr']]
    tornado_data.append(dict(label=label,low=offsets[0],high=offsets[1],
        swing=max(0.,*offsets)-min(0.,*offsets),low_case=low_result,high_case=high_result))
# Prescribed upstream separator conditions make compressor efficiency irrelevant to gas yield.
efficiency_row = tornado_data[-1]
assert abs(efficiency_row['low']) < 1e-6 and abs(efficiency_row['high']) < 1e-6
assert efficiency_row['low_case']['compressor_power_kW'] > efficiency_row['high_case']['compressor_power_kW']
tornado_data.sort(key=lambda row:row['swing'],reverse=True)
fig,ax = plt.subplots(figsize=(10,5))
y = np.arange(len(tornado_data))
ax.barh(y-.17,[r['low'] for r in tornado_data],height=.32,label='Low input value')
ax.barh(y+.17,[r['high'] for r in tornado_data],height=.32,label='High input value')
ax.set_yticks(y,labels=[r['label'] for r in tornado_data]);ax.invert_yaxis()
ax.set_xlabel('Gas rate change from base (kg/hr)')
ax.set_title('CPA separator sensitivity at prescribed feed rate')
ax.axvline(0,color='black',linewidth=.8);ax.grid(axis='x',alpha=.25);ax.legend()
fig.tight_layout();fig.savefig('figures/fig28_tornado.png',dpi=170,bbox_inches='tight');plt.close(fig)
Path('ch27_surface_tornado.json').write_text(json.dumps(
    {'base':base_result,'rows':tornado_data,'interpretation':'Low/high input cases; not probabilities or guaranteed extremes.'},indent=2))
print(json.dumps({'base_gas_kghr':base_result['gas_production_kg_hr'],
                  'base_power_kW':base_result['compressor_power_kW'],
                  'ranked_swings_kghr':[[r['label'],r['swing']] for r in tornado_data]},indent=2))
