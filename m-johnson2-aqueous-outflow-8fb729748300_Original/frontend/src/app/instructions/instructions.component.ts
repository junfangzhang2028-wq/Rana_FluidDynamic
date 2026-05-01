import { Component, OnInit } from '@angular/core';
import { FlatTreeControl } from "@angular/cdk/tree";
import { MatTreeFlatDataSource, MatTreeFlattener } from "@angular/material";
import { InstructionNode, FlatNode } from "../interfaces";
import { animate, style, transition, trigger } from "@angular/animations";

const INSTRUCTIONS: InstructionNode[] = [
  {
    name: `This model can be used to simulate the effects of a variety of different conditions the aqueous outflow
        pathway might be subjected to by altering the various options available from the <b>Simulations</b> page.
        Included below are instructions for common use cases, followed by more specific information about each of the
        options available, and finally, some information about convergence issues.`
  },
  {
    name: 'Use Cases',
    children: [
      {
        name: `Basic Use`,
        children: [
          {name: `The model is ready to be solved with the default parameters immediately upon opening the
          <b>Simulations</b> page. To run it, click the <b>Solve</b> button in the lower right hand corner and the model
          will begin to solve. The default simulation should not take more than a few seconds to solve.`},
          {name: `Once the model has arrived at a solution, the set up diagram will be replaced with the solution
          diagram. The solution diagram displays a heat map representing the pressure distribution throughout Schlemm\'s
          canal with a scale bar on the left that goes from episcleral venous pressure to <b>IOP</b>. Below the diagram
          are two panels. On the left are results for the whole eye: <b>IOP</b>, outflow rate (<b>Flowrate</b>),
          facility, and resistance. On the right, local pressure and canal height can be seen by placing you cursor in
          the location of interest. Additionally, the flowrate through a given collector channel by hovering over said
          collector channel (the <b>&theta;</b>, <b>P<sub>SC</sub></b> and <b>Canal Height</b> values shown pertain to
          the last location in the canal touched by the cursor, not the collector channel being hovered over).`},
          {name: `To switch back from the solution view to the setup view and prepare another simulation, click the
          <b>View Setup</b> button. Note that the solution view will not be updated until a solution has been obtained
          by clicking the <b>Solve</b> button, clicking the <b>View Solution</b> button before solving will show the
          previous solution.`}
        ]
      },
      {
        name: 'Evaluating Glaucoma Procedure Effects',
        children: [
          {name: `To evaluate the expected efficacy of a procedure performed on a given glaucomatous eye, one must first
          match the baseline <b>IOP</b> of the untreated eye. In primary open angle glaucoma, the primary factor
          responsible for elevating <b>IOP</b> is the flow resistance of the trabecular meshwork and inner wall of
          Schlemm's canal, which are collectively represented by the <b>R<sub>TM</sub></b> property, so this is the
          property that will typically be adjusted to match the baseline <b>IOP</b>.`},
          {name: `Changing the <b>Baseline IOP</b> parameter adjusts <b>R<sub>TM</sub></b> such that a simulation with a
          <b>Flowrate</b> of 2 &mu;L/min and <b>P<sub>V</sub></b> (episcleral venous pressure, see
          <b>Edit Constants</b>) of 8 mmHg without any surgeries applied results in the specified <b>Baseline IOP</b>.
          If any parameters (besides <b>R<sub>TM</sub></b> and <b>Baseline IOP</b>) have non-default values, then the
          <b>Baseline IOP</b> option will not work correctly and is therefore disabled. If conditions other than
          the defaults are needed for the baseline, <b>R<sub>TM</sub></b> along with several other model parameters, are
          editable directly from the <b>Edit Constants</b> dialog, but it may require several solution attempts to
          achieve the desired baseline this way.`},
          {name: `Once the baseline simulation has been set up, click the <b>Solve</b> button to ensure that the
          baseline <b>IOP</b> and other results are as desired, then click the <b>View Setup</b> button to switch back
          to the setup view and begin applying the treatment of interest.`},
          {name: `To apply a surgery, click the <mat-icon class="my-icon">add</mat-icon> button next to the desired
          surgery and edit the available fields as desired. For more information about the surgeries available and each
          of their unique options, see the <b>Surgeries</b> section below.`},
          {name: `Once the treatment has been set up, click <b>Solve</b> again. The solution that appears is the
          predicted result of the procedure performed on the specified baseline eye. Try applying different procedures
          to compare the resulting <b>IOP</b> reductions from baseline.`}
        ]
      }
    ]
  },
  {
    name: `Variable Trabecular Meshwork Resistance`,
    children: [{name: `The trabecular meshwork resistance (<b>R<sub>TM</sub></b>) can be changed in two ways. If <b>R<sub>TM</sub></b>`+
      ` is constant around the circumference of the system, the overall resistance can be changed by the <b>R<sub>TM</sub></b>`+
      ` (in <b>Edit Constants</b>) or <b>Baseline IOP</b> parameters. The resistance of each clock hour of trabecular `+
      `meshwork can also be edited individually by clicking on the desired section of the TM. Editing the individual clock `+
      `hours will disable both the <b>R<sub>TM</sub></b> and <b>Baseline IOP</b> fields unless all clock hours have `+
      `equal resistance. Note that since the resistors are in parallel, the overall resistance of the TM is equal to `+
      `1/12th of the resistance of an individual clock hour when all clock hours have equal resistance.`}]
  },
  {
    name: `Variable Schelmm's Canal Height`,
    children: [
      {name: `The undeformed height of Schlemm's canal (<b>h<sub>0</sub></b>) can be changed in two ways. If <b>h<sub>0</sub></b>`+
          ` is constant around the circumference of the system, <b>h<sub>0</sub></b> can be changed by the <b>h<sub>0</sub></b> `+
          `field in <b>Edit Constants</b>. The undeformed canal height can also be made to vary in different regions of the`+
          ` canal by clicking the desired segment of SC and changing the height. Editing the individual sections of SC will`+
          ` disable the <b>h<sub>0</sub></b> field in edit constants.`},
      {name: `Note that by Equation 6 of the paper, changes to <b>h<sub>0</sub></b>`+
          ` will also result in changes to the septae stiffness parameter <b>K<sub>S</sub></b>, whether uniform or variable. `+
          `Changes to <b>h<sub>0</sub></b> and <b>K<sub>S</sub></b>, especially in nonuniform distributions, can result in an unsolvable `+
          `system, so keep this in mind when using this functionality.`}
    ]
  },
  {
    name: `Collector Channel Distribution`,
    children: [
      {name: `Both the location and relative flow conductances of each of the existing collector channels can be edited
          by clicking on the desired collector channel. New collector channels can also be added using the <b>Collector Channel +</b>
          button.`},
      {name: `The <b>Relative Conductance</b> of a given collector channel is the relative contribution of that ` +
          `collector channel to the overall conductance of all of the collector channels. This parameter does not ` +
          `have any affect on the overall conductance of the collector channels (1/R<sub>CC</sub>). <i>Ex:</i> In a network with 29 ` +
          `channels of <b>Relative Conductance</b> 1 and 1 channel of <b>Relative Conductance</b> 2, the channel with a <b>Relative Conductance</b>` +
          ` of 2 has a conductance equal to (2/31)*(1/R<sub>CC</sub>), while the other 29 have conductances of
          (1/31)*(1/R<sub>CC</sub>).`}
    ]
  },
  {
    name: `Surgeries`,
    children: [
      {name: `Surgeries are defined by their angular location (eg. start and end fields in trabeculotomy). The locations
      can be edited with the input fields or by clicking and dragging the black bars on the diagram.`},
      {name: `Note: surgeries may not cross 0&deg;. <i>Ex:</i> a trabeculotomy with start at 345&deg; and end at 15&deg; is
      not a valid input for the model.`},
      {
        name: `Trabeculectomy`,
        children: [
          {name: `In trabeculotomy and trabeculectomy part or all of the trabecular meshwork is removed, and thus to
          model a trabeculotomy, the resistors representing the trabecular meshwork are removed and the adjoining
          Schlemm\'s canal nodes are set to <b>IOP</b>.`},
        ]
      },
      {
        name: `Trabecular Bypass Stents`,
        children: [
          {name: `Stents bypass the trabecular meshwork and also dilate Schlemm\'s canal, and thus they are modeled by
          removing trabecular meshwork resistors corresponding to the inlet of the stent and increasing the height of
          Schlemm\'s canal in the region with the stent.`},
          {name: `To add a stent, click the plus button next to <b>Trabecular Bypass Stents</b> and then select one of
          the provided stents or create a custom stent with <b>Custom Stent</b> option.`},
          {name: `Four example stents are provided. A 2000 &mu;m long windowless stent with a channel height of 50
          &mu;m and width of 150 &mu;m and one 2500 &mu;m long stent with 2 windows (dilated regions of SC that allow
          flow through the TM), a channel height of 50 &mu;m and width of 150 &mu;m, each available as either
          bidirectional or unidirectional. All example stents have inlets located at counterclockwise end of the stent.
          The unidirectional example stents only allow flow to travel clockwise from the inlet`},
          {name: `Custom stents can also be created by selecting the <b>Create Stent</b> option in the dropdown menu. For
          more information on the editable parameters, hover your cursor over the <mat-icon class="my-icon">help
          </mat-icon> icons in the <b>Create Stent</b> dialog.`}
        ]
      },
      {
        name: `Sinusotomy`,
        children: [
          {name: `In sinusotomy part of the outer wall of Schlemm\'s canal is ablated, and thus, it is modeled
          by removing the resistors representing the collector channels and Schlemm\'s canal.`},
          {name: `This results in part of Schlemm's canal being exposed to atmospheric pressure (0 mmHg), so when
          <b>P<sub>V</sub></b> > 0 mmHg, it is possible for <b>IOP</b> to drop below <b>P<sub>V</sub></b>, resulting in
          reverse (negative) flow through the collector channels.`},
          {name: `Sinusotomies can sometimes require long computation times, so the solver may timeout before a solution
          is obtained.`}
        ]
      },
    ]
  },
  {
    name: `Edit Constants`,
    children: [
      {name: `Many of the constant parameters used in the model can be changed in the <b>Edit Constants</b> dialog by
      clicking on the <b>Edit Constants</b> button in the lower right hand corner. For an explanation of a given
      parameter, hover your cursor over the corresponding <mat-icon class="my-icon">help</mat-icon> icon in the
      dialog.`}]
  },
  {
    name: `Model Convergence`,
    children: [
      {name: `As is discussed in the accompanying paper, this model is iterative, meaning that it solves the system many
      times until the solutions converge on a single value. A consequence of this is that under certain conditions, the
      model is unable to converge on a solution. Many of these conditions are either blocked or slightly adjusted by the
      website so that a solution is always reached, but some may not have been accounted for.`},
      {name: `Convergence can also be forced, if necessary by increasing the <b>Max Error</b> parameter in <b>Edit
      Constants</b>, however this is not recommended, as it may result in a less accurate solution.`}
    ]
  }
];

@Component({
  selector: 'app-instructions',
  templateUrl: './instructions.component.html',
  styleUrls: ['./instructions.component.scss'],
  animations: [trigger('showHide', [
    transition(':enter', [
      style({ paddingTop: '0px', paddingBottom: '0px', height: '0px', minHeight: '0', opacity: 0 }),
      animate('0.4s 0.1s ease-in-out', style({ paddingTop: '*', paddingBottom: '*', height: '*', opacity: 1 }))
    ]),
    transition(':leave', [
      style({ paddingTop: '*', paddingBottom: '*', height: '*', opacity: 1 }),
      animate('0.4s 0.1s ease-in-out', style({ paddingTop: '0px', paddingBottom: '0px', height: '0px', minHeight: '0', opacity: 0 }))
    ])
  ])]
})
export class InstructionsComponent implements OnInit {

  private _transformer = (node: InstructionNode, level: number) => {
    return {
      expandable: !!node.children && node.children.length > 0,
      name: node.name,
      level: level,
    };
  };

  treeControl = new FlatTreeControl<FlatNode>(
      node => node.level, node => node.expandable);

  treeFlattener = new MatTreeFlattener(
      this._transformer, node => node.level, node => node.expandable, node => node.children);

  dataSource = new MatTreeFlatDataSource(this.treeControl, this.treeFlattener);

  constructor() {
    this.dataSource.data = INSTRUCTIONS;
  }

  ngOnInit() {
  }

  hasChild = (_: number, node: FlatNode) => node.expandable;

}
