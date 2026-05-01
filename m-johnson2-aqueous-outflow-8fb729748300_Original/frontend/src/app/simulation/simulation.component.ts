import { Component, Inject, OnInit } from '@angular/core';
import { Conditions, defaultTMSegs } from "./conditions.model";
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA, MatSnackBar } from "@angular/material";
import { EditConstantsDialogComponent } from "../edit-constants-dialog/edit-constants-dialog.component";
import { Sinusotomy } from "./sinusotomy.model";
import { StentInfo } from "./stent-info.model";
import { SolverService } from "../solver.service";
import {CC, CCwIndex, EditCCSignal} from "./cc.model";
import { CCDistribution } from "./cc-distribution.model";
import { CreateStentDialogComponent } from "../create-stent-dialog/create-stent-dialog.component";
import {SurgArc, Circle, TMArc, SCArc} from "../interfaces";
import { transition, trigger, style, animate } from "@angular/animations";
import {IOP2RTM, IOP2RTM_QU} from "./iop-rtm-correlation";
import { FormArray, FormControl, FormGroup, Validators } from "@angular/forms";
import { environment } from "../env"
import { isString } from "util";
import {EditCcDialogComponent} from "../edit-cc-dialog/edit-cc-dialog.component";

const DEFAULT_CIRCLE_PROPS: Circle = {
  radius: 149,
  strokeWidth: 41,
  centerX: 205,
  centerY: 205
};

@Component({
  selector: 'app-simulation',
  templateUrl: './simulation.component.html',
  styleUrls: ['./simulation.component.scss'],
  animations: [trigger('addRemove', [
    transition(':enter', [
      style({ transform: 'translateY(-40px)', height: '0px', minHeight: '0', opacity: 0 }),
      animate('0.4s 0.1s ease-in-out', style({ transform: 'translateY(0px)', height: '*', opacity: 1 }))
    ]),
    transition(':leave', [
      style({ transform: 'translateY(0px)', height: '*', opacity: 1 }),
      animate('0.4s 0.1s ease-in-out', style({ transform: 'translateY(-40px)', height: '0px', minHeight: '0', opacity: 0 }))
    ])
  ])]
})
export class SimulationComponent implements OnInit {

  default_cc_dist: CCDistribution;

  public env = environment;
  public circleProps: Circle;

  private oldConditions: string;

  public conditionsForm: FormGroup;

  public surgArcs: SurgArc[];

  public tmArcs: TMArc[];
  public scArcs: SCArc[];
  public ccLines: CCwIndex[];

  public errorMessage = '';

  public stentOptions = [
    new StentInfo('Windowless Bidirectional Stent', 2000.0, 0.0, 150.0, 50.0, undefined, undefined, undefined, undefined, undefined, undefined, undefined, true, 'ellipse'),
    new StentInfo('Windowless Unidirectional Stent', 2000.0, 0.0, 150.0, 50.0, undefined, undefined, undefined, undefined, undefined, undefined, undefined, false),
    new StentInfo('Windowed Bidirectional Stent', 2500.0, 0.0, 150.0, undefined, 2, 500, 50, 500, 50, undefined, undefined, true, 'ellipse'),
    new StentInfo('Windowed Unidirectional Stent', 2500.0, 0.0, 150.0, undefined, 2, 500, 50, 500, 50, undefined, undefined, false)
  ];

  constructor(public dialog: MatDialog, private solverService: SolverService) {
    this.default_cc_dist = new CCDistribution();
    this.circleProps = DEFAULT_CIRCLE_PROPS;
    this.oldConditions = JSON.stringify(this.env.conditions);
    this.conditionsForm = new FormGroup({
      mode: new FormControl('constant flow', Validators.pattern('constant (flow|pressure)')),
      iop: new FormControl(15.09, Validators.min(this.env.conditions.constants.pev)),
      qt: new FormControl(2),
      geometry: new FormControl('ellipse', Validators.pattern('(ellipse|rectangle)')),
      unconventional: new FormControl(false),
      variable_rtm: new FormControl(false),
      trabeculotomies: new FormArray([]),
      stents: new FormArray([]),
      sinusotomies: new FormArray([]),
      ccs: new FormArray([]),
      rtm: new FormArray([]),
      h0: new FormArray([]),
      constants: new FormControl(this.env.conditions.constants)
    });
    this.toControls()
  }

  ngOnInit() {
    this.calcRtm()
  }

  toControls() {
    let trabControls = this.conditionsForm.get('trabeculotomies') as FormArray
    for (let trab of this.env.conditions.trabeculotomies) {
      trabControls.push(new FormGroup({
        start: new FormControl(trab.start, [
          Validators.min(0),
          Validators.max(195),
          Validators.required
        ]),
        end: new FormControl(trab.end, [
          Validators.min(165),
          Validators.max(360),
          Validators.required
        ])
      }));
    }

    let sinusControls = this.conditionsForm.get('sinusotomies') as FormArray
    for (let sinus of this.env.conditions.sinusotomies) {
      sinusControls.push(new FormGroup({
        start: new FormControl(sinus.start, [
          Validators.min(0),
          Validators.max(195),
          Validators.required
        ]),
        end: new FormControl(sinus.end, [
          Validators.min(165),
          Validators.max(360),
          Validators.required
        ])
      }));
    }

    let stentControls = this.conditionsForm.get('stents') as FormArray;
    for (let stent of this.env.conditions.stents) {
      stentControls.push(new FormGroup({
        stent: new FormControl(stent.stent),
        loc: new FormControl(stent.loc, [
          Validators.max(360 - (stent.stent.length / 100)),
          Validators.min(0),
          Validators.required
        ])
      }));
    }

    let tmControls = this.conditionsForm.get('rtm') as FormArray;
    for (let i in this.env.conditions.rtm) {
      let index = Number(i);
      if (this.env.conditions.variable_rtm) {
        tmControls.setControl(index, new FormGroup({
          hour: new FormControl(this.env.conditions.rtm[index].hour),
          resistance: new FormControl(this.env.conditions.rtm[index].resistance, [
            Validators.min(0),
            Validators.required
          ])
        }));
      } else {
        tmControls.setControl(index, new FormGroup({
          hour: new FormControl(this.env.conditions.rtm[index].hour),
          resistance: new FormControl(this.env.conditions.constants.rtm * 12, [
            Validators.min(0),
            Validators.required
          ])
        }));
      }

    }

    let scControls = this.conditionsForm.get('h0') as FormArray;
    for (let i in this.env.conditions.h0) {
      let index = Number(i);
      if (this.env.conditions.variable_h0) {
        scControls.setControl(index, new FormGroup({
          seg: new FormControl(this.env.conditions.h0[index].seg),
          height: new FormControl(this.env.conditions.h0[index].height, [
            Validators.min(0),
            Validators.required
          ])
        }));
      } else {
        scControls.setControl(index, new FormGroup({
          seg: new FormControl(this.env.conditions.h0[index].seg),
          height: new FormControl(this.env.conditions.constants.h0, [
            Validators.min(0),
            Validators.required
          ])
        }));
      }

    }

    let ccControls = this.conditionsForm.get('ccs') as FormArray;
    for (let i in this.env.conditions.ccs) {
      let index = Number(i);
      ccControls.setControl(index, new FormGroup({
        loc: new FormControl(this.env.conditions.ccs[index].loc, [
          Validators.min(0),
          Validators.max(360),
          Validators.required
        ]),
        g_ratio: new FormControl(this.env.conditions.ccs[index].g_ratio, [
          Validators.min(0),
          Validators.required
        ])
      }));
    }

    this.toSurgArcs();
    this.toTMArcs();
    this.toSCArcs();
    this.toCCLines();
  }

  toSurgArcs() {
    let trabInd = 0;
    let trabeculotomies = this.conditionsForm.get('trabeculotomies') as FormArray;
    let sinusInd = 0;
    let sinusotomies = this.conditionsForm.get('sinusotomies') as FormArray;
    let stentInd = 0;
    let stents = this.conditionsForm.get('stents') as FormArray;
    let absIndex = 0;
    this.surgArcs = [];
    if (trabeculotomies.length > 0) {
      for (let trab of trabeculotomies.controls as FormGroup[]) {

        if (!isNaN(trab.get('start').value) && !isNaN(trab.get('end').value)) {
          if (trab.get('start').valid && trab.get('end').valid) {
            trab.setControl('start', new FormControl(trab.get('start').value, [
              Validators.min(0),
              Validators.max(trab.get('end').value)
            ]));
            trab.setControl('end', new FormControl(trab.get('end').value, [
              Validators.min(trab.get('start').value),
              Validators.max(360)
            ]));
            this.surgArcs.push({
              angleStart: (trab.get('start').value) * Math.PI / 180,
              angleStop: (trab.get('end').value) * Math.PI / 180,
              color: "#ab000d",
              type: "Trabeculectomy",
              surgIndex: trabInd,
              arcIndex: absIndex,
              strokeWidth: 5
            });
          }
          trabInd += 1;
          absIndex += 1;
        }
      }
    }
    if (sinusotomies.length > 0) {
      for (let sinus of sinusotomies.controls as FormGroup[]) {
        if (!isNaN(sinus.get('start').value) && !isNaN(sinus.get('end').value)) {
          if (sinus.get('start').valid && sinus.get('end').valid) {
            sinus.setControl('start', new FormControl(sinus.get('start').value, [
              Validators.min(0),
              Validators.max(sinus.get('end').value)
            ]));
            sinus.setControl('end', new FormControl(sinus.get('end').value, [
              Validators.min(sinus.get('start').value),
              Validators.max(360)
            ]));
            this.surgArcs.push({
              angleStart: (sinus.get('start').value) * Math.PI / 180,
              angleStop: (sinus.get('end').value) * Math.PI / 180,
              color: "#1e88e5",
              type: "Sinusotomy",
              surgIndex: sinusInd,
              arcIndex: absIndex,
              strokeWidth: 5
            });
          }
          sinusInd += 1;
          absIndex += 1;
        }
      }
    }
    if (stents.length > 0) {
      for (let stent of stents.controls as FormGroup[]) {
        if (!isNaN(stent.get('loc').value)) {
          if (stent.get('loc').valid) {
            stent.setControl('loc', new FormControl(stent.get('loc').value, [
              Validators.max(360 - (stent.get('stent').value.length / 100)),
              Validators.min(0)
            ]));
            this.surgArcs.push({
              angleStart: stent.get('loc').value * Math.PI / 180,
              angleStop: (stent.get('loc').value + (stent.get('stent').value.length / 100)) * Math.PI / 180,
              color: "#fdd835",
              type: stent.get('stent').value.name,
              surgIndex: stentInd,
              arcIndex: absIndex,
              lengthLocked: true,
              strokeWidth: 5
            });
          }
          stentInd += 1;
          absIndex += 1;
        }
      }
    }
    this.env.conditions = this.conditionsForm.value;
  }

  toTMArcs() {
    let tmSegments = this.conditionsForm.get('rtm') as FormArray;
    this.tmArcs = [];
    for (let seg of tmSegments.controls as FormGroup[]) {
      this.tmArcs.push({
        hour: seg.get('hour').value,
        resistance: seg.get('resistance').value,
      });
    }
    this.env.conditions.rtm = this.tmArcs;
    this.checkVariableRtm();
  }

  toSCArcs() {
    let scSegments = this.conditionsForm.get('h0') as FormArray;
    this.scArcs = [];
    for (let seg of scSegments.controls as FormGroup[]) {
      this.scArcs.push({
        seg: seg.get('seg').value,
        height: seg.get('height').value,
      });
    }
    this.env.conditions.h0 = this.scArcs;
    this.checkVariableH0();
  }

  toCCLines() {
    let ccs = this.conditionsForm.get('ccs') as FormArray;
    this.ccLines = [];
    let index = 0;
    for (let cc of ccs.controls as FormGroup[]) {
      this.ccLines.push({
        index: index,
        cc: {
          loc: cc.get('loc').value,
          g_ratio: cc.get('g_ratio').value
        }
      });
      index = index + 1;
    }
    this.env.conditions.ccs = ccs.value;
    this.checkUniformCCs();
  }

  checkVariableRtm() {
    let res = this.tmArcs[0].resistance;
    let uniform = true;
    for (let seg of this.tmArcs) {
      if (seg.resistance != res) {
        uniform = false;
        break;
      }
    }
    if (uniform) {
      this.conditionsForm.setControl('variable_rtm', new FormControl(false));
      this.env.conditions.variable_rtm = false;
      this.env.conditions.constants.rtm = res / 12;
      this.conditionsForm.setControl('constants', new FormControl(this.env.conditions.constants));
      this.conditionsForm.get('iop').enable();
    } else {
      this.conditionsForm.setControl('variable_rtm', new FormControl(true));
      this.env.conditions.variable_rtm = true;
      this.conditionsForm.get('iop').disable();
    }
  }

  checkVariableH0() {
    let h = this.scArcs[0].height;
    let uniform = true;
    for (let seg of this.scArcs) {
      if (seg.height != h) {
        uniform = false;
        break;
      }
    }
    if (uniform) {
      this.conditionsForm.setControl('variable_h0', new FormControl(false));
      this.env.conditions.variable_h0 = false;
      this.env.conditions.constants.h0 = h;
      this.conditionsForm.setControl('constants', new FormControl(this.env.conditions.constants));
      this.conditionsForm.get('iop').enable();
    } else {
      this.conditionsForm.setControl('variable_h0', new FormControl(true));
      this.env.conditions.variable_h0 = true;
      this.conditionsForm.get('iop').disable();
    }
  }

  checkUniformCCs() {
    let uniform = true;
    if (this.ccLines.length == this.default_cc_dist.ccs.length) {
      for (let cc of this.ccLines) {
        if (cc.cc.loc != this.default_cc_dist.ccs[cc.index].loc || cc.cc.g_ratio != this.default_cc_dist.ccs[cc.index].g_ratio) {
          uniform = false;
        } else {
          continue;
        }
      }
    } else {
      uniform = false;
    }

    if (uniform) {
      this.conditionsForm.get('iop').enable();
    } else {
      this.conditionsForm.get('iop').disable();
    }
  }

  calcRtm(): void {
    let corr = IOP2RTM;
    if (this.conditionsForm.get('unconventional').value) {
      corr = IOP2RTM_QU;
    }
    let iop = this.conditionsForm.get('iop');
    if (iop.enabled) {
      this.env.conditions.iop = iop.value;
      for (let reg of corr) {
        if (this.env.conditions.iop <= reg.iop_max && this.env.conditions.iop > reg.iop_min) {
          this.env.conditions.constants.rtm = Number((reg.slope * (this.env.conditions.iop - reg.iop_min) + reg.rtm_min).toFixed(2));
          break;
        } else {
          continue;
        }
      }
    }

    let tmControls = this.conditionsForm.get('rtm') as FormArray;
    for (let i in this.env.conditions.rtm) {
      let index = Number(i);
      if (this.env.conditions.variable_rtm) {
        tmControls.setControl(index, new FormGroup({
          hour: new FormControl(this.env.conditions.rtm[index].hour),
          resistance: new FormControl(this.env.conditions.rtm[index].resistance, [
            Validators.min(0),
            Validators.required
          ])
        }));
      } else {
        tmControls.setControl(index, new FormGroup({
          hour: new FormControl(this.env.conditions.rtm[index].hour),
          resistance: new FormControl(this.env.conditions.constants.rtm * 12, [
            Validators.min(0),
            Validators.required
          ])
        }));
      }

    }

    let scControls = this.conditionsForm.get('h0') as FormArray;
    for (let i in this.env.conditions.h0) {
      let index = Number(i);
      if (this.env.conditions.variable_h0) {
        scControls.setControl(index, new FormGroup({
          seg: new FormControl(this.env.conditions.h0[index].seg),
          height: new FormControl(this.env.conditions.h0[index].height, [
            Validators.min(0),
            Validators.required
          ])
        }));
      } else {
        scControls.setControl(index, new FormGroup({
          seg: new FormControl(this.env.conditions.h0[index].seg),
          height: new FormControl(this.env.conditions.constants.h0, [
            Validators.min(0),
            Validators.required
          ])
        }));
      }

    }
  }

  calcIOP(): void {
    let corr = IOP2RTM;
    if (this.conditionsForm.get('unconventional').value) {
      corr = IOP2RTM_QU;
    }
    let iop = this.conditionsForm.get('iop')
    if (iop.enabled) {
      console.log("finding IOP...")
      for (let reg of corr) {
        if (this.env.conditions.constants.rtm <= reg.rtm_max && this.env.conditions.constants.rtm > reg.rtm_min) {
          this.env.conditions.iop = Number(((1 / reg.slope) * (this.env.conditions.constants.rtm - reg.rtm_min) + reg.iop_min).toFixed(2));
          console.log(`IOP = ${this.env.conditions.iop} mmHg`)
          this.conditionsForm.setControl("iop", new FormControl(this.env.conditions.iop, [Validators.min(this.env.conditions.constants.pev)]))
          break;
        } else {
          continue;
        }
      }
    }

    let tmControls = this.conditionsForm.get('rtm') as FormArray;
    for (let i in this.env.conditions.rtm) {
      let index = Number(i);
      if (this.env.conditions.variable_rtm) {
        tmControls.setControl(index, new FormGroup({
          hour: new FormControl(this.env.conditions.rtm[index].hour),
          resistance: new FormControl(this.env.conditions.rtm[index].resistance, [
            Validators.min(0),
            Validators.required
          ])
        }));
      } else {
        tmControls.setControl(index, new FormGroup({
          hour: new FormControl(this.env.conditions.rtm[index].hour),
          resistance: new FormControl(this.env.conditions.constants.rtm * 12, [
            Validators.min(0),
            Validators.required
          ])
        }));
      }

    }

    let scControls = this.conditionsForm.get('h0') as FormArray;
    for (let i in this.env.conditions.h0) {
      let index = Number(i);
      if (this.env.conditions.variable_h0) {
        scControls.setControl(index, new FormGroup({
          seg: new FormControl(this.env.conditions.h0[index].seg),
          height: new FormControl(this.env.conditions.h0[index].height, [
            Validators.min(0),
            Validators.required
          ])
        }));
      } else {
        scControls.setControl(index, new FormGroup({
          seg: new FormControl(this.env.conditions.h0[index].seg),
          height: new FormControl(this.env.conditions.constants.h0, [
            Validators.min(0),
            Validators.required
          ])
        }));
      }

    }
  }

  toTMControl(arc: TMArc) {
    let tmSegments = this.conditionsForm.get('rtm') as FormArray;
    let seg = tmSegments.at(arc.hour - 1) as FormGroup;
    seg.setControl('resistance', new FormControl(arc.resistance, [
      Validators.min(0),
      Validators.required
    ]));
    this.toTMArcs();
  }

  toSCControl(arc: SCArc) {
    let scSegments = this.conditionsForm.get('h0') as FormArray;
    let seg = scSegments.at(arc.seg - 1) as FormGroup;
    seg.setControl('height', new FormControl(arc.height, [
      Validators.min(0),
      Validators.required
    ]));
    this.toSCArcs();
  }

  toCCControl(edit: EditCCSignal) {
    let ccs = this.conditionsForm.get('ccs') as FormArray;
    if (edit.delete) {
      ccs.removeAt(edit.data);
    } else {
      let line = edit.data;
      let cc = ccs.at(line.index) as FormGroup;
      cc.setControl('loc', new FormControl(line.cc.loc, [
        Validators.min(0),
        Validators.max(360),
        Validators.required
      ]));
      cc.setControl('g_ratio', new FormControl(line.cc.g_ratio, [
        Validators.min(0),
        Validators.required
      ]));
    }
    this.toCCLines();
  }

  addCC(): void {
    let newCC = {
      index: this.ccLines[this.ccLines.length - 1].index + 1,
      cc: {
        loc: null,
        g_ratio: null
      }
    };
    const dialogRef = this.dialog.open(EditCcDialogComponent, {
      data: newCC
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result != null) {
        if (!result.delete) {
          let ccControls = this.conditionsForm.get('ccs') as FormArray;
          ccControls.push(new FormGroup({
            loc: new FormControl(result.data.cc.loc, [
              Validators.min(0),
              Validators.max(360),
              Validators.required
            ]),
            g_ratio: new FormControl(result.data.cc.g_ratio, [
              Validators.min(0),
              Validators.required
            ])
          }));
          this.toCCLines();
        }
      }
    });
  }

  toSurgery(arc: SurgArc) {
    let trabeculotomies = this.conditionsForm.get('trabeculotomies') as FormArray;
    let sinusotomies = this.conditionsForm.get('sinusotomies') as FormArray;
    let stents = this.conditionsForm.get('stents') as FormArray;
    if (arc.type == "Trabeculectomy") {
      let trab = trabeculotomies.at(arc.surgIndex) as FormGroup;
      trab.setControl('start', new FormControl(Math.round(arc.angleStart * 1800 / Math.PI) / 10, [
        Validators.min(0),
        Validators.max(Math.round(arc.angleStop * 1800 / Math.PI) / 10),
        Validators.required
      ]));
      trab.setControl('end', new FormControl(Math.round(arc.angleStop * 1800 / Math.PI) / 10, [
        Validators.min(trab.get('start').value),
        Validators.max(360),
        Validators.required
      ]));
    } else if (arc.type == "Sinusotomy") {
      let sinus = sinusotomies.at(arc.surgIndex) as FormGroup;
      sinus.setControl('start', new FormControl(Math.round(arc.angleStart * 1800 / Math.PI) / 10, [
        Validators.min(0),
        Validators.max(Math.round(arc.angleStop * 1800 / Math.PI) / 10),
        Validators.required
      ]));
      sinus.setControl('end', new FormControl(Math.round(arc.angleStop * 1800 / Math.PI) / 10, [
        Validators.min(sinus.get('start').value),
        Validators.max(360),
        Validators.required
      ]));
    } else {
      let stent = stents.at(arc.surgIndex) as FormGroup;
      stent.setControl('loc', new FormControl(Math.round(arc.angleStart * 1800 / Math.PI) / 10, [
        Validators.max(360 - (stent.get('stent').value.length / 100)),
        Validators.min(0),
        Validators.required
      ]));
    }
    this.env.conditions = this.conditionsForm.value;
  }

  addTrabeculotomy(): void {
    let trabControls = this.conditionsForm.get('trabeculotomies') as FormArray;
    trabControls.push(new FormGroup({
      start: new FormControl(165, [
        Validators.min(0),
        Validators.max(195),
        Validators.required
      ]),
      end: new FormControl(195, [
        Validators.min(165),
        Validators.max(360),
        Validators.required
      ])
    }));
    this.toSurgArcs();
  }

  deleteTrabeculotomy(i): void {
    let trabeculotomies = this.conditionsForm.get('trabeculotomies') as FormArray;
    trabeculotomies.removeAt(i);
    this.toSurgArcs();
  }

  addSinusotomy(): void {
    let sinusControls = this.conditionsForm.get('sinusotomies') as FormArray;
    sinusControls.push(new FormGroup({
      start: new FormControl(165, [
        Validators.min(0),
        Validators.max(195),
        Validators.required
      ]),
      end: new FormControl(195, [
        Validators.min(165),
        Validators.max(360),
        Validators.required
      ])
    }));
    this.toSurgArcs();
  }

  deleteSinusotomy(i): void {
    let sinusotomies = this.conditionsForm.get('sinusotomies') as FormArray;
    sinusotomies.removeAt(i);
    this.toSurgArcs();
  }

  addStent(): void {
    let stentControls = this.conditionsForm.get('stents') as FormArray;
    stentControls.push(new FormGroup({
      stent: new FormControl(this.stentOptions[0]),
      loc: new FormControl(180, [
        Validators.max(360 - (this.stentOptions[0].length / 100)),
        Validators.min(0),
        Validators.required
      ])
    }));
    this.toSurgArcs();
  }

  deleteStent(i): void {
    let stents = this.conditionsForm.get('stents') as FormArray;
    stents.removeAt(i);
    this.toSurgArcs();
  }

  newStent(i): void {
    const dialogRef = this.dialog.open(CreateStentDialogComponent);

    dialogRef.afterClosed().subscribe(result => {
      if (result != null) {
        this.stentOptions.push(result);
        let stents = this.conditionsForm.get('stents') as FormArray;
        let stent = stents.at(i) as FormGroup;
        stent.get('stent').setValue(result);
        stent.setControl('loc', new FormControl(180, [
              Validators.max(360 - (stent.get('stent').value.length / 100)),
              Validators.min(0),
              Validators.required
        ]));
        this.toSurgArcs();
      }
    })
  }

  editParams(): void {
    this.env.conditions = this.conditionsForm.value;
    const dialogRef = this.dialog.open(EditConstantsDialogComponent, {
      data: this.env.conditions
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result != null) {
        this.env.conditions = result;
        if (this.env.conditions.constants.pev != 8.0 || this.conditionsForm.get('qt').value != 2.0 || (this.conditionsForm.get('unconventional').value && this.env.conditions.constants.qu != 0.28)) {
          this.conditionsForm.get('iop').disable();
        } else {
          this.conditionsForm.get('iop').enable();
          this.calcIOP();
          this.conditionsForm.setControl('iop', new FormControl(this.env.conditions.iop, Validators.min(this.env.conditions.constants.pev)));
        }
      }
    });
  }

  resetToBaseline(): void {
    this.env.conditions = new Conditions('constant flow');
    this.conditionsForm = new FormGroup({
      mode: new FormControl('constant flow', Validators.pattern('constant (flow|pressure)')),
      iop: new FormControl(15.09, Validators.min(this.env.conditions.constants.pev)),
      qt: new FormControl(2),
      geometry: new FormControl('ellipse', Validators.pattern('(ellipse|rectangle)')),
      unconventional: new FormControl(false),
      trabeculotomies: new FormArray([]),
      stents: new FormArray([]),
      sinusotomies: new FormArray([]),
      ccs: new FormArray([]),
      rtm: new FormArray([]),
      h0: new FormArray([]),
      constants: new FormControl(this.env.conditions.constants)
    });
    this.toControls();
    this.calcRtm();
    this.conditionsForm.get('iop').enable();
    this.env.solving = false;
    this.env.solved = false;
    this.env.hasSoln = false;
  }

  solve(): void {
    this.env.solving = true;
    this.env.solved = false;
    this.env.conditions = this.conditionsForm.value;
    this.solverService.solve(this.env.conditions)
      .subscribe(sol => {
        this.env.solution = sol;
        this.env.failed = false;
        this.env.solving = false;
        this.env.solved = true;
        this.env.hasSoln = true;
      },error => {
        this.env.failed = true;
        this.env.solving = false;
        console.log(error);
        this.dialog.open(ErrorDialogComponent, {data: error});
        this.env.failed = false;
      });
  }

}

@Component({
  selector: 'error-dialog',
  template: `<h1 mat-dialog-title color="warn">ERROR</h1>
  <mat-dialog-content [innerHtml]="data"></mat-dialog-content>
  <mat-dialog-actions><button mat-button color="primary" [mat-dialog-close]="">Close</button></mat-dialog-actions>`
})
export class ErrorDialogComponent {

  constructor(public dialogRef: MatDialogRef<ErrorDialogComponent>, @Inject(MAT_DIALOG_DATA) public data: any) {
    if (!isString(data[0])) {
      this.data = "An unknown error occurred. Please check that all parameters are valid. In most cases, a red warning message will appear underneath any invalid parameters.";
    }
  }

  onNoClick(): void {
    this.dialogRef.close();
  }
}
