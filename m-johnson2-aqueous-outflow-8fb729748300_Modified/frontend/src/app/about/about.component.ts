import { Component, OnInit } from '@angular/core';
import {animate, style, transition, trigger} from "@angular/animations";

@Component({
  selector: 'app-about-component',
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.scss'],
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
export class AboutComponent {

}
