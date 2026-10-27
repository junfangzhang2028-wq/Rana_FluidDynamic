/* Angle-based UI adapter. Hydraulic solver and legacy input format stay in nodes. */
(function(root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.AngularInputs = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function() {
  'use strict';
  function blank(v) { return v === undefined || v === null || String(v).trim() === ''; }
  function chunks(v) { return String(v).split(/[,;\n]+/).map(function(s){return s.trim();}).filter(Boolean); }
  function total(p) {
    var n = Number(p.n || 30), m = Number(p.m || 40);
    if (!Number.isInteger(n) || !Number.isInteger(m) || n < 1 || m < 1) throw Error('N and M must be positive integers.');
    return n * m;
  }
  function angle(v) {
    var x = Number(String(v).trim().replace(/°$/, ''));
    if (blank(v) || !isFinite(x) || x < 0 || x > 360) throw Error('Angles must be between 0 and 360 degrees.');
    return x;
  }
  function fmt(x) { return String(Number(x.toFixed(10))); }
  function point(v, n) { return Math.round(angle(v) * n / 360) % n; }
  function extent(v, n, allowZero) {
    var a = angle(v);
    if (!allowZero && a === 0) throw Error('Angular extent must be greater than zero.');
    return a === 0 ? 0 : Math.max(1, Math.round(a * n / 360));
  }
  // Ranges are clockwise [start,end). Equal endpoints are not a full circle.
  function range(v, n) {
    var parts = String(v).trim().split(/[-:]/);
    if (parts.length === 1) { var i = point(parts[0], n); return [[i,i]]; }
    if (parts.length !== 2) throw Error('Use an angle or a start-end angular range.');
    var a = angle(parts[0]), b = angle(parts[1]);
    if (a === 0 && b === 360) return [[0,n-1]];
    var span = (b - a + 360) % 360;
    if (span === 0) throw Error('Equal range endpoints have zero width; use 0-360 for the full circle.');
    var first = point(a, n);
    var count = Math.max(1, Math.round((a + span) * n / 360) - Math.round(a * n / 360));
    if (count >= n) return [[0,n-1]];
    var last = first + count - 1;
    return last < n ? [[first,last]] : [[first,n-1],[0,last-n]];
  }
  function ranges(v,n) { return blank(v) ? '' : chunks(v).flatMap(function(s){return range(s,n);}).map(function(r){return r[0]+'-'+r[1];}).join(', '); }
  function points(v,n) { return blank(v) ? '' : chunks(v).map(function(s){return point(s,n);}).join(', '); }
  function keyed(v,n) {
    if (blank(v) || !/[:=]/.test(v)) return v;
    return chunks(v).flatMap(function(s) {
      var at = s.search(/[:=]/), key = s.slice(0,at), value = s.slice(at+1);
      if (at < 1 || blank(value)) throw Error('Use angle:value or start-end:value.');
      return range(key,n).map(function(r){return (r[0]===r[1]?r[0]:r[0]+'-'+r[1])+':'+value;});
    }).join(', ');
  }
  function ccs(v,n) {
    if (blank(v)) return '';
    var seen = new Set();
    return chunks(v).map(function(s) {
      var parts = s.split(/[:=]/), i = point(parts[0],n);
      if (seen.has(i)) throw Error('Two CC angles snap to the same position; increase resolution or separate them.');
      seen.add(i);
      return i+':'+(parts.length>1?parts[1]:'1');
    }).join(', ');
  }
  function preset(hours,n) {
    var map = {1:'165-195',4:'30-60, 120-150, 210-240, 300-330',12:'0-360'};
    if (!map[hours]) throw Error('Trabeculotomy preset must be 1, 4 or 12 clock hours.');
    return ranges(map[hours],n);
  }
  var holeAngles={1:[180],2:[90,270],3:[60,180,300],4:[45,135,225,315],5:[36,108,180,252,324],6:[30,90,150,210,270,330]};
  function toNodes(input) {
    if (input.position_units !== 'degrees') return Object.assign({},input);
    var p = Object.assign({},input), n = total(p);
    ['trabeculotomies','sinusotomies'].forEach(function(k){p[k]=ranges(p[k],n);});
    ['yag_holes_list','stent_nodes'].forEach(function(k){p[k]=points(p[k],n);});
    p.ccs = ccs(p.ccs,n);
    ['rtm_node_overrides','h0_node_overrides','gsc_multiplier','gsc_override'].forEach(function(k){p[k]=keyed(p[k],n);});
    p.damage_start = point(blank(p.damage_start)?0:p.damage_start,n);
    p.damage_count = extent(blank(p.damage_count)?360/n:p.damage_count,n,false);
    p.stent_node = point(blank(p.stent_node)?0:p.stent_node,n);
    ['stent_l_before','stent_l_after'].forEach(function(k){p[k]=extent(blank(p[k])?0:p[k],n,true);});
    if (p.surgery === 'Trabeculotomy' && blank(p.trabeculotomies)) p.trabeculotomies=preset(p.trab_hours||1,n);
    // The existing hole-count presets also follow the angular grid.
    if (p.surgery === 'YAG holes' && blank(p.yag_holes_list)) {
      if(holeAngles[p.yag_holes||2]) p.yag_holes_list=points(holeAngles[p.yag_holes||2].join(','),n);
    }
    [2,3].forEach(function(slot) {
      var k='procedure'+slot+'_positions', t=p['surgery'+slot], a='procedure'+slot+'_amount';
      if(t==='Trabeculotomy') p[k]=blank(p[k])?preset(p[a]||1,n):ranges(p[k],n);
      else if(t==='Sinusotomy') p[k]=ranges(p[k],n);
      else if(t && t.indexOf('Laser damage')===0) {p[k]=point(blank(p[k])?0:p[k],n);p[a]=extent(blank(p[a])?360/n:p[a],n,false);}
      else if(t==='YAG holes' && blank(p[k]) && holeAngles[p[a]||1]) p[k]=points(holeAngles[p[a]||1].join(','),n);
      else if(t==='iStent'||t==='YAG holes') p[k]=points(p[k],n);
    });
    p.position_units='nodes';
    return p;
  }
  // Convert a legacy model to the new UI without changing its discretized region.
  function toDegrees(input) {
    if(input.position_units==='degrees') return Object.assign({},input);
    var p=Object.assign({},input), n=total(p);
    function pos(x){return fmt(Number(x)*360/n);}
    function oldRanges(v){return blank(v)?'':chunks(v).map(function(s){var r=s.split(/[-:]/).map(Number);var a=Math.min.apply(null,r),b=Math.max.apply(null,r);return pos(a)+'-'+pos(b+1);}).join(', ');}
    function oldPoints(v){return blank(v)?'':chunks(v).map(pos).join(', ');}
    function oldKeyed(v){if(blank(v)||! /[:=]/.test(v))return v;return chunks(v).map(function(s){var at=s.search(/[:=]/),k=s.slice(0,at);return (k.indexOf('-')>=0?oldRanges(k):pos(k))+':'+s.slice(at+1);}).join(', ');}
    ['trabeculotomies','sinusotomies'].forEach(function(k){p[k]=oldRanges(p[k]);});
    ['yag_holes_list','stent_nodes'].forEach(function(k){p[k]=oldPoints(p[k]);});
    if(!blank(p.ccs))p.ccs=chunks(p.ccs).map(function(s){var v=s.split(/[:=]/);return pos(v[0])+':'+(v[1]||'1');}).join(', ');
    ['rtm_node_overrides','h0_node_overrides','gsc_multiplier','gsc_override'].forEach(function(k){p[k]=oldKeyed(p[k]);});
    ['damage_start','damage_count','stent_node','stent_l_before','stent_l_after'].forEach(function(k){if(!blank(p[k]))p[k]=pos(p[k]);});
    // Preserve historical preset footprints (inclusive end nodes on the 1200 grid).
    var oldPresets={1:'550-650',4:'100-200,400-500,700-800,1000-1100',12:'0-1199'};
    if(p.surgery==='Trabeculotomy'&&blank(p.trabeculotomies))p.trabeculotomies=oldRanges(oldPresets[p.trab_hours||1]);
    if(p.surgery==='YAG holes'&&blank(p.yag_holes_list)&&holeAngles[p.yag_holes||2])p.yag_holes_list=oldPoints(holeAngles[p.yag_holes||2].map(function(a){return a*1200/360;}).join(','));
    [2,3].forEach(function(slot){var k='procedure'+slot+'_positions',t=p['surgery'+slot],a='procedure'+slot+'_amount';
      if(t==='Trabeculotomy')p[k]=oldRanges(blank(p[k])?oldPresets[p[a]||1]:p[k]);
      else if(t==='Sinusotomy')p[k]=oldRanges(p[k]);
      else if(t&&t.indexOf('Laser damage')===0){p[k]=pos(blank(p[k])?0:p[k]);p[a]=pos(blank(p[a])?1:p[a]);}
      else if(t==='YAG holes'&&blank(p[k])&&holeAngles[p[a]||1])p[k]=oldPoints(holeAngles[p[a]||1].map(function(a){return a*1200/360;}).join(','));
      else if(t==='YAG holes'||t==='iStent')p[k]=oldPoints(p[k]);
    });
    Object.keys(p).forEach(function(k){if(p[k]===undefined)delete p[k];});
    p.position_units='degrees';return p;
  }
  function periodicSeries(series,padding) {
    padding=padding===undefined?30:padding;
    var points=[],seen=new Set();
    series.x.forEach(function(x,i){var a=((Number(x)%360)+360)%360;if(!seen.has(a)){points.push([a,series.y[i]]);seen.add(a);}});
    points.sort(function(a,b){return a[0]-b[0];});
    if(!points.length)return {x:[],y:[]};
    var copies=[];[-360,0,360].forEach(function(offset){points.forEach(function(p){copies.push([p[0]+offset,p[1]]);});});
    function valueAt(x){for(var i=1;i<copies.length;i++){if(copies[i][0]>=x){var a=copies[i-1],b=copies[i];return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0]);}}return copies[copies.length-1][1];}
    var lo=-padding,hi=360+padding;
    var out=[[lo,valueAt(lo)]].concat(copies.filter(function(p){return p[0]>lo&&p[0]<hi;}),[[hi,valueAt(hi)]]);
    return {x:out.map(function(p){return p[0];}),y:out.map(function(p){return p[1];}),
      synthetic:out.map(function(p){return !copies.some(function(c){return c[0]===p[0];});})};
  }
  return {toNodes:toNodes,toDegrees:toDegrees,range:range,point:point,periodicSeries:periodicSeries};
});
