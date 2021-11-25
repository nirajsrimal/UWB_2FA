import {Component, Inject, OnInit} from '@angular/core';
import {MAT_DIALOG_DATA} from "@angular/material/dialog";

@Component({
  selector: 'app-draw-modal',
  templateUrl: './draw-modal.component.html',
  styleUrls: ['./draw-modal.component.css']
})
export class DrawModalComponent implements OnInit {

  xData: number[] = []
  yData: number[] = []

  graph: {data: any[], layout: any} | undefined = undefined;
  anyNavigator: any = undefined;

  constructor(@Inject(MAT_DIALOG_DATA) public data: any) {
    this.regenerateGraph();
  }

  ngOnInit(): void {
    this.lookupDevice();
    this.anyNavigator = navigator;

  }

  regenerateGraph() {
    this.graph = {
      data: [
        { x: this.xData, y: this.yData, type: 'scatter', mode: 'lines+points', marker: {color: 'red'} }
      ],
      layout: {width: 500, height: 500, title: 'Detected Motion'}
    };
  }

  lookupDevice() {
    const lookFor = this.data.deviceId;

  }

}
