const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const angles=require('../docs/angular-inputs.js');
const html=fs.readFileSync(require('node:path').join(__dirname,'../docs/index.html'),'utf8');
const a=html.indexOf('var AqueousOutflow = (function'),ctx={AngularInputs:angles};vm.createContext(ctx);vm.runInContext(html.slice(a,html.indexOf('</script>',a)),ctx);const model=ctx.AqueousOutflow;
assert.deepEqual(angles.range('0-30',1200),[[0,99]]);
assert.deepEqual(angles.range('350-10',1200),[[1167,1199],[0,32]]);
assert.deepEqual(angles.range('0-360',1200),[[0,1199]]);
assert.deepEqual(angles.range('0-30',2400),[[0,199]]);
assert.equal(angles.point('360',1200),0);
assert.equal(angles.point('90°',1200),300);
assert.throws(()=>angles.range('10-10',1200),/zero width/);
assert.throws(()=>angles.point(361,1200),/between/);
const angular={position_units:'degrees',n:30,m:40,surgery:'Trabeculotomy',trabeculotomies:'0-30',rtm_node_overrides:'36-42.3:3200',h0_node_overrides:'350-10:14',ccs:'0:1,12:0.5',stent_nodes:'90,180',stent_l_before:3,stent_l_after:6,damage_start:350,damage_count:20};
const converted=angles.toNodes(angular);
assert.equal(converted.trabeculotomies,'0-99');assert.equal(converted.rtm_node_overrides,'120-140:3200');
assert.equal(converted.h0_node_overrides,'1167-1199:14, 0-32:14');assert.equal(converted.ccs,'0:1, 40:0.5');
assert.equal(converted.stent_nodes,'300, 600');assert.equal(converted.stent_l_before,10);assert.equal(converted.stent_l_after,20);assert.equal(converted.damage_count,67);
assert.throws(()=>angles.toNodes({position_units:'degrees',ccs:'0:1,360:2'}),/same position/);
// Saved v1 files retain inclusive footprints, sparse overrides, and counts.
const old={n:30,m:40,surgery:'Trabeculotomy',trab_hours:1,trabeculotomies:'0-99,1100-1199',stent_nodes:'0,300',rtm_node_overrides:'120-140:3200',gsc_override:'0:0',damage_start:900,damage_count:10,stent_l_before:3,stent_l_after:5,surgery2:'Laser damage — TM only',procedure2_positions:'1199',procedure2_amount:2};
const roundtrip=angles.toNodes(angles.toDegrees(old));
assert(Object.values(angles.toDegrees(old)).every(v=>v!==undefined));
for(const field of ['damage_start','damage_count','stent_l_before','stent_l_after'])assert.equal(roundtrip[field],old[field]);
assert.equal(roundtrip.trabeculotomies,'0-99, 1100-1199');assert.equal(roundtrip.rtm_node_overrides,'120-140:3200');assert.equal(roundtrip.procedure2_positions,1199);assert.equal(roundtrip.procedure2_amount,2);
const preset=angles.toNodes(angles.toDegrees({surgery:'Trabeculotomy',trab_hours:1}));assert.equal(preset.trabeculotomies,'550-650');
assert.equal(angles.toNodes({position_units:'degrees',n:30,m:80,surgery2:'YAG holes',procedure2_amount:2}).procedure2_positions,'600, 1800');
assert.equal(angles.toNodes(angles.toDegrees({n:30,m:80,surgery:'YAG holes',yag_holes:2})).yag_holes_list,'300, 900');
// Match the unchanged node-based solver, including every procedure slot.
const common={mode:'constant flow',qt:2,pev:8,rtm:2};
for(const p of [
 {surgery:'Trabeculotomy',trabeculotomies:'350-10'},
 {surgery:'YAG holes',yag_holes_list:'90,270'},
 {surgery:'Laser damage — TM only',damage_start:350,damage_count:20},
 {surgery:'None',surgery2:'Trabeculotomy',procedure2_positions:'0-30'},
 {surgery:'None',surgery3:'Laser damage — TM only',procedure3_positions:350,procedure3_amount:20},
 {surgery:'iStent',stent_nodes:'90',stent_l_before:0,stent_l_after:0}
]){
 const input={...common,...p,position_units:'degrees'},nodeInput=angles.toNodes(input);
 const angularResult=model.solvePayload(input),nodeResult=model.solvePayload(nodeInput);
 assert.equal(JSON.stringify(angularResult.metrics),JSON.stringify(nodeResult.metrics));
 assert.equal(JSON.stringify(angularResult.series),JSON.stringify(nodeResult.series));
}
const baseline=model.solvePayload(common);assert.equal(baseline.series.pressure.x[40],12);assert.equal(baseline.series.pressure.x[1199],359.7);assert.equal(baseline.series.jcc.x[1],12);
const series={x:[0,90,180,270],y:[1,2,3,4]},extended=angles.periodicSeries(series);
assert.equal(extended.x[0],-30);assert.equal(extended.x.at(-1),390);assert.equal(extended.y[extended.x.indexOf(0)],extended.y[extended.x.indexOf(360)]);
for(let i=1;i<extended.x.length;i++)assert(extended.x[i]>extended.x[i-1]);
assert.deepEqual(series,{x:[0,90,180,270],y:[1,2,3,4]});
assert.deepEqual(angles.periodicSeries({x:[45],y:[7]}).y,[7,7,7]);
console.log('PASS: angle boundaries, wraparound, grid scaling, legacy migration, all procedure slots, solver equivalence, periodic display.');
