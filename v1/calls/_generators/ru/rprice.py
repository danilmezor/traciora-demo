import json, os
SEED=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
C=json.load(open(SEED+'/catalogue.json'))
JOBS={j['key']:j['ru'] for j in C['jobs']}
CFG=C['configurations']['ru']
HOURS={'now':(1900,1700),'before':(1760,1580)}
def r10(x): return int(round(x/10.0)*10)
def price(key, cls='car', tier='standard', when='now', company=False, detail=False):
    """List price of a job for a vehicle class: hours x the hour (or the menu price) plus parts at list.
    Company accounts: the company hour and parts at 10 % off. Parts are today's (no drift), as the story cards use them."""
    j=JOBS[key]
    hb=j.get('hours_by_class') or {}
    mult=hb.get(cls,1.0) if hb else 1.0
    if mult is None: raise ValueError('not offered')
    idx={'before':2,'now':3}[when]
    if j['labour_pricing']=='hourly':
        lab=j['hours']*mult*HOURS[when][1 if company else 0]
    else:
        lab=(j['labour_price_company'] if company else j['labour_price'])['history'][idx]*mult
    pm=CFG['parts_class_multiplier'][cls] if j.get('parts_scale_with_class') else 1.0
    parts=0; pl=[]
    for p in j['parts']:
        opts={o['tier']:o for o in p['options'] if not o.get('story')}
        o=opts.get(tier) or opts.get('standard') or list(opts.values())[0]
        lp=r10(o['list_price']*pm)
        if company: lp=r10(lp*0.9)
        parts+=lp*p['qty']; pl.append((p['name'],p['qty'],o['brand'],o.get('part_number'),lp))
    fees=sum(f.get('price',0) for f in j.get('fees') or [])
    sub=(j.get('sublet') or {}).get('price',0) if j.get('sublet') else 0
    tot=lab+parts+fees+sub
    if detail: return dict(name=j['name'],hours=round(j['hours']*mult,2),labour=round(lab,2),parts=parts,fees=fees,sublet=sub,total=round(tot,2),pl=pl,pricing=j['labour_pricing'])
    return round(tot,2)
