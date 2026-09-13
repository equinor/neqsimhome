from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent;BOOK=ROOT.parents[1]
changes=[]
for path in (BOOK/'chapters').glob('*/notebooks/*.ipynb'):
    chapter=int(path.parent.parent.name[2:4]);nb=json.loads(path.read_text(encoding='utf-8'));changed=False
    for cell in nb['cells']:
        if cell['cell_type']!='code':continue
        source=''.join(cell['source']);new=source
        if chapter==7:
            new=new.replace("xytext=(8, 0.4)","xytext=(0.35, 0.15)")
            new=new.replace("Typical subsea\\noperating point","Illustrative\\noperating point")
            new=new.replace("Horizontal Multiphase Flow Regime Map","Illustrative Horizontal Flow-Regime Map")
            new=new.replace("Temperature Profile Along Subsea Pipeline","Isothermal Hydraulic Case: Temperature Held Constant")
            new=new.replace("label=f'Seawater Temperature = {T_seawater:.1f} °C'","label=f'Seawater reference only = {T_seawater:.1f} °C'")
            new=new.replace("xytext=(temperatures[-1]+3, pressures[-1]+5)","xytext=(temperatures[-1]+3, pressures[-1]-8)")
            old="""    ax1.text(cumulative[i+1] + val/2, i, f'{val:.0f} bar', ha='center', va='center',
             fontsize=11, fontweight='bold', color='white')"""
            replacement="""    if val < 15:
        ax1.text(cumulative[i] + 5, i, f'{val:.1f} bar', ha='left', va='center',
                 fontsize=11, fontweight='bold', color='#263746')
    else:
        ax1.text(cumulative[i+1] + val/2, i, f'{val:.0f} bar', ha='center', va='center',
                 fontsize=11, fontweight='bold', color='white')"""
            new=new.replace(old,replacement)
        if chapter==10:
            new=new.replace("xytext=(opt_p + 5, opt_y/1000 + 0.1)","xytext=(opt_p + 9, opt_y/1000 - 0.05)")
        if chapter==11 and 'fig10_3_multistage_oil_quality.png' in source:
            new=new.replace("ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)",
                            "ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper center', fontsize=11, ncol=2)\nax1.set_ylim(0, max(api_results)*1.15)\nax2.set_ylim(0, max(density_results)*1.15)")
        if chapter==12:
            new=new.replace('Typical C3+ spec (~5 mol%)','Illustrative C3+ limit (5 mol%)')
        if chapter==19:
            new=new.replace('Typical max dP = 50 bar','Illustrative dP limit = 50 bar')
        if chapter==27 and 'ch28_scenario_comparison.png' in source:
            new=new.replace("ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=10)",
                            "ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper center', fontsize=10, ncol=2)\nax1.set_ylim(0, max(optimal_rates)*1.20)\nax2.set_ylim(0, max(optimal_utils)*1.20)")
        if chapter==29:
            new=new.replace('ax.set_ylim(45, 62)',"ax.set_ylim(45, max(float(np.nanmax(line.get_ydata())) for line in ax.lines if len(line.get_ydata()) > 2) + 2)")
        if chapter==31:
            new=new.replace('Vapor Fraction (-)','Gas-labelled Phase Fraction (-)')
            new=new.replace('Vapor Fraction vs Pressure (SRK EOS)','NeqSim Gas-Phase Classification (SRK EOS)')
        if new!=source:
            changes.append({'notebook':str(path.relative_to(BOOK)),'before_sha256':hashlib.sha256(source.encode()).hexdigest(),
                            'after_sha256':hashlib.sha256(new.encode()).hexdigest(),'change_type':'plot labels, limits, annotations or legend placement only'})
            cell['source']=new.splitlines(keepends=True);changed=True
    if changed:path.write_text(json.dumps(nb,indent=1,ensure_ascii=False)+'\n',encoding='utf-8')
(ROOT/'figure_visual_review/layout_changes.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')
print('Updated',len(changes),'plot cells; no physical calculations changed.')
