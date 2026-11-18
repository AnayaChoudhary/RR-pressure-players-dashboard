const pptxgen=require('pptxgenjs'); const D=require('./data.json');
const NAVY='0B1F4B',PINK='E4118A',LIGHT='F5F6FA',INK='0B1F4B',GREY='5B6785',WHITE='FFFFFF';
const pres=new pptxgen(); pres.layout='LAYOUT_16x9'; pres.author='Anaya'; pres.title='Who Holds Under Pressure? RR IPL 2027 Auction';
pres.theme={headFontFace:'Calibri',bodyFontFace:'Calibri'};
const LOGO='rr_logo_small.png';
function base(title,sub,n){const s=pres.addSlide(); s.background={color:LIGHT};
 s.addShape(pres.ShapeType.rect,{x:0,y:0,w:10,h:0.08,fill:{color:PINK},line:{color:PINK}});
 s.addText(title,{x:0.5,y:0.25,w:7.8,h:0.55,fontSize:24,bold:true,color:NAVY,fontFace:'Calibri',margin:0,isTextBox:true});
 if(sub) s.addText(sub,{x:0.5,y:0.8,w:7.8,h:0.3,fontSize:12,color:GREY,margin:0,isTextBox:true});
 s.addImage({path:LOGO,x:9.05,y:0.18,w:0.5,h:0.78});
 s.addText('Created by Anaya  |  SupeRR Selector Season 2, Round 1  |  Independent analysis of the supplied data',{x:0.5,y:5.28,w:8,h:0.22,fontSize:8,color:GREY,margin:0,isTextBox:true});
 s.addText(String(n),{x:9.2,y:5.28,w:0.3,h:0.22,fontSize:8,color:GREY,align:'right',margin:0,isTextBox:true}); return s;}
// 1 title
let s=pres.addSlide(); s.background={color:NAVY};
s.addShape(pres.ShapeType.rect,{x:0,y:0,w:0.18,h:5.625,fill:{color:PINK},line:{color:PINK}});
s.addImage({path:LOGO,x:0.8,y:0.9,w:1.4,h:2.19});
s.addText('WHO HOLDS UNDER PRESSURE?',{x:2.7,y:1.1,w:6.8,h:0.9,fontSize:34,bold:true,color:WHITE,margin:0,isTextBox:true});
s.addText('The most reliable players Rajasthan Royals should back at the IPL 2027 auction',{x:2.7,y:2.1,w:6.6,h:0.8,fontSize:18,color:'FFD3EB',margin:0,isTextBox:true});
s.addText('SupeRR Selector Season 2  |  Round 1',{x:2.7,y:3.2,w:6.5,h:0.3,fontSize:13,bold:true,color:PINK,margin:0,isTextBox:true});
s.addText('Created by Anaya',{x:2.7,y:3.6,w:6.5,h:0.3,fontSize:13,color:WHITE,margin:0,isTextBox:true});
s.addText('201k balls, 867 matches, 355 IPL games (2022 to Nov 2026)',{x:2.7,y:4.9,w:6.5,h:0.25,fontSize:10,color:'A9B4D6',margin:0,isTextBox:true});
// 2 pressure
s=base('How I defined pressure','Built from win probability, not one stat. Every ball gets a leverage score.',2);
const cards=[['Live chase','Innings 2, balls with a leverage index of 1.5 or more (1.0 = average ball). Combines required rate, wickets in hand and balls left.'],
['Rebuild','Innings 1, three or more wickets down inside 10 overs. The batter must repair the innings, not just score.'],
['Death overs','Overs 17 to 20, for bowlers. The batting side is attacking, so every run and wicket moves the result.']];
cards.forEach((c,i)=>{const x=0.5+i*3.05; s.addShape(pres.ShapeType.roundRect,{x,y:1.35,w:2.85,h:2.0,fill:{color:WHITE},line:{color:'DDE2F0',width:1},rectRadius:0.08});
 s.addShape(pres.ShapeType.rect,{x,y:1.35,w:0.07,h:2.0,fill:{color:PINK},line:{color:PINK}});
 s.addText(c[0],{x:x+0.25,y:1.5,w:2.4,h:0.35,fontSize:16,bold:true,color:NAVY,margin:0,isTextBox:true});
 s.addText(c[1],{x:x+0.25,y:1.95,w:2.45,h:1.3,fontSize:11.5,color:GREY,margin:0,valign:'top',isTextBox:true});});
s.addShape(pres.ShapeType.rect,{x:0.5,y:3.6,w:9,h:1.45,fill:{color:NAVY},line:{color:NAVY}});
s.addText([{text:'Rating logic. ',options:{bold:true,color:PINK}},{text:'Each player is scored on pressure balls only against an IPL-vs-T20I over-by-over baseline, then shrunk toward the average for small samples. Batters: boundary rate, runs above expected, dismissal rate, dot balls, win probability added. Bowlers: economy, wickets, dots, boundaries conceded. Eligibility: 100+ pressure balls (batters), 150+ (bowlers), active since mid-2025.',options:{color:WHITE}}],{x:0.7,y:3.7,w:8.6,h:1.25,fontSize:11.5,margin:0,valign:'middle',isTextBox:true});
// 3 validation
s=base('What can we trust? I tested it','Pressure form from 2022 to mid-2024 vs the same players after. Higher = more repeatable.',3);
s.addChart(pres.charts.BAR,[{name:'Repeatability (r)',labels:['Boundary rate','Runs per ball','Runs above expected','Win prob. added'],values:[0.53,0.38,0.25,0.05]}],
 {x:0.5,y:1.3,w:5.6,h:3.7,barDir:'bar',chartColors:[PINK],showValue:true,dataLabelFormatCode:'0.00',dataLabelColor:NAVY,dataLabelFontSize:12,catAxisLabelColor:NAVY,catAxisLabelFontSize:12,valAxisHidden:true,valGridLine:{style:'none'},catGridLine:{style:'none'},showLegend:false,catAxisOrientation:'maxMin'});
s.addShape(pres.ShapeType.roundRect,{x:6.4,y:1.35,w:3.1,h:3.6,fill:{color:WHITE},line:{color:'DDE2F0',width:1},rectRadius:0.08});
s.addText([{text:'So the ranking leans on repeatable skill.',options:{bold:true,color:NAVY,breakLine:true}},{text:'Boundary and scoring rate carry most weight. Win probability added carries little, because on its own it is mostly noise.',options:{color:GREY,breakLine:true}},{text:' ',options:{breakLine:true}},{text:'A 75/25 blend of pressure and overall form predicted later pressure play best.',options:{color:GREY,breakLine:true}},{text:' ',options:{breakLine:true}},{text:'Bowling is noisier: the composite repeats at r = 0.16. Treat these as the best bets, not guarantees.',options:{color:PINK,bold:true}}],{x:6.6,y:1.5,w:2.75,h:3.3,fontSize:12,margin:0,valign:'top',isTextBox:true});
// 4 RR gaps
s=base('Where Rajasthan Royals need help','Rank among the 10 IPL teams, 2022 to 2026 (1 = best).',4);
const H=(t)=>({text:t,options:{bold:true,color:WHITE,fill:{color:NAVY},align:'center',fontSize:12}});
const cell=(v,bad)=>({text:String(v),options:{align:'center',fontSize:14,bold:true,color:bad?WHITE:NAVY,fill:{color:bad?PINK:WHITE}}});
const rows=[[H('Phase'),H('Batting runs'),H('Bowling economy'),H('Bowling wickets')],
 [{text:'Powerplay',options:{bold:true,color:NAVY,fontSize:13}},cell('1st'),cell('1st'),cell('5th')],
 [{text:'Middle overs',options:{bold:true,color:NAVY,fontSize:13}},cell('8th'),cell('6th'),cell('10th',true)],
 [{text:'Death overs',options:{bold:true,color:NAVY,fontSize:13}},cell('6th'),cell('5th'),cell('9th',true)]];
s.addTable(rows,{x:0.5,y:1.35,w:5.6,colW:[1.6,1.3,1.4,1.3],rowH:0.6,border:{type:'solid',color:'DDE2F0',pt:1}});
s.addShape(pres.ShapeType.roundRect,{x:6.4,y:1.35,w:3.1,h:2.4,fill:{color:NAVY},line:{color:NAVY},rectRadius:0.08});
s.addText([{text:'The gap is strike power.',options:{bold:true,color:PINK,fontSize:15,breakLine:true}},{text:'Royals contain runs and chase well (1st for strike rate and economy in live chases) but take wickets slowest in the middle overs and near last at the death.',options:{color:WHITE,fontSize:12}}],{x:6.6,y:1.5,w:2.75,h:2.15,margin:0,valign:'top',isTextBox:true});
s.addText('Also: Hetmyer was released, leaving the finisher role open. Parag (SR 140) and Jurel (SR 133) are steady, not explosive, under pressure.',{x:0.5,y:3.95,w:9,h:0.6,fontSize:12,color:GREY,margin:0,isTextBox:true});
// 5 board
s=base('Auction board: top 10 available players','All retained players removed (official lists, 17 Nov). Pakistani players excluded: not eligible for the IPL.',5);
function tbl(items,cols,x,w,head){const r=[[{text:head,options:{bold:true,color:WHITE,fill:{color:PINK},colspan:cols.length,fontSize:12}}]]; r.push(cols.map(c=>({text:c,options:{bold:true,color:WHITE,fill:{color:NAVY},fontSize:9}})));
 items.forEach((it,i)=>r.push(it.map((v,j)=>({text:String(v),options:{fontSize:9.5,color:NAVY,bold:j<2,fill:{color:i%2?LIGHT:WHITE}}})))); return r;}
const bt=D.bat.map((p,i)=>[i+1,p.name,p.status,p.balls,p.sr,p.bnd+'%']);
const bw=D.bow.map((p,i)=>[i+1,p.name,p.status,p.balls,p.econ,p.wk4]);
s.addTable(tbl(bt,['#','Batter','Status','Balls','SR','Bnd%'],0,4.4,'TOP 10 BATTERS (pressure)'),{x:0.4,y:1.3,w:4.55,colW:[0.4,1.3,1.0,0.5,0.65,0.7],rowH:0.27,border:{type:'solid',color:'DDE2F0',pt:0.5}});
s.addTable(tbl(bw,['#','Bowler','Status','Balls','Econ','Wkts/4ov'],0,4.4,'TOP 10 BOWLERS (pressure)'),{x:5.05,y:1.3,w:4.55,colW:[0.4,1.35,0.95,0.5,0.6,0.75],rowH:0.27,border:{type:'solid',color:'DDE2F0',pt:0.5}});
s.addText('Raw pressure figures shown; the ranking uses sample-size-shrunk scores. Unattached players may not register for the auction.',{x:0.4,y:4.95,w:9.2,h:0.3,fontSize:9,color:GREY,margin:0,isTextBox:true});
// 6 who to back
s=base('Who to back, and how each strengthens RR','Three overseas slots, 6 places, Rs 27.05 cr. Priority order.',6);
const P=[['1. Matheesha Pathirana','Death overs','490 pressure balls, 2.3 wickets per 4 overs, 409 death-over balls at econ 9.3. Gives Royals the death-over strike bowler they lack.'],
['2. Wanindu Hasaranga','Middle-over leg-spin','Econ 8.5, 2.1 wickets per 4 overs; IPL pressure econ 8.4. Attacks the worst-ranked area: middle-over wickets.'],
['3. Pathum Nissanka','No. 3 batter','Biggest pressure sample in the pool (556 balls), SR 149, 21% boundaries. Lets Parag move to 4 and Jurel to 5.'],
['4. Rahul Tripathi','Indian middle order','SR 141, 21% boundaries over 231 balls. Adds depth with no overseas slot used.'],
['5. Bethell or Maxwell','Finisher cover','Replaces Hetmyer: Maxwell SR 149 (240 balls), Bethell SR 140 (144 balls). Pick on price.'],
['Fallback: Theekshana','Spin','Econ 7.35 over 578 balls. The cheaper alternative if Hasaranga gets expensive.']];
P.forEach((p,i)=>{const col=i%2,row=Math.floor(i/2); const x=0.5+col*4.6,y=1.3+row*1.3;
 s.addShape(pres.ShapeType.roundRect,{x,y,w:4.4,h:1.18,fill:{color:WHITE},line:{color:'DDE2F0',width:1},rectRadius:0.06});
 s.addShape(pres.ShapeType.rect,{x,y,w:0.07,h:1.18,fill:{color:i<3?PINK:NAVY},line:{color:i<3?PINK:NAVY}});
 s.addText([{text:p[0],options:{bold:true,color:NAVY,fontSize:13}},{text:'   '+p[1],options:{color:PINK,fontSize:10,bold:true,breakLine:true}},{text:p[2],options:{color:GREY,fontSize:10}}],{x:x+0.2,y:y+0.08,w:4.1,h:1.02,margin:0,valign:'top',isTextBox:true});});
// 7 squad
s=base('Proposed squad and risks','19 retained + 3 overseas buys + 3 flexible spots. Overseas cap reached at 8.',7);
s.addShape(pres.ShapeType.roundRect,{x:0.5,y:1.3,w:5.4,h:3.7,fill:{color:NAVY},line:{color:NAVY},rectRadius:0.08});
s.addText([{text:'LIKELY XI',options:{bold:true,color:PINK,fontSize:12,breakLine:true}},{text:'Jaiswal, Sooryavanshi, Nissanka, Parag, Jurel, Jadeja, Hasaranga, Archer, Pathirana, Shami, Sandeep Sharma',options:{color:WHITE,fontSize:15,breakLine:true}},{text:' ',options:{breakLine:true}},{text:'BENCH / IMPACT',options:{bold:true,color:PINK,fontSize:12,breakLine:true}},{text:'Burger, Ferreira, Shanaka, Bishnoi, Tripathi',options:{color:WHITE,fontSize:15,breakLine:true}},{text:' ',options:{breakLine:true}},{text:'Overseas in XI: Nissanka, Hasaranga, Archer, Pathirana (4).',options:{color:'FFD3EB',fontSize:13}}],{x:0.75,y:1.5,w:4.9,h:3.3,margin:0,valign:'top',isTextBox:true});
s.addShape(pres.ShapeType.roundRect,{x:6.2,y:1.3,w:3.3,h:3.7,fill:{color:WHITE},line:{color:'DDE2F0',width:1},rectRadius:0.08});
s.addText([{text:'RISKS TO CHECK',options:{bold:true,color:PINK,fontSize:12,breakLine:true}},{text:'Fitness: Pathirana played 1 of 13 for KKR in 2026; Hasaranga none for LSG.',options:{color:NAVY,fontSize:12,breakLine:true}},{text:' ',options:{breakLine:true}},{text:'Price: Rs 27.05 cr is tight if both go high.',options:{color:NAVY,fontSize:12,breakLine:true}},{text:' ',options:{breakLine:true}},{text:'Small samples: Sooryavanshi, Ferreira, Dubey under 200 balls.',options:{color:NAVY,fontSize:12,breakLine:true}},{text:' ',options:{breakLine:true}},{text:'Registration: unattached players may not enter the auction.',options:{color:NAVY,fontSize:12}}],{x:6.4,y:1.5,w:2.95,h:3.4,margin:0,valign:'top',isTextBox:true});
pres.writeFile({fileName:'/mnt/user-data/outputs/RR_Pressure_Players_IPL2027.pptx'}).then(()=>console.log('ok'));
